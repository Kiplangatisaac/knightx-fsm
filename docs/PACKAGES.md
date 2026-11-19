# KnightX_fsm - Required Packages & Installation

## Complete Package List by Operating System

---

## Ubuntu / Debian / Kali Linux

### System Packages

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    clamav \
    clamav-daemon \
    clamav-freshclam \
    gir1.2-gtk-3.0 \
    python3-gi \
    python3-gi-cairo \
    python3-pyclamd \
    python3-pyudev \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    wget \
    git
```

### Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Or manually:

```bash
pip install \
    customtkinter>=6.0.0 \
    psutil>=7.2.2 \
    cryptography>=49.0.0 \
    pycryptodomex>=3.20.0 \
    bcrypt>=3.2.2 \
    pyjwt>=2.15.1 \
    requests>=2.34.2 \
    pyClamd>=0.4.0 \
    pyinstaller>=6.22.2 \
    buildozer>=1.5.0 \
    cython>=3.0.0
```

---

## Fedora / RHEL / CentOS

### System Packages

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    clamav \
    clamav-update \
    gtk3 \
    python3-gobject \
    libXrandr \
    libXScrSaver \
    libXcursor \
    libXcomposite \
    libXcomposite \
    libXSS \
    libXi \
    libXtst \
    wget \
    git
```

### Python Packages

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

## Arch Linux

### System Packages

```bash
sudo pacman -S --noconfirm \
    python \
    python-pip \
    clamav \
    gtk3 \
    python-gobject \
    libxrandr \
    libxss \
    libxcursor \
    libxcomposite \
    alsa-lib \
    wget \
    git
```

### Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## macOS

### System Packages (via Homebrew)

```bash
brew install \
    python3 \
    clamav \
    gtk+3 \
    pygobject3 \
    git
```

### Python Packages

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt
```

---

## Windows

### System Packages

1. Install Python 3.10+ from https://python.org
2. Install Git for Windows from https://git-scm.com/
3. Install ClamAV for Windows from https://www.clamav.net/
4. Add Python and ClamAV to PATH

### Python Packages

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** Some Linux-specific features (pyudev for USB detection, ClamAV daemon) have limited functionality on Windows.

---

## Android Build Dependencies

### Linux Host (for building APK)

```bash
sudo apt install -y \
    git zip unzip \
    openjdk-17-jdk \
    python3-pip \
    autoconf libtool \
    pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake \
    libffi-dev libssl-dev
```

### Python Packages

```bash
pip install buildozer cython
```

---

## Ollama (AI Features) - All Platforms

```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve &

# Pull model
ollama pull llama3.2
```

---

## Quick Install Script (Linux)

```bash
#!/bin/bash
# One-line installer for Ubuntu/Debian/Kali
sudo apt update && sudo apt install -y \
    python3 python3-pip python3-venv \
    clamav clamav-daemon clamav-freshclam \
    gir1.2-gtk-3.0 python3-gi python3-gi-cairo \
    python3-pyclamd python3-pyudev \
    libgl1-mesa-glx libegl1-mesa \
    libxrandr2 libxss1 libxcursor1 libxcomposite1 \
    libasound2 libxi6 libxtst6 \
    wget git

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Package Summary Table

| Category | Package | Purpose |
|----------|---------|---------|
| GUI | customtkinter | Modern dark-themed UI |
| System | psutil | CPU, memory, disk monitoring |
| Security | cryptography | AES-256 encryption |
| Security | pycryptodomex | Additional crypto primitives |
| Auth | bcrypt | Password hashing |
| Auth | pyjwt | JWT token support |
| HTTP | requests | API communication (Ollama) |
| Antivirus | pyClamd | ClamAV daemon interface |
| Build | pyinstaller | Standalone executable/AppImage |
| Android | buildozer | APK build tool |
| Android | cython | Python-to-C compiler for Android |

---

## Verification

After installation, verify all packages:

```bash
python3 -c "
import customtkinter
import psutil
from cryptography.fernet import Fernet
import bcrypt
import jwt
import requests
print('All core packages OK')
"
```
