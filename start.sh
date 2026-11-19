#!/bin/bash
# Script to start the File Manager Application

echo "Setting up environment..."
cd /home/janitor/file_manager_app
source venv/bin/activate

echo "Starting Kali Linux File Manager Application..."
echo "Note: This application requires a graphical display."
echo "If you're running this over SSH, make sure to forward X11 (ssh -X) or use VNC."
echo ""
echo "Application features:"
echo "- File browser with folder selection"
echo "- Duplicate file detection (SHA-256)"
echo "- ClamAV virus scanning"
echo "- USB device detection and scanning"
echo "- AI integration placeholder (ready for Ollama/LLM connection)"
echo "- File sharing placeholders (Samba/ADB)"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application
python3 file_manager_app.py