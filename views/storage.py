"""
KnightX_fsm - Storage View
Disk usage visualization and junk file management.
"""

import customtkinter as ctk
import psutil
import threading
from pathlib import Path

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_INFO, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_BACKGROUND, COLOR_ACCENT,
)
from database import db
from file_operations import scanner


class StorageView(ctk.CTkFrame):
    """Storage monitoring and junk cleaning view."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_ui()
        self.refresh_storage()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(
            self, text="Storage",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(30, 10))

        # Disk usage cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=30, pady=10)

        # Storage info section
        self.info_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        self.info_frame.pack(fill="x", padx=30, pady=10)
        self.info_frame.grid_columnconfigure(0, weight=1)

        self.storage_label = ctk.CTkLabel(
            self.info_frame, text="Loading disk information...",
            font=ctk.CTkFont(size=14), text_color=COLOR_TEXT_MUTED
        )
        self.storage_label.pack(pady=20)

        # Junk cleaning section
        junk_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        junk_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            junk_frame, text="Junk File Cleaner",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.junk_info = ctk.CTkLabel(
            junk_frame, text="Click 'Scan Junk' to find removable files",
            text_color=COLOR_TEXT_MUTED,
        )
        self.junk_info.pack(anchor="w", padx=20, pady=(0, 10))

        btn_frame = ctk.CTkFrame(junk_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_scan_junk = ctk.CTkButton(
            btn_frame, text="🔍 Scan Junk", width=120,
            command=self.scan_junk,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_scan_junk.pack(side="left", padx=5)

        self.btn_clean_junk = ctk.CTkButton(
            btn_frame, text="🗑️ Clean Junk", width=120,
            command=self.clean_junk,
            fg_color=COLOR_DANGER, hover_color="#b91c1c",
            state="disabled"
        )
        self.btn_clean_junk.pack(side="left", padx=5)

        self.junk_result = ctk.CTkLabel(
            junk_frame, text="", text_color=COLOR_SUCCESS,
        )
        self.junk_result.pack(anchor="w", padx=20, pady=(0, 10))

    def refresh_storage(self):
        def run():
            partitions = psutil.disk_partitions(all=False)
            cards = []
            for part in partitions:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    cards.append((part.device, part.mountpoint, part.fstype, usage))
                except Exception:
                    continue

            self._create_cards(cards)

            total = sum(c[3].total for c in cards)
            used = sum(c[3].used for c in cards)
            free = sum(c[3].free for c in cards)
            percent = (used / total * 100) if total > 0 else 0

            self.storage_label.configure(
                text=f"Total: {self._format_size(total)}  |  Used: {self._format_size(used)} ({percent:.1f}%)  |  Free: {self._format_size(free)}"
            )
        threading.Thread(target=run, daemon=True).start()

    def _create_cards(self, cards):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        for i, (device, mountpoint, fstype, usage) in enumerate(cards):
            card = ctk.CTkFrame(self.cards_frame, fg_color=COLOR_SURFACE, width=240, height=140)
            card.grid(row=0, column=i, padx=10, pady=10)
            card.grid_propagate(False)

            pct = (usage.used / usage.total * 100) if usage.total > 0 else 0

            ctk.CTkLabel(
                card, text=device, font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLOR_TEXT,
            ).pack(pady=(15, 5))

            ctk.CTkLabel(
                card, text=mountpoint, font=ctk.CTkFont(size=13),
                text_color=COLOR_TEXT_MUTED,
            ).pack()

            ctk.CTkLabel(
                card, text=f"Used: {self._format_size(usage.used)} / {self._format_size(usage.total)}",
                font=ctk.CTkFont(size=13),
                text_color=COLOR_TEXT,
            ).pack(pady=(10, 5))

            ctk.CTkLabel(
                card, text=f"{pct:.1f}%", font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLOR_SUCCESS if pct < 80 else COLOR_WARNING if pct < 95 else COLOR_DANGER,
            ).pack(pady=(5, 15))

    def _format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def scan_junk(self):
        def run():
            self.btn_scan_junk.configure(state="disabled")
            self.app.set_status("Scanning for junk files...")
            result = scanner.find_junk(str(Path.home()))
            self.junk_files = result["junk_files"]
            self.junk_count = result["count"]
            self.junk_size = result["total_size"]

            self.junk_info.configure(
                text=f"Found {self.junk_count} junk files ({self._format_size(self.junk_size)})"
            )
            self.btn_clean_junk.configure(state="normal" if self.junk_count > 0 else "disabled")
            self.btn_scan_junk.configure(state="normal")
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def clean_junk(self):
        if not hasattr(self, "junk_files") or not self.junk_files:
            return
        if not self.junk_files:
            return

        confirm = ctk.CTkInputDialog(
            text=f"Type 'DELETE' to confirm removing {self.junk_count} junk files ({self._format_size(self.junk_size)}):",
            title="Confirm Junk Clean"
        ).get_input()

        if confirm != "DELETE":
            return

        def run():
            self.btn_clean_junk.configure(state="disabled")
            self.app.set_status("Cleaning junk files...")
            result = scanner.clean_junk(self.junk_files)
            self.junk_result.configure(
                text=f"Deleted {result['deleted']} files, freed {result['space_freed_mb']} MB"
            )
            self.btn_clean_junk.configure(state="disabled")
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()