"""
KnightX_fsm - Settings View
Application settings and user management.
"""

import customtkinter as ctk

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_INFO, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_BACKGROUND,
)
from database import db
from encryption import encryption


class SettingsView(ctk.CTkFrame):
    """Settings and configuration view."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(30, 10))

        # Appearance
        appearance_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        appearance_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            appearance_frame, text="Appearance",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left", padx=(0, 10))

        self.theme_var = ctk.StringVar(value="dark")
        self.theme_menu = ctk.CTkOptionMenu(
            theme_frame, values=["dark", "light"],
            variable=self.theme_var,
            command=self.change_theme,
            width=120,
        )
        self.theme_menu.pack(side="left")

        # User account
        user_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        user_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            user_frame, text="User Account",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self.user_info_label = ctk.CTkLabel(
            user_frame, text="Not logged in",
            text_color=COLOR_TEXT_MUTED,
        )
        self.user_info_label.pack(anchor="w", padx=20, pady=(0, 10))

        # Change password
        pass_frame = ctk.CTkFrame(user_frame, fg_color="transparent")
        pass_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(pass_frame, text="New Password:").pack(side="left", padx=(0, 10))
        self.new_pass_entry = ctk.CTkEntry(pass_frame, width=200, show="*")
        self.new_pass_entry.pack(side="left", padx=(0, 10))

        self.btn_change_pass = ctk.CTkButton(
            pass_frame, text="Change", width=80,
            command=self.change_password,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_change_pass.pack(side="left")

        # Security
        security_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        security_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            security_frame, text="Security",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            security_frame, text="All sensitive data is encrypted at rest using AES-256.",
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            security_frame, text="Passwords are hashed using bcrypt.",
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 20))

        # About
        about_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        about_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            about_frame, text="About KnightX_fsm",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT,
        ).pack(anchor="w", padx=20, pady=(20, 5))

        ctk.CTkLabel(
            about_frame, text="Version 2.0.0\nFuturistic File System Manager for Linux\nBuilt with Python, CustomTkinter, and SQLite",
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 20))

    def change_theme(self, value):
        ctk.set_appearance_mode(value)

    def change_password(self):
        new_password = self.new_pass_entry.get().strip()
        if not new_password:
            return
        if len(new_password) < 6:
            ctk.CTkLabel(
                self, text="Password must be at least 6 characters",
                text_color=COLOR_DANGER,
            ).pack()
            return
        if self.app.current_user:
            # Update password in DB
            import sqlite3
            try:
                hashed = encryption.hash_password(new_password)
                with db.get_connection() as conn:
                    conn.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (hashed, self.app.current_user["id"]),
                    )
                self.new_pass_entry.delete(0, "end")
                ctk.CTkLabel(
                    self, text="Password updated successfully",
                    text_color=COLOR_SUCCESS,
                ).pack()
            except Exception as e:
                ctk.CTkLabel(
                    self, text=f"Error: {e}",
                    text_color=COLOR_DANGER,
                ).pack()