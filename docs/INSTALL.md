# KnightX_fsm - Installation & Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Linux Installation](#linux-installation)
3. [Windows Installation](#windows-installation)
4. [macOS Installation](#macos-installation)
5. [Android Deployment](#android-deployment)
6. [AppImage Deployment](#appimage-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Post-Installation Configuration](#post-installation-configuration)
9. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum
- **OS:** Linux (Ubuntu 20.04+, Debian 11+, Kali Linux, Fedora 35+, Arch Linux)
- **Python:** 3.10+
- **RAM:** 2 GB
- **Storage:** 500 MB free space
- **Display:** Graphical desktop environment (GNOME, KDE, XFCE, etc.)

### Recommended
- **OS:** Kali Linux or Ubuntu 22.04+
- **Python:** 3.11+
- **RAM:** 4 GB+
- **Storage:** 2 GB free space
- **Display:** 1920x1080 or higher
- **Ollama:** For AI features (optional but recommended)

---

## Linux Installation

### Method 1: Development Mode (Recommended for testing)

```bash
# 1. Clone or navigate to the project
cd /home/janitor/file_manager_app

# 2. Install system dependencies
./build.sh deps

# 3. Run the application
./build.sh dev
```

### Method 2: AppImage (Pre-built, portable)

```bash
# 1. Download the AppImage from the Releases page
wget https://github.com/your-org/KnightX_fsm/releases/download/v2.0.0/KnightX_fsm-x86_64.AppImage

# 2. Make executable
chmod +x KnightX_fsm-x86_64.AppImage

# 3. Run
./KnightX_fsm-x86_64.AppImage
```

### Method 3: System-wide Installation

```bash
# 1. Install system packages
sudo apt update
sudo apt install -y python3-pip python3-venv clamav clamav-daemon clamav-freshclam

# 2. Create application directory
sudo mkdir -p /opt/knightx_fsm
sudo cp -r /home/janitor/file_manager_app/* /opt/knightx_fsm/

# 3. Set up virtual environment
cd /opt/knightx_fsm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Create desktop entry
sudo tee /usr/share/applications/knightx_fsm.desktop << 'EOF'
[Desktop Entry]
Name=KnightX_fsm
Comment=Futuristic File System Manager
Exec=/opt/knightx_fsm/venv/bin/python /opt/knightx_fsm/main.py
Icon=knightx_fsm
Type=Application
Categories=System;FileManager;
EOF

# 5. Create launcher script
sudo tee /usr/local/bin/knightx_fsm << 'EOF'
#!/bin/bash
source /opt/knightx_fsm/venv/bin/activate
exec python /opt/knightx_fsm/main.py "$@"
EOF
sudo chmod +x /usr/local/bin/knightx_fsm

# 6. Run
knightx_fsm
```

---

## Windows Installation

KnightX_fsm is primarily developed for Linux, but can run on Windows with some limitations:

### Prerequisites
- Python 3.10+ from https://python.org
- Git for Windows
- ClamAV for Windows (https://www.clamav.net/)

### Installation

```powershell
# 1. Clone the repository
git clone <repository-url>
cd file_manager_app

# 2. Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller

# 4. Install ClamAV for Windows
# Download and install from https://www.clamav.net/

# 5. Run the application
python main.py
```

**Note:** Some Linux-specific features (USB detection via pyudev, ClamAV daemon) may not work on Windows.

---

## macOS Installation

### Prerequisites
- macOS 10.15+
- Python 3.10+ (via Homebrew or python.org)
- ClamAV (via Homebrew)

### Installation

```bash
# 1. Install Homebrew packages
brew install clamav python3 gtk+3 pygobject3

# 2. Clone the repository
git clone <repository-url>
cd file_manager_app

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller

# 5. Run
python main.py
```

---

## Android Deployment

KnightX_fsm can be deployed to Android using Buildozer (Python for Android).

### Prerequisites

```bash
# Install buildozer and dependencies
pip install buildozer cython

# Install Android SDK dependencies (Ubuntu/Debian)
sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
    pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev
```

### Build Debug APK

```bash
cd /home/janitor/file_manager_app

# Initialize buildozer (already configured in buildozer.spec)
buildozer init

# Build debug APK
buildozer android debug
```

The APK will be created in the `bin/` directory:
```
bin/KnightX_fsm-2.0.0-debug.apk
```

### Install on Android Device

```bash
# Enable USB debugging on your Android device, then:
adb install bin/KnightX_fsm-2.0.0-debug.apk
```

### Build Release APK

```bash
buildozer android release
```

Sign the APK before publishing:
```bash
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/KnightX_fsm-2.0.0-release.apk alias_name
zipalign -v 4 bin/KnightX_fsm-2.0.0-release.apk KnightX_fsm-aligned.apk
```

### Android Permissions

The app requests the following permissions:
- `INTERNET` - For AI API calls and updates
- `WRITE_EXTERNAL_STORAGE` - For file operations
- `READ_EXTERNAL_STORAGE` - For file browsing
- `ACCESS_FINE_LOCATION` - For location-aware features
- `CAMERA` - For future face recognition features

**Note:** On Android 10+, scoped storage limits access to app-specific directories. Full file system access requires root or special permissions.

---

## AppImage Deployment

### Building AppImage

```bash
cd /home/janitor/file_manager_app

# Make build script executable
chmod +x build.sh

# Build AppImage
./build.sh build
```

This creates:
```
KnightX_fsm-x86_64.AppImage
```

### Distributing AppImage

1. Upload the `.AppImage` file to your GitHub Releases page
2. Users download, make executable (`chmod +x`), and run
3. No installation required - runs on any Linux distribution with FUSE

### AppImage Requirements

- Linux kernel 3.2+
- FUSE (Filesystem in Userspace)
- glibc 2.17+
- Desktop environment with GTK libraries

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    clamav clamav-daemon clamav-freshclam \
    libgl1-mesa-glx libegl1-mesa \
    libxrandr2 libxss1 libxcursor1 libxcomposite1 \
    libasound2 libxi6 libxtst6 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller

# Create data directory
RUN mkdir -p /app/data

# Expose port (if needed for future web features)
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
```

### Build and Run

```bash
# Build image
docker build -t knightx_fsm .

# Run container (requires X11 forwarding for GUI)
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    knightx_fsm
```

---

## Post-Installation Configuration

### 1. Update ClamAV Definitions

```bash
sudo freshclam
sudo systemctl start clamav-freshclam
sudo systemctl enable clamav-freshclam
```

### 2. Start Ollama (for AI features)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve &

# Pull a model
ollama pull llama3.2
```

### 3. First Login

Default credentials:
- **Username:** `admin`
- **Password:** `KnightX@2026!`

**Important:** Change the default password immediately after first login.

### 4. Configure Encryption Key

The encryption key is automatically generated at `data/.encryption_key` with 600 permissions. Back up this file securely - without it, encrypted data cannot be recovered.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'customtkinter'` | Run `pip install customtkinter` |
| `Gtk-CRITICAL` errors | Install GTK system packages: `sudo apt install gir1.2-gtk-3.0 python3-gi` |
| ClamAV: `clamscan: command not found` | Install: `sudo apt install clamav` |
| AI: Offline | Start Ollama: `ollama serve` and ensure model is pulled |
| AppImage won't execute | Run `chmod +x KnightX_fsm-x86_64.AppImage` |
| Permission denied on data directory | `chmod -R 755 data/` |
| Database locked | Ensure only one instance is running; SQLite uses file locking |
| Android build fails | Ensure Android SDK, NDK, and JDK are installed; check `buildozer.spec` |

### Log Files

Activity logs are stored in the SQLite database (`data/knightx_fsm.db`). View them in the Tools > Activity Log section of the application.

### Reset Admin Password

If you forget the admin password, reset it directly in the database:

```bash
sqlite3 data/knightx_fsm.db "UPDATE users SET password_hash = '\$2b\$12\$K2X...' WHERE username = 'admin';"
```

Or delete the database to reset to defaults (will lose all data):
```bash
rm data/knightx_fsm.db
```