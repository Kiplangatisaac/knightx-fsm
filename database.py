"""
KnightX_fsm - Database Module
SQLite database management with encryption support for sensitive fields.
"""

import sqlite3
import json
import logging
from pathlib import Path
from contextlib import contextmanager

from config import DB_PATH, TABLES
from encryption import encryption

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        return conn

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_schema(self):
        """Create all tables if they don't exist."""
        with self.get_connection() as conn:
            for table_name, create_sql in TABLES.items():
                try:
                    conn.execute(create_sql)
                    logger.info(f"Table '{table_name}' initialized.")
                except Exception as e:
                    logger.error(f"Failed to initialize table '{table_name}': {e}")
            self._seed_default_user(conn)

    def _seed_default_user(self, conn):
        """Seed the default admin user if no users exist."""
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            if count == 0:
                from config import DEFAULT_ADMIN
                password_hash = encryption.hash_password(DEFAULT_ADMIN["password"])
                conn.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                    (DEFAULT_ADMIN["username"], password_hash, DEFAULT_ADMIN["email"], DEFAULT_ADMIN["role"])
                )
                logger.info("Default admin user seeded.")
        except Exception as e:
            logger.error(f"Failed to seed default user: {e}")

    # --- User Operations ---

    def create_user(self, username: str, password: str, email: str = None, role: str = "user") -> bool:
        """Create a new user."""
        try:
            password_hash = encryption.hash_password(password)
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
                    (username, password_hash, email, role)
                )
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False

    def authenticate_user(self, username: str, password: str) -> dict | None:
        """Authenticate a user and return user dict if successful."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, password_hash, email, role, is_active FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row and encryption.verify_password(password, row["password_hash"]):
                    if not row["is_active"]:
                        return None
                    conn.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (row["id"],)
                    )
                    return {
                        "id": row["id"],
                        "username": row["username"],
                        "email": row["email"],
                        "role": row["role"],
                    }
                return None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> dict | None:
        """Get user by ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, username, email, role, is_active, created_at, last_login FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    # --- File Metadata Operations ---

    def insert_file_metadata(self, file_data: dict) -> int:
        """Insert file metadata and return the row ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO file_metadata
                   (path, name, size, file_type, mime_type, sha256, is_duplicate, is_junk, risk_score, last_scanned)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (
                    file_data.get("path"),
                    file_data.get("name"),
                    file_data.get("size", 0),
                    file_data.get("file_type"),
                    file_data.get("mime_type"),
                    file_data.get("sha256"),
                    file_data.get("is_duplicate", 0),
                    file_data.get("is_junk", 0),
                    file_data.get("risk_score", 0.0),
                )
            )
            return cursor.lastrowid

    def get_files_by_path(self, path: str) -> list:
        """Get file metadata for a directory path."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM file_metadata WHERE path = ? ORDER BY name",
                    (path,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting files by path: {e}")
            return []

    def mark_duplicate(self, file_id: int, is_duplicate: bool = True):
        """Mark a file as duplicate or not."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE file_metadata SET is_duplicate = ? WHERE id = ?",
                    (1 if is_duplicate else 0, file_id)
                )
        except Exception as e:
            logger.error(f"Error marking duplicate: {e}")

    def mark_junk(self, file_id: int, is_junk: bool = True):
        """Mark a file as junk or not."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE file_metadata SET is_junk = ? WHERE id = ?",
                    (1 if is_junk else 0, file_id)
                )
        except Exception as e:
            logger.error(f"Error marking junk: {e}")

    def get_junk_files(self) -> list:
        """Get all files marked as junk."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM file_metadata WHERE is_junk = 1 ORDER BY path, name"
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting junk files: {e}")
            return []

    def get_duplicates(self) -> list:
        """Get all files marked as duplicates."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM file_metadata WHERE is_duplicate = 1 ORDER BY sha256, name"
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting duplicates: {e}")
            return []

    def clear_file_metadata(self):
        """Clear all file metadata."""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM file_metadata")
        except Exception as e:
            logger.error(f"Error clearing file metadata: {e}")

    # --- Scan History Operations ---

    def insert_scan_history(self, scan_data: dict) -> int:
        """Insert a scan history record."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO scan_history
                   (scan_type, target_path, files_scanned, threats_found, duplicates_found,
                    junk_found, space_recovered, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    scan_data.get("scan_type"),
                    scan_data.get("target_path"),
                    scan_data.get("files_scanned", 0),
                    scan_data.get("threats_found", 0),
                    scan_data.get("duplicates_found", 0),
                    scan_data.get("junk_found", 0),
                    scan_data.get("space_recovered", 0),
                    scan_data.get("status", "completed"),
                )
            )
            return cursor.lastrowid

    def get_scan_history(self, limit: int = 50) -> list:
        """Get recent scan history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM scan_history ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting scan history: {e}")
            return []

    # --- USB Device Operations ---

    def insert_usb_device(self, device_data: dict) -> int:
        """Insert or update a USB device record."""
        with self.get_connection() as conn:
            # Check if device exists
            cursor = conn.execute(
                "SELECT id FROM usb_devices WHERE serial_number = ? OR device_path = ?",
                (device_data.get("serial_number"), device_data.get("device_path"))
            )
            existing = cursor.fetchone()
            if existing:
                conn.execute(
                    """UPDATE usb_devices SET last_seen = datetime('now'), scan_status = ?,
                       threats_found = ? WHERE id = ?""",
                    (
                        device_data.get("scan_status", "pending"),
                        device_data.get("threats_found", 0),
                        existing["id"],
                    )
                )
                return existing["id"]
            else:
                cursor = conn.execute(
                    """INSERT INTO usb_devices
                       (device_name, device_path, serial_number, vendor_id, product_id, size,
                        scan_status, threats_found)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        device_data.get("device_name"),
                        device_data.get("device_path"),
                        device_data.get("serial_number"),
                        device_data.get("vendor_id"),
                        device_data.get("product_id"),
                        device_data.get("size", 0),
                        device_data.get("scan_status", "pending"),
                        device_data.get("threats_found", 0),
                    )
                )
                return cursor.lastrowid

    def get_usb_devices(self) -> list:
        """Get all USB devices."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM usb_devices ORDER BY last_seen DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting USB devices: {e}")
            return []

    # --- Activity Log Operations ---

    def log_activity(self, user_id: int, action: str, details: str = None, ip_address: str = None):
        """Log an activity."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO activity_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
                    (user_id, action, details, ip_address)
                )
        except Exception as e:
            logger.error(f"Error logging activity: {e}")

    def get_activity_log(self, limit: int = 100) -> list:
        """Get recent activity log."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT al.*, u.username FROM activity_log al
                       LEFT JOIN users u ON al.user_id = u.id
                       ORDER BY al.timestamp DESC LIMIT ?""",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting activity log: {e}")
            return []

    # --- System Metrics ---

    def insert_system_metrics(self, metrics: dict):
        """Insert system metrics snapshot."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO system_metrics
                       (cpu_percent, memory_percent, disk_percent, network_sent, network_recv)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        metrics.get("cpu_percent", 0),
                        metrics.get("memory_percent", 0),
                        metrics.get("disk_percent", 0),
                        metrics.get("network_sent", 0),
                        metrics.get("network_recv", 0),
                    )
                )
        except Exception as e:
            logger.error(f"Error inserting system metrics: {e}")

    def get_recent_metrics(self, limit: int = 60) -> list:
        """Get recent system metrics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return []


# Global instance
db = DatabaseManager()