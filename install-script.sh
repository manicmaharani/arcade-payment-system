#!/bin/bash
# Arcade Payment System - Installation Script
# Run this script to install the complete system

# Configuration
ARCADE_DIR="/home/pi/arcade"
RETROPIE_CONFIG="/opt/retropie/configs/all"
RUNCOMMAND_SCRIPT="$RETROPIE_CONFIG/runcommand-onstart.sh"

# Create directories
echo "Creating directories..."
mkdir -p "$ARCADE_DIR/logs"

# Install dependencies
echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk python3-pygame

# Make scripts executable
echo "Setting permissions..."
chmod +x "$ARCADE_DIR/validation_screen.py"
chmod +x "$ARCADE_DIR/time_tracker.py"

# Backup existing runcommand script if it exists
if [ -f "$RUNCOMMAND_SCRIPT" ]; then
    echo "Backing up existing runcommand-onstart.sh..."
    cp "$RUNCOMMAND_SCRIPT" "$RUNCOMMAND_SCRIPT.bak"
fi

# Create runcommand hook
echo "Installing runcommand hook..."
cp "$ARCADE_DIR/runcommand-onstart.sh" "$RUNCOMMAND_SCRIPT"

# Make runcommand hook executable
chmod +x "$RUNCOMMAND_SCRIPT"

echo "Installation complete!"
echo "The arcade payment system has been installed."
echo "Test the system by launching a game in RetroPie."
