"""
KnightX_fsm - AI Integration Module
Integration with local LLMs (Ollama) for anomaly detection and intelligent file analysis.
"""

import json
import logging
import requests
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, AI_ANOMALY_THRESHOLD

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI integration with Ollama for file anomaly detection."""

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._available = None

    def is_available(self) -> bool:
        """Check if Ollama server is available."""
        if self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            self._available = resp.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False

    def list_models(self) -> list:
        """List available models on Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []

    def pull_model(self, model_name: str = None) -> bool:
        """Pull a model from Ollama library."""
        model = model_name or self.model
        try:
            resp = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                timeout=300,
            )
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def analyze_file_anomaly(self, file_path: str, file_info: dict) -> float:
        """
        Analyze a file for anomalies using the LLM.
        Returns a risk score between 0.0 and 1.0.
        """
        if not self.is_available():
            return 0.0

        try:
            prompt = self._build_anomaly_prompt(file_path, file_info)
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                result = resp.json()
                response_text = result.get("response", "")
                score = self._extract_score(response_text)
                return max(0.0, min(1.0, score))
        except Exception as e:
            logger.error(f"AI anomaly analysis failed: {e}")
        return 0.0

    def analyze_file_anomaly_async(self, file_path: str, file_info: dict, callback):
        """Run anomaly analysis in a background thread."""
        def task():
            score = self.analyze_file_anomaly(file_path, file_info)
            callback(score)
        self.executor.submit(task)

    def summarize_directory(self, path: str, file_count: int, total_size: int) -> str:
        """Generate an AI summary of a directory."""
        if not self.is_available():
            return "AI unavailable - Ollama not running."

        try:
            prompt = (
                f"Summarize this directory: {path}\n"
                f"Files: {file_count}\n"
                f"Total size: {total_size} bytes\n"
                "Provide a brief, helpful summary of what this directory likely contains "
                "and any notable observations. Keep it under 100 words."
            )
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "temperature": 0.5},
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"AI directory summary failed: {e}")
        return "AI summary unavailable."

    def chat(self, message: str) -> str:
        """Send a chat message to the AI."""
        if not self.is_available():
            return "AI is not available. Please start Ollama."
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": message, "stream": False, "temperature": 0.7},
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "No response.")
        except Exception as e:
            logger.error(f"AI chat failed: {e}")
        return "AI request failed."

    def _build_anomaly_prompt(self, file_path: str, file_info: dict) -> str:
        """Build a prompt for anomaly detection."""
        return (
            f"Analyze this file for security risk:\n"
            f"Path: {file_path}\n"
            f"Name: {file_info.get('name', 'unknown')}\n"
            f"Size: {file_info.get('size', 0)} bytes\n"
            f"Type: {file_info.get('file_type', 'unknown')}\n"
            f"MIME: {file_info.get('mime_type', 'unknown')}\n\n"
            "Rate the security risk from 0.0 (safe) to 1.0 (dangerous). "
            "Consider: executable scripts in unusual locations, unusually large files, "
            "hidden files, files with double extensions, temp files, etc. "
            "Return ONLY a single number between 0.0 and 1.0."
        )

    def _extract_score(self, text: str) -> float:
        """Extract a numeric score from AI response."""
        import re
        match = re.search(r"(\d*\.?\d+)", text.strip())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.0


# Global instance
ai = AIManager()