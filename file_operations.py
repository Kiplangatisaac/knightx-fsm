"""
KnightX_fsm - File Operations Module
File scanning, duplicate detection, junk cleaning, virus scanning, and USB management.
"""

import os
import hashlib
import logging
import shutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional

import psutil

from config import (
    CHUNK_SIZE, JUNK_EXTENSIONS, JUNK_PATTERNS, COMMON_JUNK_DIRS,
    CLAMSCAN_PATH, FRESHCLAM_PATH
)
from database import db
from encryption import encryption

logger = logging.getLogger(__name__)


class FileScanner:
    """Handles file system scanning operations."""

    def __init__(self):
        self._cancel = False
        self._progress_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable):
        """Set a callback for progress updates: (current, total, message)."""
        self._progress_callback = callback

    def cancel(self):
        """Cancel the current operation."""
        self._cancel = True

    def reset(self):
        """Reset cancel flag."""
        self._cancel = False

    # --- Hashing ---

    @staticmethod
    def sha256_file(file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error hashing {file_path}: {e}")
            return ""

    @staticmethod
    def get_file_type(file_path: Path) -> str:
        """Get file extension/type."""
        return file_path.suffix.lower() if file_path.suffix else "unknown"

    # --- Directory Scan ---

    def scan_directory(self, directory: str, recursive: bool = True,
                       deep_scan: bool = False) -> dict:
        """
        Scan a directory and collect file metadata.
        Returns a dict with scan results.
        """
        self.reset()
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return {"error": "Directory not found", "files": []}

        files = []
        total_size = 0
        seen_hashes = {}  # hash -> first file path

        try:
            entries = dir_path.rglob("*") if recursive else dir_path.iterdir()
            for entry in entries:
                if self._cancel:
                    break
                if not entry.is_file():
                    continue
                try:
                    stat = entry.stat()
                    size = stat.st_size
                    total_size += size
                    file_type = self.get_file_type(entry)
                    mime_type = self._guess_mime(entry)

                    file_data = {
                        "path": str(entry.parent),
                        "name": entry.name,
                        "size": size,
                        "file_type": file_type,
                        "mime_type": mime_type,
                        "sha256": "",
                        "is_duplicate": 0,
                        "is_junk": self._is_junk(entry),
                        "risk_score": 0.0,
                    }

                    if deep_scan:
                        file_data["sha256"] = self.sha256_file(entry)
                        # Duplicate detection
                        if file_data["sha256"]:
                            if file_data["sha256"] in seen_hashes:
                                file_data["is_duplicate"] = 1
                            else:
                                seen_hashes[file_data["sha256"]] = str(entry)

                    files.append(file_data)

                    if self._progress_callback:
                        self._progress_callback(len(files), 0, f"Scanning: {entry.name}")
                except (PermissionError, OSError) as e:
                    logger.warning(f"Cannot access {entry}: {e}")
                    continue

            # Store metadata in DB
            db.clear_file_metadata()
            for f in files:
                db.insert_file_metadata(f)

            duplicates = sum(1 for f in files if f["is_duplicate"])
            junk = sum(1 for f in files if f["is_junk"])

            # Log scan
            db.insert_scan_history({
                "scan_type": "directory",
                "target_path": directory,
                "files_scanned": len(files),
                "threats_found": 0,
                "duplicates_found": duplicates,
                "junk_found": junk,
                "space_recovered": 0,
                "status": "completed",
            })

            return {
                "files": files,
                "total_files": len(files),
                "total_size": total_size,
                "duplicates": duplicates,
                "junk": junk,
            }
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return {"error": str(e), "files": []}

    def _guess_mime(self, file_path: Path) -> str:
        """Guess MIME type from extension."""
        import mimetypes
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime or "application/octet-stream"

    def _is_junk(self, file_path: Path) -> bool:
        """Check if a file is likely junk."""
        name = file_path.name.lower()
        # Check extensions
        if file_path.suffix.lower() in JUNK_EXTENSIONS:
            return True
        # Check patterns
        import fnmatch
        for pattern in JUNK_PATTERNS:
            if fnmatch.fnmatch(name, pattern.lower()):
                return True
        # Check directory names
        for part in file_path.parts:
            if part.lower() in COMMON_JUNK_DIRS:
                return True
        return False

    # --- Duplicate Finder ---

    def find_duplicates(self, directory: str = None) -> dict:
        """Find duplicate files across the system or in a directory."""
        self.reset()
        if directory:
            result = self.scan_directory(directory, deep_scan=True)
        else:
            # Scan home directory
            home = str(Path.home())
            result = self.scan_directory(home, deep_scan=True)

        # Group by hash
        from database import db
        duplicates = db.get_duplicates()
        groups = {}
        for d in duplicates:
            h = d.get("sha256", "")
            if h:
                groups.setdefault(h, []).append(d)

        duplicate_groups = [g for g in groups.values() if len(g) > 1]
        total_wasted = sum(
            sum(f["size"] for f in group[1:]) for group in duplicate_groups
        )

        return {
            "groups": duplicate_groups,
            "group_count": len(duplicate_groups),
            "total_wasted_bytes": total_wasted,
        }

    # --- Junk Cleaner ---

    def find_junk(self, directory: str = None) -> dict:
        """Find junk files."""
        target = directory or str(Path.home())
        result = self.scan_directory(target, deep_scan=False)
        junk_files = [f for f in result["files"] if f["is_junk"]]
        total_size = sum(f["size"] for f in junk_files)
        return {
            "junk_files": junk_files,
            "count": len(junk_files),
            "total_size": total_size,
        }

    def clean_junk(self, junk_files: list) -> dict:
        """Delete junk files and return recovery stats."""
        freed = 0
        deleted = 0
        errors = 0
        for f in junk_files:
            try:
                path = Path(f["path"]) / f["name"]
                if path.exists():
                    size = path.stat().st_size
                    path.unlink()
                    freed += size
                    deleted += 1
                    db.mark_junk(f["id"], is_junk=False)
            except Exception as e:
                logger.error(f"Error deleting {f}: {e}")
                errors += 1

        db.insert_scan_history({
            "scan_type": "junk_clean",
            "target_path": "multiple",
            "files_scanned": deleted,
            "threats_found": 0,
            "duplicates_found": 0,
            "junk_found": deleted,
            "space_recovered": freed,
            "status": "completed",
        })

        return {
            "deleted": deleted,
            "errors": errors,
            "space_freed_bytes": freed,
            "space_freed_mb": round(freed / (1024 * 1024), 2),
        }

    # --- Virus Scanning (ClamAV) ---

    def scan_file_clamav(self, file_path: str) -> dict:
        """Scan a single file with ClamAV."""
        try:
            result = subprocess.run(
                [CLAMSCAN_PATH, "--no-summary", file_path],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout.strip()
            infected = "FOUND" in output
            threat = ""
            if infected:
                # Extract threat name
                parts = output.split(":", 1)
                if len(parts) > 1:
                    threat = parts[1].strip()
            return {
                "infected": infected,
                "threat": threat,
                "output": output,
                "scan_engine": "clamav",
            }
        except subprocess.TimeoutExpired:
            return {"infected": False, "threat": "timeout", "output": "", "scan_engine": "clamav"}
        except FileNotFoundError:
            return {"infected": False, "threat": "clamav_not_installed", "output": "", "scan_engine": "clamav"}
        except Exception as e:
            return {"infected": False, "threat": str(e), "output": "", "scan_engine": "clamav"}

    def scan_directory_clamav(self, directory: str,
                              callback: Callable = None) -> dict:
        """Scan a directory recursively with ClamAV."""
        infected_files = []
        total_scanned = 0
        dir_path = Path(directory)

        try:
            result = subprocess.run(
                [CLAMSCAN_PATH, "-r", "--no-summary", str(dir_path)],
                capture_output=True, text=True, timeout=300
            )
            output = result.stdout
            for line in output.splitlines():
                if "FOUND" in line:
                    parts = line.split(":", 1)
                    file_path = parts[0].strip() if parts else line
                    threat = parts[1].strip() if len(parts) > 1 else "Unknown"
                    infected_files.append({"file": file_path, "threat": threat})
                    total_scanned += 1
                    if callback:
                        callback(file_path, threat)

            return {
                "infected": len(infected_files) > 0,
                "infected_files": infected_files,
                "total_scanned": total_scanned,
                "output": output,
            }
        except subprocess.TimeoutExpired:
            return {"infected": False, "infected_files": [], "total_scanned": total_scanned, "output": "timeout"}
        except FileNotFoundError:
            return {"infected": False, "infected_files": [], "total_scanned": 0, "output": "clamav_not_installed"}
        except Exception as e:
            return {"infected": False, "infected_files": [], "total_scanned": 0, "output": str(e)}

    def update_clamav_definitions(self) -> dict:
        """Update ClamAV virus definitions."""
        try:
            result = subprocess.run(
                [FRESHCLAM_PATH], capture_output=True, text=True, timeout=120
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr,
            }
        except FileNotFoundError:
            return {"success": False, "output": "freshclam not installed"}
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "update timed out"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    # --- USB Detection ---

    def detect_usb_devices(self) -> list:
        """Detect connected USB storage devices."""
        devices = []
        try:
            partitions = psutil.disk_partitions(all=False)
            for part in partitions:
                if "removable" in part.opts or part.device.startswith(("/dev/sd", "/dev/nvme")):
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        devices.append({
                            "device_name": part.device,
                            "device_path": part.mountpoint,
                            "serial_number": part.device,
                            "vendor_id": "unknown",
                            "product_id": "unknown",
                            "size": usage.total,
                            "mountpoint": part.mountpoint,
                            "fstype": part.fstype,
                        })
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"USB detection error: {e}")
        return devices

    def scan_usb_device(self, mountpoint: str) -> dict:
        """Scan a USB device for viruses and junk."""
        result = self.scan_directory_clamav(mountpoint)
        junk_result = self.find_junk(mountpoint)
        return {
            "virus": result,
            "junk": junk_result,
        }


# Global instance
scanner = FileScanner()