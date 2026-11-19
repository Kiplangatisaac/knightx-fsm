#!/bin/bash
# KnightX_fsm - Build and Run Script
# Supports: development run, AppImage build, and APK build

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/venv"
APP_ENTRY="main.py"
APP_NAME="KnightX_fsm"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  KnightX_fsm - Build & Run Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Activate venv if it exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}[+]${NC} Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
else
    echo -e "${YELLOW}[!]${NC} Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller
fi

# Function: Run in development mode
run_dev() {
    echo -e "${GREEN}[+]${NC} Starting KnightX_fsm in development mode..."
    python3 "$APP_ENTRY"
}

# Function: Build AppImage
build_appimage() {
    echo -e "${GREEN}[+]${NC} Building AppImage for $APP_NAME..."

    # Check for appimagetool
    if ! command -v appimagetool &> /dev/null; then
        echo -e "${YELLOW}[!]${NC} appimagetool not found. Installing..."
        wget -O /tmp/appimagetool.AppImage "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" 2>/dev/null || \
        wget -O /tmp/appimagetool.AppImage "https://github.com/AppImage/AppImageKit/releases/download/13.0.0/appimagetool-x86_64.AppImage" 2>/dev/null || true
        chmod +x /tmp/appimagetool.AppImage
    fi

    # Build with PyInstaller
    echo -e "${GREEN}[+]${NC} Running PyInstaller..."
    pyinstaller --noconfirm --onefile --windowed \
        --name "$APP_NAME" \
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

    # Create AppDir structure
    APPDIR="$SCRIPT_DIR/build/$APP_NAME.AppDir"
    rm -rf "$APPDIR"
    mkdir -p "$APPDIR/usr/bin"
    mkdir -p "$APPDIR/usr/share/applications"
    mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

    # Copy binary
    cp "$SCRIPT_DIR/dist/$APP_NAME" "$APPDIR/usr/bin/"

    # Create desktop file
    cat > "$APPDIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Name=$APP_NAME
Comment=Futuristic File System Manager
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=System;FileManager;
EOF

    # Create AppRun
    cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
exec ./usr/bin/"$(basename "$0" .AppDir)" "$@"
EOF
    chmod +x "$APPDIR/AppRun"

    # Create .desktop inside AppDir root
    cp "$APPDIR/usr/share/applications/$APP_NAME.desktop" "$APPDIR/$APP_NAME.desktop"

    # Build AppImage
    echo -e "${GREEN}[+]${NC} Creating AppImage..."
    ARCH=x86_64 /tmp/appimagetool.AppImage "$APPDIR" "$SCRIPT_DIR/${APP_NAME}-${APP_VERSION}-x86_64.AppImage" 2>/dev/null || \
    (cd "$APPDIR" && ARCH=x86_64 /tmp/appimagetool.AppImage . "$SCRIPT_DIR/${APP_NAME}-x86_64.AppImage") 2>/dev/null || true

    if [ -f "$SCRIPT_DIR/${APP_NAME}"*.AppImage ]; then
        echo -e "${GREEN}[+]${NC} AppImage created: $SCRIPT_DIR/${APP_NAME}*.AppImage"
        chmod +x "$SCRIPT_DIR/${APP_NAME}"*.AppImage
    else
        echo -e "${RED}[!]${NC} AppImage build failed. Check pyinstaller output."
    fi
}

# Function: Build Android APK (requires buildozer)
build_android() {
    echo -e "${GREEN}[+]${NC} Preparing Android build..."

    if ! command -v buildozer &> /dev/null; then
        echo -e "${YELLOW}[!]${NC} buildozer not found. Installing..."
        pip install buildozer cython
    fi

    # Initialize buildozer spec if not exists
    if [ ! -f "buildozer.spec" ]; then
        buildozer init
    fi

    echo -e "${GREEN}[+]${NC} Buildozer initialized. Edit buildozer.spec and run 'buildozer android debug' to build APK."
}

# Function: Install system dependencies (Linux)
install_deps() {
    echo -e "${GREEN}[+]${NC} Installing system dependencies..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            clamav clamav-daemon clamav-freshclam \
            gir1.2-gtk-3.0 python3-gi python3-gi-cairo python3-pyclamd python3-pyudev \
            libgl1-mesa-glx libegl1-mesa libxrandr2 libxss1 libxcursor1 libxcomposite1 \
            libasound2 libxi6 libxtst6 wget
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y clamav clamav-update gtk3 python3-gobject PyQt5
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm clamav gtk3 python-gobject python-pip
    else
        echo -e "${YELLOW}[!]${NC} Unknown package manager. Install dependencies manually."
    fi
}

# Main
case "${1:-dev}" in
    dev)
        run_dev
        ;;
    build)
        build_appimage
        ;;
    android)
        build_android
        ;;
    deps)
        install_deps
        ;;
    *)
        echo "Usage: $0 {dev|build|android|deps}"
        echo "  dev       - Run in development mode (default)"
        echo "  build     - Build AppImage"
        echo "  android   - Prepare Android build"
        echo "  deps      - Install system dependencies"
        exit 1
        ;;
esac