#!/bin/bash
# Pi Camera Integration System - Dependency Installation Script

set -e  # Exit on error

echo "=========================================="
echo "Pi Camera Integration System"
echo "Dependency Installation"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package list
echo "Updating package list..."
sudo apt update

# Install system dependencies
echo "Installing system packages..."
sudo apt install -y \
    fswebcam \
    v4l-utils \
    python3 \
    python3-pip \
    python3-yaml

# Install Python dependencies
echo "Installing Python packages..."
pip3 install -r requirements.txt

# Check if user is in video group
if ! groups $USER | grep -q '\bvideo\b'; then
    echo ""
    echo "Adding user $USER to 'video' group for camera access..."
    sudo usermod -a -G video $USER
    echo "Note: You need to log out and log back in for group changes to take effect"
fi

# Verify fswebcam installation
echo ""
echo "Verifying fswebcam installation..."
if command -v fswebcam &> /dev/null; then
    echo "✓ fswebcam is installed: $(which fswebcam)"
else
    echo "✗ fswebcam installation failed"
    exit 1
fi

# Verify v4l2-ctl installation
echo "Verifying v4l-utils installation..."
if command -v v4l2-ctl &> /dev/null; then
    echo "✓ v4l2-ctl is installed: $(which v4l2-ctl)"
else
    echo "✗ v4l-utils installation failed"
    exit 1
fi

# List available video devices
echo ""
echo "Scanning for video devices..."
if ls /dev/video* 1> /dev/null 2>&1; then
    echo "Found video devices:"
    ls -l /dev/video*
else
    echo "Warning: No video devices found"
    echo "Make sure your camera is connected"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Connect your USB webcam"
echo "2. Run: ./scripts/run_once.sh  (for single test)"
echo "3. Run: ./scripts/start.sh     (for continuous mode)"
echo ""
