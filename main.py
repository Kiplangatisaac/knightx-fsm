"""
KnightX_fsm - Main Application
Futuristic File System Manager with modern UI.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import logging

from config import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION,
    THEME_MODE, COLOR_PRIMARY, COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_INFO,
    COLOR_BACKGROUND, COLOR_SURFACE, COLOR_SURFACE_HOVER,
    COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_ACCENT,
    COLOR_GRADIENT_START, COLOR_GRADIENT_END,
)
from database import db
from encryption import encryption
from ai_integration import ai
from file_operations import scanner
from views.explorer import ExplorerView
from views.storage import StorageView
from views.security import SecurityView
from views.tools import ToolsView
from views.ai_view import AIView
from views.settings import SettingsView

logger = logging.getLogger(__name__)


class KnightXApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        ctk.set_appearance_mode(THEME_MODE)
        ctk.set_default_color_theme("blue")

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State
        self.current_user = None
        self.current_path = str(Path.home())
        self.navigation_history = []
        self.nav_index = -1

        # Build UI
        self._build_sidebar()
        self._build_main_area()
        self._build_status_bar()

        # Show login first
        self.show_login()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=COLOR_SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # App header
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="KnightX_fsm",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY,
        )
        self.logo_label.pack(pady=(30, 10))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar,
            text="Futuristic File Manager",
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXT_MUTED,
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard", "🏠"),
            ("explorer", "File Explorer", "📁"),
            ("storage", "Storage", "💾"),
            ("security", "Security", "🛡️"),
            ("tools", "Tools", "🔧"),
            ("ai", "AI Assistant", "🤖"),
            ("settings", "Settings", "⚙️"),
        ]

        for key, label, icon in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}  {label}",
                anchor="w",
                height=40,
                fg_color="transparent",
                text_color=COLOR_TEXT,
                hover_color=COLOR_SURFACE_HOVER,
                command=lambda k=key: self.switch_view(k),
            )
            btn.pack(fill="x", padx=20, pady=4)
            self.nav_buttons[key] = btn

        # User section at bottom
        self.user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.user_frame.pack(side="bottom", fill="x", padx=20, pady=30)

        self.user_label = ctk.CTkLabel(
            self.user_frame,
            text="Not logged in",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        )
        self.user_label.pack()

        self.login_btn = ctk.CTkButton(
            self.user_frame,
            text="Login",
            height=32,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.show_login,
        )
        self.login_btn.pack(pady=(10, 0), fill="x")

    def _build_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND)
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # Container for all views
        self.views_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.views_container.grid(row=0, column=0, sticky="nsew")
        self.views_container.grid_columnconfigure(0, weight=1)
        self.views_container.grid_rowconfigure(0, weight=1)

        # Build all views (hidden by default)
        self._build_dashboard_view()
        self._build_explorer_view()
        self._build_storage_view()
        self._build_security_view()
        self._build_tools_view()
        self._build_ai_view()
        self._build_settings_view()

        # Show dashboard by default
        self.current_view = None
        self.switch_view("dashboard")

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=30, fg_color=COLOR_SURFACE)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_propagate(False)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.pack(side="left", padx=15)

        self.ai_status_label = ctk.CTkLabel(
            self.status_bar,
            text="AI: Offline",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT_MUTED,
        )
        self.ai_status_label.pack(side="right", padx=15)

    # ------------------------------------------------------------------
    # View Switching
    # ------------------------------------------------------------------
    def switch_view(self, key):
        """Switch to a different view."""
        # Hide all views
        for attr in dir(self):
            if attr.endswith("_view"):
                getattr(self, attr).grid_forget()

        # Update sidebar button states
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=COLOR_PRIMARY, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT)

        # Show selected view
        view = getattr(self, f"{key}_view", None)
        if view:
            view.grid(row=0, column=0, sticky="nsew")
            self.current_view = key

        # Update user label
        if self.current_user:
            self.user_label.configure(text=self.current_user["username"])
            self.login_btn.configure(text="Logout")
        else:
            self.user_label.configure(text="Not logged in")
            self.login_btn.configure(text="Login")

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    def show_login(self):
        """Show login dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Login - KnightX_fsm")
        dialog.geometry("400x500")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 250
        dialog.geometry(f"400x500+{x}+{y}")

        ctk.CTkLabel(
            dialog, text="KnightX_fsm",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY,
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            dialog, text="Please log in to continue",
            font=ctk.CTkFont(size=14),
            text_color=COLOR_TEXT_MUTED,
        ).pack(pady=(0, 30))

        # Username
        ctk.CTkLabel(dialog, text="Username", anchor="w").pack(
            padx=40, anchor="w"
        )
        username_entry = ctk.CTkEntry(dialog, width=320, placeholder_text="admin")
        username_entry.pack(padx=40, pady=(5, 20))

        # Password
        ctk.CTkLabel(dialog, text="Password", anchor="w").pack(
            padx=40, anchor="w"
        )
        password_entry = ctk.CTkEntry(dialog, width=320, placeholder_text="Password", show="*")
        password_entry.pack(padx=40, pady=(5, 20))

        error_label = ctk.CTkLabel(dialog, text="", text_color=COLOR_DANGER)
        error_label.pack(pady=(0, 20))

        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get()
            if not username or not password:
                error_label.configure(text="Please enter username and password")
                return
            user = db.authenticate_user(username, password)
            if user:
                self.current_user = user
                db.log_activity(user["id"], "login", "User logged in")
                error_label.configure(text="")
                dialog.destroy()
                self.switch_view(self.current_view or "dashboard")
            else:
                error_label.configure(text="Invalid username or password")

        ctk.CTkButton(
            dialog, text="Login", width=320, height=40,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            command=do_login,
        ).pack(padx=40, pady=(10, 20))

        ctk.CTkButton(
            dialog, text="Cancel", width=320, height=32,
            fg_color="transparent", text_color=COLOR_TEXT,
            command=dialog.destroy,
        ).pack(padx=40, pady=(0, 30))

        username_entry.focus()

    # ------------------------------------------------------------------
    # Placeholder views (implemented in separate files)
    # ------------------------------------------------------------------
    def _build_dashboard_view(self):
        self.dashboard_view = ctk.CTkFrame(self.views_container, fg_color="transparent")
        ctk.CTkLabel(
            self.dashboard_view, text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=30)
        ctk.CTkLabel(
            self.dashboard_view, text="Welcome to KnightX_fsm",
            font=ctk.CTkFont(size=16),
            text_color=COLOR_TEXT_MUTED,
        ).pack()

    def _build_explorer_view(self):
        self.explorer_view = ExplorerView(self.views_container, self)

    def _build_storage_view(self):
        self.storage_view = StorageView(self.views_container, self)

    def _build_security_view(self):
        self.security_view = SecurityView(self.views_container, self)

    def _build_tools_view(self):
        self.tools_view = ToolsView(self.views_container, self)

    def _build_ai_view(self):
        self.ai_view = AIView(self.views_container, self)

    def _build_settings_view(self):
        self.settings_view = SettingsView(self.views_container, self)

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------
    def set_status(self, message: str):
        self.status_label.configure(text=message)

    def update_ai_status(self):
        if ai.is_available():
            self.ai_status_label.configure(text="AI: Online", text_color=COLOR_SUCCESS)
        else:
            self.ai_status_label.configure(text="AI: Offline", text_color=COLOR_TEXT_MUTED)


if __name__ == "__main__":
    from pathlib import Path
    app = KnightXApp()
    app.update_ai_status()
    app.mainloop()