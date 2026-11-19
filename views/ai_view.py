"""
KnightX_fsm - AI Assistant View
Integration with Ollama LLM for file analysis and chat.
"""

import customtkinter as ctk
import threading

from config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_WARNING,
    COLOR_DANGER, COLOR_INFO, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_SURFACE, COLOR_BACKGROUND, COLOR_ACCENT,
)
from ai_integration import ai
from database import db


class AIView(ctk.CTkFrame):
    """AI Assistant view with Ollama integration."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build_ui()
        self.check_ai_status()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="AI Assistant",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(anchor="w", padx=30, pady=(30, 10))

        # AI status
        self.ai_status_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        self.ai_status_frame.pack(fill="x", padx=30, pady=10)

        self.ai_status_label = ctk.CTkLabel(
            self.ai_status_frame, text="Checking AI connection...",
            text_color=COLOR_TEXT_MUTED,
        )
        self.ai_status_label.pack(anchor="w", padx=20, pady=15)

        # Model selection
        self.model_frame = ctk.CTkFrame(self.ai_status_frame, fg_color="transparent")
        self.model_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.model_label = ctk.CTkLabel(self.model_frame, text="Model:")
        self.model_label.pack(side="left", padx=(0, 10))

        self.model_entry = ctk.CTkEntry(self.model_frame, width=200, placeholder_text="llama3.2")
        self.model_entry.pack(side="left", padx=(0, 10))
        self.model_entry.insert(0, "llama3.2")

        self.btn_pull = ctk.CTkButton(
            self.model_frame, text="Pull Model", width=100,
            command=self.pull_model,
            fg_color=COLOR_INFO, hover_color="#0891b2"
        )
        self.btn_pull.pack(side="left")

        # Chat area
        chat_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        chat_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self.chat_text = ctk.CTkTextbox(chat_frame, fg_color=COLOR_BACKGROUND, height=300)
        self.chat_text.pack(fill="both", expand=True, padx=20, pady=20)

        # Input area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.chat_input = ctk.CTkEntry(
            input_frame, placeholder_text="Ask KnightX AI...",
            height=40,
        )
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.chat_input.bind("<Return>", lambda e: self.send_message())

        self.btn_send = ctk.CTkButton(
            input_frame, text="Send", width=80, height=40,
            command=self.send_message,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        self.btn_send.pack(side="right")

        # Quick actions
        quick_frame = ctk.CTkFrame(self, fg_color=COLOR_SURFACE)
        quick_frame.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(
            quick_frame, text="Quick Actions",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(15, 10))

        quick_btn_frame = ctk.CTkFrame(quick_frame, fg_color="transparent")
        quick_btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        actions = [
            ("📁 Summarize Directory", self.summarize_directory),
            ("🛡️ Security Tips", self.security_tips),
            ("🧹 Cleanup Advice", self.cleanup_advice),
        ]

        for label, cmd in actions:
            ctk.CTkButton(
                quick_btn_frame, text=label, width=150,
                command=cmd,
                fg_color=COLOR_SURFACE, hover_color=COLOR_PRIMARY_HOVER,
                text_color=COLOR_TEXT,
            ).pack(side="left", padx=5)

    def check_ai_status(self):
        def run():
            if ai.is_available():
                self.ai_status_label.configure(text="AI: Online ✓", text_color=COLOR_SUCCESS)
                models = ai.list_models()
                if models:
                    self.ai_status_label.configure(
                        text=f"AI: Online ✓ ({len(models)} model(s))",
                        text_color=COLOR_SUCCESS,
                    )
            else:
                self.ai_status_label.configure(text="AI: Offline - Start Ollama", text_color=COLOR_WARNING)

        threading.Thread(target=run, daemon=True).start()

    def pull_model(self):
        model_name = self.model_entry.get().strip() or "llama3.2"

        def run():
            self.app.set_status(f"Pulling model {model_name}...")
            self.btn_pull.configure(state="disabled")
            success = ai.pull_model(model_name)
            self.btn_pull.configure(state="normal")
            if success:
                self.ai_status_label.configure(text=f"AI: Online ✓ ({model_name})", text_color=COLOR_SUCCESS)
                self.app.set_status(f"Model {model_name} pulled successfully")
            else:
                self.app.set_status(f"Failed to pull model {model_name}")

        threading.Thread(target=run, daemon=True).start()

    def send_message(self):
        message = self.chat_input.get().strip()
        if not message:
            return
        self.chat_input.delete(0, "end")
        self._append_chat("You", message)

        def run():
            response = ai.chat(message)
            self._append_chat("KnightX", response)
            self.app.set_status("Ready")

        threading.Thread(target=run, daemon=True).start()

    def _append_chat(self, sender, message):
        self.chat_text.insert("end", f"{sender}: {message}\n\n")
        self.chat_text.see("end")

    def summarize_directory(self):
        from pathlib import Path
        path = str(Path.home())
        def run():
            self.app.set_status("Generating AI summary...")
            summary = ai.summarize_directory(path, 0, 0)
            self._append_chat("KnightX", f"Directory summary for {path}:\n{summary}")
            self.app.set_status("Ready")
        threading.Thread(target=run, daemon=True).start()

    def security_tips(self):
        def run():
            self.app.set_status("Getting security tips...")
            response = ai.chat("Give me 5 practical computer security tips for personal file management.")
            self._append_chat("KnightX", response)
            self.app.set_status("Ready")
        threading.Thread(target=run, daemon=True).start()

    def cleanup_advice(self):
        def run():
            self.app.set_status("Getting cleanup advice...")
            response = ai.chat("Give me advice on how to clean up junk files and free disk space safely.")
            self._append_chat("KnightX", response)
            self.app.set_status("Ready")
        threading.Thread(target=run, daemon=True).start()