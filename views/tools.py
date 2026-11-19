"""
KnightX_fsm - Tools View
Duplicate finder, USB scanning, activity log, and system tools.
"""

import customtkinter as ctk
import threading
from pathlib import Path

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_INFO, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_BACKGROUND,
)
from database import db
from file_operations import scanner


class ToolsView(ctk.CTkFrame):
    """Tools and utilities view."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="Tools",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(30, 10))

        # Duplicate finder
        dup_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        dup_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            dup_frame, text="Duplicate File Finder",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            dup_frame, text="Find and remove duplicate files using SHA-256 hashing",
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        btn_frame = ctk.CTkFrame(dup_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_find_dups = ctk.CTkButton(
            btn_frame, text="🔍 Find Duplicates", width=140,
            command=self.find_duplicates,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_find_dups.pack(side="left", padx=5)

        self.dup_result = ctk.CTkLabel(dup_frame, text="", text_color=COLOR_TEXT_MUTED)
        self.dup_result.pack(anchor="w", padx=20, pady=(0, 10))

        # USB scanner
        usb_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        usb_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            usb_frame, text="USB Device Scanner",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            usb_frame, text="Detect and scan connected USB storage devices",
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        usb_btn_frame = ctk.CTkFrame(usb_frame, fg_color="transparent")
        usb_btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_detect_usb = ctk.CTkButton(
            usb_btn_frame, text="🔌 Detect USB", width=130,
            command=self.detect_usb,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_detect_usb.pack(side="left", padx=5)

        self.usb_result = ctk.CTkLabel(usb_frame, text="", text_color=COLOR_TEXT_MUTED)
        self.usb_result.pack(anchor="w", padx=20, pady=(0, 10))

        # Activity log
        log_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        log_frame.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(
            log_frame, text="Activity Log",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.log_text = ctk.CTkTextbox(log_frame, height=200, fg_color=COLOR_BACKGROUND)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.refresh_log()

    def find_duplicates(self):
        def run():
            self.btn_find_dups.configure(state="disabled")
            self.app.set_status("Finding duplicates...")
            result = scanner.find_duplicates(str(Path.home()))
            groups = result["group_count"]
            wasted = result["total_wasted_bytes"]
            self.dup_result.configure(
                text=f"Found {groups} duplicate groups ({self._format_size(wasted)} potentially recoverable)",
                text_color=COLOR_WARNING if groups > 0 else COLOR_SUCCESS,
            )
            self.btn_find_dups.configure(state="normal")
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def detect_usb(self):
        def run():
            self.app.set_status("Detecting USB devices...")
            devices = scanner.detect_usb_devices()
            for d in devices:
                db.insert_usb_device(d)
            count = len(devices)
            if count > 0:
                details = "\n".join(f"• {d['device_name']} at {d['mountpoint']}" for d in devices)
                self.usb_result.configure(text=f"Found {count} USB device(s)\n{details}", text_color=COLOR_SUCCESS)
            else:
                self.usb_result.configure(text="No USB devices detected", text_color=COLOR_TEXT_MUTED)
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def refresh_log(self):
        try:
            logs = db.get_activity_log(limit=50)
            lines = []
            for log in reversed(logs):
                user = log.get("username", "system")
                action = log.get("action", "")
                ts = log.get("timestamp", "")
                lines.append(f"[{ts}] {user}: {action}")
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", "\n".join(lines))
        except Exception as e:
            self.log_text.delete("0.0", "end")
            self.log_text.insert("0.0", f"Error loading log: {e}")

    @staticmethod
    def _format_size(size_bytes):
        if size_bytes == 0:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"