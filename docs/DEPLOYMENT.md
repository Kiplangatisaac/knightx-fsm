# KnightX_fsm - Deployment Guide

## Deployment Options

KnightX_fsm supports multiple deployment methods:

| Method | Best For | Platform |
|--------|----------|----------|
| Development Mode | Testing, development | Linux |
| AppImage | Portable distribution | Linux |
| System Package | Production servers | Linux |
| Android APK | Mobile devices | Android |
| Docker | Containerized deployment | Linux |

---

## 1. Development Mode Deployment

For development and testing:

```bash
cd /home/janitor/file_manager_app
chmod +x build.sh
./build.sh dev
```

The application runs directly from source with hot-reload capabilities (restart to see changes).

---

## 2. AppImage Deployment (Production Linux)

AppImage is the recommended distribution method for Linux desktop users.

### Build

```bash
./build.sh build
```

Output: `KnightX_fsm-x86_64.AppImage`

### Distribute

1. Upload to GitHub Releases
2. Provide download link to users
3. Users run: `chmod +x KnightX_fsm-x86_64.AppImage && ./KnightX_fsm-x86_64.AppImage`

### Requirements for End Users

- Linux with FUSE support
- glibc 2.17+
- GTK3 libraries installed on host system

---

## 3. Android Deployment (APK)

### Build Debug APK

```bash
cd /home/janitor/file_manager_app
buildozer android debug
```

Output: `bin/KnightX_fsm-2.0.0-debug.apk`

### Build Release APK

```bash
buildozer android release
```

### Sign and Align (for Play Store)

```bash
# Generate keystore (one-time)
keytool -genkey -v -keystore knightx.keystore -alias knightx -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore knightx.keystore bin/KnightX_fsm-2.0.0-release.apk knightx

# Align APK
zipalign -v 4 bin/KnightX_fsm-2.0.0-release.apk KnightX_fsm.apk
```

### Install on Device

```bash
adb install KnightX_fsm.apk
```

### Android Limitations

- Scoped storage limits file system access (Android 10+)
- ClamAV may not be available on Android
- AI features require network connection to Ollama server
- Some system monitoring features limited

---

## 4. Docker Deployment

### Build Image

```bash
docker build -t knightx_fsm:2.0.0 .
```

### Run with GUI (X11 Forwarding)

```bash
docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /home/user/data:/app/data \
    knightx_fsm:2.0.0
```

### Docker Compose

```yaml
version: '3.8'
services:
  knightx_fsm:
    build: .
    container_name: knightx_fsm
    environment:
      - DISPLAY=:0
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ./data:/app/data
    network_mode: host
```

---

## 5. System-wide Package Deployment

### Create .deb Package (Debian/Ubuntu)

```bash
# Install dpkg-dev
sudo apt install dpkg-dev

# Build package structure
mkdir -p knightx_fsm-2.0.0/DEBIAN
mkdir -p knightx_fsm-2.0.0/usr/local/bin
mkdir -p knightx_fsm-2.0.0/usr/share/applications

# Copy files
cp -r /home/janitor/file_manager_app/* knightx_fsm-2.0.0/usr/local/bin/

# Create control file
cat > knightx_fsm-2.0.0/DEBIAN/control << EOF
Package: knightx-fsm
Version: 2.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pip, clamav, clamav-daemon, gir1.2-gtk-3.0, python3-gi
Maintainer: KnightX Development
Description: Futuristic File System Manager
EOF

# Create launcher
cat > knightx_fsm-2.0.0/usr/local/bin/knightx_fsm << 'EOF'
#!/bin/bash
exec python3 /usr/local/bin/knightx_fsm/main.py "$@"
EOF
chmod +x knightx_fsm-2.0.0/usr/local/bin/knightx_fsm

# Build .deb
dpkg-deb --build knightx_fsm-2.0.0
```

Install:
```bash
sudo dpkg -i knightx_fsm-2.0.0.deb
```

---

## 6. GitHub Actions CI/CD

Create `.github/workflows/release.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
          
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y clamav clamav-daemon clamav-freshclam
          pip install customtkinter psutil pycryptodomex cryptography bcrypt pyjwt requests pyinstaller
          
      - name: Build AppImage
        run: |
          chmod +x build.sh
          ./build.sh build
          
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: KnightX_fsm-x86_64.AppImage
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 7. Production Checklist

- [ ] Change default admin password
- [ ] Back up encryption key (`data/.encryption_key`)
- [ ] Configure regular ClamAV definition updates (`sudo freshclam`)
- [ ] Set up Ollama server for AI features
- [ ] Configure database backups
- [ ] Set appropriate file permissions on data directory
- [ ] Enable firewall rules if exposing any network services
- [ ] Review user accounts and roles

---

## 8. Data Backup & Recovery

### Backup

```bash
# Backup database
cp data/knightx_fsm.db knightx_fsm_backup_$(date +%Y%m%d).db

# Backup encryption key (CRITICAL)
cp data/.encryption_key .encryption_key_backup_$(date +%Y%m%d)

# Backup all data
tar czf knightx_fsm_backup_$(date +%Y%m%d).tar.gz data/
```

### Recovery

```bash
# Restore database
cp knightx_fsm_backup_YYYYMMDD.db data/knightx_fsm.db

# Restore encryption key (CRITICAL - must match)
cp .encryption_key_backup_YYYYMMDD data/.encryption_key
chmod 600 data/.encryption_key
```

**Warning:** Without the encryption key, all encrypted data in the database is permanently unrecoverable.

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | Nov 2026 | Major rewrite: CustomTkinter UI, SQLite database, AI integration, encryption, AppImage/Android support |
| 1.0.0 | Jul 2026 | Initial release: GTK3 file manager with basic features |
