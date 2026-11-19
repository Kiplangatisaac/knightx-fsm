# KnightX_fsm - Futuristic File System Manager

**Version 2.0.0** | A modern, cross-platform file system manager with AI integration, security scanning, and junk cleaning.

## Overview

KnightX_fsm is a next-generation file management application built with Python and CustomTkinter. It features a sleek, futuristic dark-themed UI inspired by Windows and Google file managers, with full backend database support, AES-256 encryption, ClamAV antivirus integration, duplicate detection, junk file cleaning, USB device management, and local LLM (Ollama) AI integration.

## Features

### Core File Management
- **Modern File Explorer** - Intuitive interface with back/forward/up/home navigation, path bar, and file operations
- **Duplicate File Finder** - SHA-256 based detection with size pre-filtering
- **Junk File Cleaner** - Automatically detects and removes temporary, cache, and junk files
- **File Operations** - Create folders, rename, delete files and directories

### Security & Antivirus
- **ClamAV Integration** - Virus scanning for individual files and entire directories
- **Virus Definition Updates** - One-click freshclam integration
- **Threat Detection** - Real-time infected file identification
- **AES-256 Encryption** - All sensitive data encrypted at rest
- **bcrypt Password Hashing** - Secure user authentication

### AI Integration
- **Ollama LLM Integration** - Connect to local LLMs for intelligent file analysis
- **AI Chat Assistant** - Ask questions about file management and security
- **Anomaly Detection** - AI-powered file risk scoring
- **Directory Summarization** - AI-generated summaries of directory contents

### System Monitoring
- **Storage Visualization** - Interactive disk usage cards with percentage indicators
- **USB Device Detection** - Automatic detection and scanning of USB storage
- **Activity Logging** - Complete audit trail of all operations
- **System Metrics** - CPU, memory, and disk monitoring

### User Management
- **Multi-user Support** - Separate user accounts with roles (admin/user)
- **Secure Login** - Bcrypt-hashed passwords with session tracking
- **Activity Audit** - All user actions logged to database

## Project Structure

```
KnightX_fsm/
├── main.py                 # Application entry point
├── config.py               # Centralized configuration
├── encryption.py           # AES-256 encryption & password hashing
├── database.py             # SQLite database management
├── ai_integration.py       # Ollama LLM integration
├── file_operations.py      # File scanning, duplicate/junk detection, ClamAV
├── views/                  # UI views
│   ├── __init__.py
│   ├── explorer.py         # File Explorer view
│   ├── storage.py          # Storage monitoring view
│   ├── security.py         # Virus scanning view
│   ├── tools.py            # Tools (duplicates, USB, log)
│   ├── ai_view.py          # AI Assistant view
│   └── settings.py         # Settings view
├── build.sh                # Build and deployment script
├── buildozer.spec          # Android APK build configuration
├── knightx_fsm.spec        # PyInstaller specification
├── data/                   # Database and runtime data (created at runtime)
├── assets/                 # Icons and assets
└── docs/                   # Documentation
```

## Installation

### Prerequisites

#### System Packages (Linux)

**Ubuntu/Debian/Kali:**
```bash
sudo apt update
sudo apt install -y \
    clamav clamav-daemon clamav-freshclam \
    gir1.2-gtk-3.0 python3-gi python3-gi-cairo \
    python3-pyclamd python3-pyudev \
    libgl1-mesa-glx libegl1-mesa \
    libxrandr2 libxss1 libxcursor1 libxcomposite1 \
    libasound2 libxi6 libxtst6 \
    wget
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
    clamav clamav-update \
    gtk3 python3-gobject \
    libXrandr libXScrSaver libXcursor libXcomposite \
    libXSS libXi libXtst
```

**Arch Linux:**
```bash
sudo pacman -S --noconfirm \
    clamav gtk3 python-gobject python-pip \
    libxrandr libxss libxcursor libxcomposite \
    libxcomposite alsa-lib
```

### Python Dependencies

```bash
pip install customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller
```

### Quick Start

```bash
# Clone or navigate to the project
cd /home/janitor/file_manager_app

# Make build script executable
chmod +x build.sh

# Install system dependencies (one-time)
./build.sh deps

# Run in development mode
./build.sh dev
```

**Default Login Credentials:**
- Username: `admin`
- Password: `KnightX@2026!`

## Building

### AppImage (Linux)

```bash
./build.sh build
```

This creates `KnightX_fsm-x86_64.AppImage` in the project directory. Make it executable and run:

```bash
chmod +x KnightX_fsm-x86_64.AppImage
./KnightX_fsm-x86_64.AppImage
```

### Android APK

KnightX_fsm can be built as an Android APK using Buildozer:

```bash
# Install buildozer
pip install buildozer cython

# Initialize (already done - buildozer.spec exists)
./build.sh android

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release
```

The APK will be output to the `bin/` directory.

**Android Requirements:**
- Android API 24+ (Android 7.0+)
- Target API 33 (Android 13)
- Permissions: Internet, Storage, Camera, Location

### Standalone Executable (PyInstaller)

```bash
pyinstaller --noconfirm --onefile --windowed \
    --name KnightX_fsm \
    --add-data "config.py:." \
    --add-data "encryption.py:." \
    --add-data "database.py:." \
    --add-data "ai_integration.py:." \
    --add-data "file_operations.py:." \
    --add-data "views:views" \
    --hidden-import=customtkinter \
    --hidden-import=psutil \
    --hidden-import=Crypto \
    --hidden-import=cryptography \
    --hidden-import=bcrypt \
    --hidden-import=jwt \
    --hidden-import=requests \
    main.py
```

Output: `dist/KnightX_fsm`

## AI Integration (Ollama)

KnightX_fsm integrates with Ollama for local AI processing:

### Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3.2
```

### Configure

In the AI Assistant view, enter your model name (default: `llama3.2`) and click "Pull Model" if needed. The AI status indicator in the bottom-right shows online/offline status.

### AI Features

- **Chat** - Ask KnightX anything about file management, security, or cleanup
- **Directory Summarization** - Get AI summaries of any directory
- **Security Tips** - Get practical computer security advice
- **Cleanup Advice** - Get guidance on freeing disk space

## Database Schema

KnightX_fsm uses SQLite with the following tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts with bcrypt-hashed passwords |
| `file_metadata` | Scanned file information (path, size, hash, risk score) |
| `scan_history` | History of all scans (virus, junk, duplicates) |
| `usb_devices` | Detected USB devices and scan status |
| `activity_log` | Audit trail of all user actions |
| `system_metrics` | CPU, memory, and disk usage snapshots |

See `docs/DATABASE_SCHEMA.md` for full schema details.

## Security

- All passwords hashed with bcrypt (12 rounds)
- Sensitive data encrypted with AES-256 (Fernet)
- Encryption key stored with 600 permissions
- Database uses WAL journal mode for consistency
- Foreign key constraints enabled
- SQL injection prevention via parameterized queries

## File Formats Supported

All file types are supported for browsing and scanning. Junk detection targets:
`.tmp, .temp, .bak, .old, .orig, .cache, .log, .swp, .swo, ~, .dmp, .crash`

Common junk directories: `__pycache__, .cache, node_modules, .gradle, .m2, build, dist, .venv`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't start | Ensure GTK system packages installed; run from terminal to see errors |
| ClamAV not found | Install clamav: `sudo apt install clamav clamav-daemon` |
| AI offline | Start Ollama: `ollama serve` and pull a model |
| Permission denied on scan | Run with appropriate permissions or scan user-accessible directories |
| AppImage won't run | `chmod +x KnightX_fsm-x86_64.AppImage` and ensure FUSE is installed |

## License

MIT License - feel free to modify and enhance for your specific needs.

## Support

For issues and feature requests, please open an issue on the GitHub repository.