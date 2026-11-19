#!/bin/bash
# Script to launch KnightX_fsm application

echo "============================================="
echo "  KnightX_fsm - Kali Linux File System Manager"
echo "============================================="
echo ""

# Change to application directory
cd /home/janitor/file_manager_app

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if virtual environment activation succeeded
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Display application information
echo "Starting KnightX_fsm..."
echo "Features available:"
echo "  - File Explorer with navigation controls"
echo "  - Duplicate File Detection (SHA-256)"
echo "  - Virus Scanning (ClamAV integration)"
echo "  - USB Device Detection and Scanning"
echo "  - Storage Usage Visualization (Pie Chart)"
echo "  - System Resource Monitoring (CPU/Memory)"
echo "  - Activity Log"
echo "  - AI Integration Ready"
echo ""
echo "Close the application window to exit."
echo "============================================="
echo ""

# Run the application
python3 knightx_fsm.py

# Deactivate virtual environment on exit
deactivate
echo ""
echo "KnightX_fsm has been closed."