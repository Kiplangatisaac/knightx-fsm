# KnightX_fsm - Kali Linux File System Management App

A modern, feature-rich file system management application for Kali Linux with an enhanced user interface, storage monitoring, and system resource visualization.

## Features

### Core Functionality
- **Modern File Explorer** - Intuitive interface with back/forward/up/home navigation
- **Duplicate File Finder** - SHA-256 based detection with size pre-filtering for efficiency
- **Integrated Virus Scanning** - ClamAV integration via pyclamd daemon or clamscan subprocess
- **USB Device Management** - Automatic detection and scanning of USB storage devices
- **Storage Usage Visualization** - Interactive pie chart showing disk usage
- **System Resource Monitoring** - Real-time CPU and memory usage graphs
- **AI Integration Ready** - Placeholder for connecting to local LLMs (Ollama, etc.)
- **File Sharing Preparation** - Framework for Samba/ADB integration

### Enhanced UI/UX
- Tabbed interface for organized workflow
- Visual storage status with interactive pie chart
- System resource monitoring with live graphs
- Modern toolbar with intuitive icons
- Status bar and activity logging
- Professional application branding with "KnightX_fsm" name

## Requirements

### System Packages
- `clamav` - Antivirus engine
- `clamav-daemon` - ClamAV daemon for faster scanning
- `clamav-freshclam` - Virus database updater
- `gir1.2-gtk-3.0` - GTK 3 GUI bindings
- `python3-gi` - Python GObject bindings
- `python3-gi-cairo` - Python Cairo bindings for GTK
- `python3-pyclamd` - Python interface to ClamAV daemon
- `python3-pyudev` - Python bindings for USB device monitoring

## Installation

1. Install required system packages:
```bash
sudo apt update
sudo apt install -y clamav clamav-daemon clamav-freshclam gir1.2-gtk-3.0 python3-gi python3-gi-cairo python3-pyclamd python3-pyudev
```

2. Update virus definitions:
```bash
sudo freshclam
```

3. Clone or copy this repository to your Kali Linux machine

4. Make the script executable:
```bash
chmod +x knightx_fsm.py
```

## Usage

Run the application:
```bash
./knightx_fsm.py
```

Or:
```bash
python3 knightx_fsm.py
```

### Application Tabs

1. **File Explorer** - Browse files and folders with navigation controls
2. **Storage** - Visual disk usage monitoring with interactive pie chart
3. **System Resources** - Real-time CPU and memory usage graphs
4. **Tools** - Access to scanning functions, duplicate finder, USB scanner, and activity log

### Key Features Usage

- **File Operations**: Use the toolbar buttons (Back, Forward, Up, Home, Refresh) to navigate
- **Path Navigation**: Enter a path in the location bar and press Enter or click "Go"
- **Duplicate Finder**: Click "Find Duplicates" in the Tools tab or use the Tools menu
- **Virus Scanning**: Select files in the file explorer and click "Scan File"
- **USB Scanning**: Click "USB Scan" to detect and scan connected USB devices
- **Storage Monitor**: View real-time disk usage in the Storage tab
- **System Resources**: Monitor CPU and memory usage in the System Resources tab
- **Activity Log**: View all operations and scan results in the Tools tab log

## Architecture

The application follows a modular design:
- Main window with notebook (tabbed) interface
- DrawingArea widgets for custom visualizations (storage pie chart, resource graphs)
- Threading for background operations to keep UI responsive
- Proper GTK signal handling for user interactions
- Extensible design for adding new features

## Customization

### AI Integration
To add actual AI functionality:
1. Modify the `ai_anomaly_score()` function in `knightx_fsm.py`
2. Connect to your preferred LLM (Ollama, LlamaCpp, etc.) via HTTP API
3. Return a risk score between 0.0 and 1.0 for each file

### File Sharing
To implement file sharing:
1. Extend the `on_share_clicked()` method
2. Add Samba sharing capabilities or ADB integration for Android devices
3. Implement file transfer protocols as needed

## Notes

- The application requires a graphical display (will not work in pure SSH without X11 forwarding)
- For best performance, ensure the ClamAV daemon is running: `sudo systemctl start clamav-freshclam`
- Virus definition updates should be run regularly: `sudo freshclam`
- The USB scanning feature requires proper permissions to access device nodes

## License

MIT License - feel free to modify and enhance for your specific needs

## Acknowledgements

- Built with Python GTK+ 3 (PyGObject)
- Uses ClamAV for antivirus scanning
- Inspired by modern file manager interfaces