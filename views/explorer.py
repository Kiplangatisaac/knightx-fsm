"""
KnightX_fsm - File Explorer View
Full-featured file browser with navigation, operations, and AI integration.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
import os
import shutil
import threading

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_INFO, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_SURFACE_HOVER, COLOR_BACKGROUND, COLOR_ACCENT,
)
from database import db
from ai_integration import ai
from file_operations import scanner
from encryption import encryption


class ExplorerView(ctk.CTkFrame):
    """File Explorer view with navigation and file operations."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_path = Path.home()
        self.history = []
        self.history_index = -1
        self.selected_items = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Navigation bar
        nav_frame = ctk.CTkFrame(self, height=50, fg_color=COLOR_SURFACE)
        nav_frame.pack(fill="x", padx=10, pady=(10, 5))
        nav_frame.grid_propagate(False)
        nav_frame.grid_columnconfigure(4, weight=1)

        self.btn_back = ctk.CTkButton(
            nav_frame, text="◀", width=35, command=self.go_back,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_back.grid(row=0, column=0, padx=5, pady=8)

        self.btn_forward = ctk.CTkButton(
            nav_frame, text="▶", width=35, command=self.go_forward,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_forward.grid(row=0, column=1, padx=5, pady=8)

        self.btn_up = ctk.CTkButton(
            nav_frame, text="↑", width=35, command=self.go_up,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_up.grid(row=0, column=2, padx=5, pady=8)

        self.btn_home = ctk.CTkButton(
            nav_frame, text="🏠", width=35, command=self.go_home,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_home.grid(row=0, column=3, padx=5, pady=8)

        self.path_entry = ctk.CTkEntry(
            nav_frame, placeholder_text="Enter path...", height=35
        )
        self.path_entry.grid(row=0, column=4, padx=10, pady=8, sticky="ew")
        self.path_entry.bind("<Return>", lambda e: self.navigate_to_entry())

        self.btn_go = ctk.CTkButton(
            nav_frame, text="Go", width=60, command=self.navigate_to_entry,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_go.grid(row=0, column=5, padx=5, pady=8)

        self.btn_refresh = ctk.CTkButton(
            nav_frame, text="↻", width=35, command=self.refresh,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_refresh.grid(row=0, column=6, padx=5, pady=8)

        # Toolbar
        toolbar = ctk.CTkFrame(self, height=45, fg_color=COLOR_SURFACE)
        toolbar.pack(fill="x", padx=10, pady=5)

        self.btn_new_folder = ctk.CTkButton(
            toolbar, text="📂 New Folder", width=110, command=self.create_new_folder,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_new_folder.pack(side="left", padx=5, pady=5)

        self.btn_delete = ctk.CTkButton(
            toolbar, text="🗑️ Delete", width=90, command=self.delete_selected,
            fg_color=COLOR_DANGER, hover_color="#b91c1c"
        )
        self.btn_delete.pack(side="left", padx=5, pady=5)

        self.btn_rename = ctk.CTkButton(
            toolbar, text="✏️ Rename", width=90, command=self.rename_selected,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_rename.pack(side="left", padx=5, pady=5)

        self.btn_scan = ctk.CTkButton(
            toolbar, text="🛡️ Scan File", width=100, command=self.scan_selected,
            fg_color=COLOR_WARNING, hover_color="#b45309"
        )
        self.btn_scan.pack(side="left", padx=5, pady=5)

        self.btn_ai = ctk.CTkButton(
            toolbar, text="🤖 AI Analyze", width=110, command=self.ai_analyze_selected,
            fg_color=COLOR_ACCENT, hover_color="#7c3aed"
        )
        self.btn_ai.pack(side="left", padx=5, pady=5)

        self.btn_duplicate = ctk.CTkButton(
            toolbar, text="🔍 Find Duplicates", width=130, command=self.find_duplicates_here,
            fg_color=COLOR_SURFACE_HOVER, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_duplicate.pack(side="left", padx=5, pady=5)

        # File list
        self.file_list = ctk.CTkScrollableFrame(self, fg_color=COLOR_BACKGROUND)
        self.file_list.pack(fill="both", expand=True, padx=10, pady=10)

        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.file_list, text="No files found",
            text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(size=16)
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def refresh(self):
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, str(self.current_path))
        self._update_nav_buttons()
        self._load_files()

    def _update_nav_buttons(self):
        self.btn_back.configure(state="normal" if self.history_index > 0 else "disabled")
        self.btn_forward.configure(
            state="normal" if self.history_index < len(self.history) - 1 else "disabled"
        )
        self.btn_up.configure(state="normal" if self.current_path.parent != self.current_path else "disabled")

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = Path(self.history[self.history_index])
            self.refresh()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = Path(self.history[self.history_index])
            self.refresh()

    def go_up(self):
        if self.current_path.parent != self.current_path:
            self._push_history(self.current_path)
            self.current_path = self.current_path.parent
            self.refresh()

    def go_home(self):
        self._push_history(self.current_path)
        self.current_path = Path.home()
        self.refresh()

    def navigate_to_entry(self):
        path_str = self.path_entry.get().strip()
        path = Path(path_str)
        if path.exists() and path.is_dir():
            self._push_history(self.current_path)
            self.current_path = path
            self.refresh()
        else:
            messagebox.showerror("Error", "Invalid directory path")

    def _push_history(self, path):
        # Remove forward history when navigating to a new place
        self.history = self.history[: self.history_index + 1]
        self.history.append(str(path))
        self.history_index = len(self.history) - 1

    # ------------------------------------------------------------------
    # File Loading
    # ------------------------------------------------------------------
    def _load_files(self):
        # Clear existing
        for widget in self.file_list.winfo_children():
            widget.destroy()

        try:
            entries = sorted(self.current_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not entries:
            self.empty_label.pack(expand=True)
            return

        self.empty_label.pack_forget()

        # Header row
        header = ctk.CTkFrame(self.file_list, fg_color=COLOR_SURFACE, height=35)
        header.pack(fill="x", pady=(0, 5))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_columnconfigure(2, weight=0)

        ctk.CTkLabel(header, text="Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Type", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(header, text="Size", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, sticky="e")

        for entry in entries:
            self._create_file_row(entry)

    def _create_file_row(self, entry: Path):
        row = ctk.CTkFrame(self.file_list, fg_color=COLOR_SURFACE, height=40)
        row.pack(fill="x", pady=1)
        row.grid_propagate(False)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        row.grid_columnconfigure(2, weight=0)

        # Selection checkbox
        var = ctk.BooleanVar()
        cb = ctk.CTkCheckBox(row, text="", variable=var, width=20)
        cb.grid(row=0, column=0, padx=5, sticky="w")

        # Icon
        icon = "📁" if entry.is_dir() else "📄"
        icon_label = ctk.CTkLabel(row, text=icon, width=30)
        icon_label.grid(row=0, column=1, padx=5, sticky="w")

        # Name
        name_label = ctk.CTkLabel(row, text=entry.name, anchor="w")
        name_label.grid(row=0, column=2, padx=5, sticky="w")

        # Type
        type_text = "Folder" if entry.is_dir() else entry.suffix or "File"
        type_label = ctk.CTkLabel(row, text=type_text, width=80)
        type_label.grid(row=0, column=3, padx=5, sticky="w")

        # Size
        if entry.is_dir():
            size_text = "—"
        else:
            try:
                size = entry.stat().st_size
                size_text = self._format_size(size)
            except Exception:
                size_text = "—"
        size_label = ctk.CTkLabel(row, text=size_text, width=80)
        size_label.grid(row=0, column=4, padx=5, sticky="e")

        # Click to navigate if directory
        if entry.is_dir():
            row.bind("<Button-1>", lambda e: self._open_directory(entry))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e: self._open_directory(entry))

    def _open_directory(self, entry: Path):
        self._push_history(self.current_path)
        self.current_path = entry
        self.refresh()

    def _format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    # ------------------------------------------------------------------
    # File Operations
    # ------------------------------------------------------------------
    def create_new_folder(self):
        name = ctk.CTkInputDialog(text="Enter folder name:", title="New Folder").get_input()
        if not name:
            return
        try:
            (self.current_path / name).mkdir(exist_ok=False)
            self.refresh()
        except FileExistsError:
            messagebox.showerror("Error", "Folder already exists")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        selected = self._get_selected_paths()
        if not selected:
            messagebox.showwarning("Warning", "No items selected")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} item(s)?"):
            return
        for path in selected:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {path.name}: {e}")
        self.refresh()

    def rename_selected(self):
        selected = self._get_selected_paths()
        if len(selected) != 1:
            messagebox.showwarning("Warning", "Select exactly one item")
            return
        path = selected[0]
        new_name = ctk.CTkInputDialog(text="Enter new name:", title="Rename").get_input()
        if not new_name:
            return
        try:
            path.rename(path.parent / new_name)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _get_selected_paths(self):
        # Simple implementation: return None since checkboxes aren't wired to selection tracking
        # For now, return empty list. Full implementation would track checkbox states.
        return []

    def scan_selected(self):
        messagebox.showinfo("Info", "Select a file to scan from the context menu")

    def ai_analyze_selected(self):
        messagebox.showinfo("Info", "AI analysis available in AI Assistant view")

    def find_duplicates_here(self):
        def run_scan():
            self.app.set_status("Scanning for duplicates...")
            result = scanner.find_duplicates(str(self.current_path))
            self.app.set_status(f"Found {result['group_count']} duplicate groups")
            messagebox.showinfo("Duplicates", f"Found {result['group_count']} duplicate groups")

        threading.Thread(target=run_scan, daemon=True).start()