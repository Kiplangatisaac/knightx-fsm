"""
KnightX_fsm - Configuration Module
Centralized configuration for the KnightX File System Manager.
"""

import os
from pathlib import Path

# --- Application Info ---
APP_NAME = "KnightX_fsm"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Futuristic File System Manager for Linux"
APP_AUTHOR = "KnightX Development"

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "knightx_fsm.db"
LOG_PATH = DATA_DIR / "activity.log"
ENCRYPTION_KEY_PATH = DATA_DIR / ".encryption_key"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
THEMES_DIR = ASSETS_DIR / "themes"

# --- Ensure directories exist ---
for _d in (DATA_DIR, ASSETS_DIR, ICONS_DIR, THEMES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- UI Theme ---
THEME_MODE = "dark"  # "dark" or "light"
COLOR_PRIMARY = "#4f46e5"       # Indigo
COLOR_PRIMARY_HOVER = "#4338ca"
COLOR_SUCCESS = "#10b981"       # Emerald
COLOR_WARNING = "#f59e0b"       # Amber
COLOR_DANGER = "#ef4444"        # Red
COLOR_INFO = "#06b6d4"          # Cyan
COLOR_BACKGROUND = "#0f172a"    # Slate-900
COLOR_SURFACE = "#1e293b"       # Slate-800
COLOR_SURFACE_HOVER = "#334155" # Slate-700
COLOR_TEXT = "#f8fafc"          # Slate-50
COLOR_TEXT_MUTED = "#94a3b8"    # Slate-400
COLOR_ACCENT = "#8b5cf6"        # Violet
COLOR_GRADIENT_START = "#4f46e5"
COLOR_GRADIENT_END = "#ec4899"

# --- File Operations ---
CHUNK_SIZE = 65536  # 64KB for hashing
MAX_RECENT_PATHS = 10
JUNK_EXTENSIONS = [
    ".tmp", ".temp", ".bak", ".old", ".orig", ".cache", ".log",
    ".swp", ".swo", "~", ".dmp", ".crash", ".gsynctemp"
]
JUNK_PATTERNS = [
    "*.tmp", "*.temp", "*.bak", "*.old", "*.orig", "*.cache",
    "*.log", "*.swp", "*.swo", "*~", "*.dmp", "*.crash",
    ".DS_Store", "Thumbs.db", "desktop.ini"
]
COMMON_JUNK_DIRS = [
    "__pycache__", ".cache", "node_modules", ".gradle", ".m2",
    "build", "dist", ".venv", "venv", "env", ".tox"
]

# --- Security ---
ENCRYPTION_ALGORITHM = "AES-256"
TOKEN_EXPIRY_HOURS = 24
BCRYPT_ROUNDS = 12

# --- AI Integration (Ollama) ---
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"
AI_ANOMALY_THRESHOLD = 0.7

# --- ClamAV ---
CLAMSCAN_PATH = "/usr/bin/clamscan"
FRESHCLAM_PATH = "/usr/bin/freshclam"
CLAMAV_DB_DIR = "/var/lib/clamav"

# --- Database Tables ---
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """,
    "file_metadata": """
        CREATE TABLE IF NOT EXISTS file_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            name TEXT NOT NULL,
            size INTEGER NOT NULL,
            file_type TEXT,
            mime_type TEXT,
            sha256 TEXT,
            is_duplicate INTEGER DEFAULT 0,
            is_junk INTEGER DEFAULT 0,
            risk_score REAL DEFAULT 0.0,
            last_scanned TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "scan_history": """
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT NOT NULL,
            target_path TEXT,
            files_scanned INTEGER DEFAULT 0,
            threats_found INTEGER DEFAULT 0,
            duplicates_found INTEGER DEFAULT 0,
            junk_found INTEGER DEFAULT 0,
            space_recovered INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "usb_devices": """
        CREATE TABLE IF NOT EXISTS usb_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_name TEXT,
            device_path TEXT,
            serial_number TEXT,
            vendor_id TEXT,
            product_id TEXT,
            size INTEGER,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scan_status TEXT DEFAULT 'pending',
            threats_found INTEGER DEFAULT 0
        )
    """,
    "activity_log": """
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """,
    "system_metrics": """
        CREATE TABLE IF NOT EXISTS system_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL,
            network_sent INTEGER,
            network_recv INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
}

# --- Default Admin User ---
DEFAULT_ADMIN = {
    "username": "admin",
    "password": "KnightX@2026!",
    "email": "admin@knightx.local",
    "role": "admin"
}