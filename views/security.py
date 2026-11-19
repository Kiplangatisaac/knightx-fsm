"""
KnightX_fsm - Security View
Virus scanning with ClamAV integration.
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


class SecurityView(ctk.CTkFrame):
    """Security and virus scanning view."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="Security",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(30, 10))

        # ClamAV status
        self.status_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        self.status_frame.pack(fill="x", padx=30, pady=10)

        self.clamav_label = ctk.CTkLabel(
            self.status_frame, text="ClamAV: Checking...",
            text_color=COLOR_TEXT_MUTED,
        )
        self.clamav_label.pack(anchor="w", padx=20, pady=15)

        self._check_clamav()

        # Scan options
        scan_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        scan_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            scan_frame, text="Virus Scan",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        btn_frame = ctk.CTkFrame(scan_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_scan_file = ctk.CTkButton(
            btn_frame, text="📄 Scan File", width=120,
            command=self.scan_file,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_scan_file.pack(side="left", padx=5)

        self.btn_scan_folder = ctk.CTkButton(
            btn_frame, text="📁 Scan Folder", width=120,
            command=self.scan_folder,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_scan_folder.pack(side="left", padx=5)

        self.btn_update = ctk.CTkButton(
            btn_frame, text="🔄 Update Definitions", width=160,
            command=self.update_definitions,
            fg_color=COLOR_INFO, hover_color="#0891b2"
        )
        self.btn_update.pack(side="left", padx=5)

        # Results
        self.result_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        self.result_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.result_label = ctk.CTkLabel(
            self.result_frame, text="Scan results will appear here",
            text_color=COLOR_TEXT_MUTED,
        )
        self.result_label.pack(pady=30)

        self.progress = ctk.CTkProgressBar(self.result_frame, width=400)
        self.progress.pack(pady=10)
        self.progress.set(0)

    def _check_clamav(self):
        import shutil
        if shutil.which("clamscan"):
            self.clamav_label.configure(text="ClamAV: Installed ✓", text_color=COLOR_SUCCESS)
        else:
            self.clamav_label.configure(text="ClamAV: Not installed", text_color=COLOR_DANGER)

    def scan_file(self):
        file_path = ctk.filedialog.askopenfilename(title="Select file to scan")
        if not file_path:
            return

        def run():
            self.app.set_status(f"Scanning {file_path}...")
            result = scanner.scan_file_clamav(file_path)
            if result["infected"]:
                self.result_label.configure(
                    text=f"⚠️ THREAT DETECTED: {result['threat']}\nFile: {file_path}",
                    text_color=COLOR_DANGER,
                )
            else:
                self.result_label.configure(
                    text=f"✓ File is clean\nFile: {file_path}",
                    text_color=COLOR_SUCCESS,
                )
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def scan_folder(self):
        folder_path = ctk.filedialog.askdirectory(title="Select folder to scan")
        if not folder_path:
            return

        def run():
            self.app.set_status(f"Scanning {folder_path}...")
            result = scanner.scan_directory_clamav(folder_path)
            count = len(result["infected_files"])
            if count > 0:
                details = "\n".join(f"• {f['file']} - {f['threat']}" for f in result["infected_files"][:10])
                self.result_label.configure(
                    text=f"⚠️ {count} threat(s) found\n{details}",
                    text_color=COLOR_DANGER,
                )
            else:
                self.result_label.configure(
                    text=f"✓ No threats found\nScanned: {folder_path}",
                    text_color=COLOR_SUCCESS,
                )
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def update_definitions(self):
        def run():
            self.app.set_status("Updating ClamAV definitions...")
            result = scanner.update_clamav_definitions()
            if result["success"]:
                self.result_label.configure(
                    text="✓ Virus definitions updated successfully",
                    text_color=COLOR_SUCCESS,
                )
            else:
                self.result_label.configure(
                    text=f"✗ Update failed: {result['output'][:200]}",
                    text_color=COLOR_DANGER,
                )
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()