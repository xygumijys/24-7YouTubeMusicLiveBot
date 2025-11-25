#!/bin/bash

# Install FFmpeg (requires root privileges - run with sudo if needed)
echo "Installing system dependencies..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Note: This script needs root privileges to install system packages."
    echo "Please run with sudo: sudo bash install.sh"
    echo ""
    echo "Alternatively, install FFmpeg manually:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo ""
fi

# Try to install with proper error handling
if command -v apt-get &> /dev/null; then
    apt-get update || echo "Warning: Could not update package list"
    apt-get install -y ffmpeg || echo "Warning: Could not install FFmpeg via apt-get"
elif command -v yum &> /dev/null; then
    yum install -y ffmpeg || echo "Warning: Could not install FFmpeg via yum"
elif command -v brew &> /dev/null; then
    brew install ffmpeg || echo "Warning: Could not install FFmpeg via brew"
else
    echo "Package manager not found. Please install FFmpeg manually."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
