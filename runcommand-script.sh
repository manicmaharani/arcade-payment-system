#!/bin/bash
# Arcade Payment System - RunCommand Hook
# Place in /opt/retropie/configs/all/runcommand-onstart.sh

# Log file
LOG_FILE="/home/pi/arcade/logs/runcommand.log"

# Make sure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log start of script
echo "$(date) - Starting runcommand hook" >> "$LOG_FILE"

# Get game information
SYSTEM="$1"
EMULATOR="$2"
ROM="$3"
FULL_COMMAND="$4"

# Extract game name from ROM path
GAME_NAME=$(basename "$ROM" .zip)
GAME_NAME="${GAME_NAME%.*}"  # Remove file extension

# Log game launch
echo "$(date) - Game: $GAME_NAME, System: $SYSTEM, Emulator: $EMULATOR" >> "$LOG_FILE"

# Optional: Skip validation for certain games or systems
# Uncomment and modify to exclude games from validation
#if [[ "$GAME_NAME" == "Setup" || "$SYSTEM" == "ports" ]]; then
#    echo "$(date) - Skipping validation for $GAME_NAME" >> "$LOG_FILE"
#    exit 0
#fi

# Run validation screen
echo "$(date) - Running validation for $GAME_NAME" >> "$LOG_FILE"
python3 /home/pi/arcade/validation_screen.py "$GAME_NAME" 2>> "$LOG_FILE"

# Get validation result
VALIDATION_RESULT=$?

# Check validation result
if [ $VALIDATION_RESULT -ne 0 ]; then
    echo "$(date) - Validation failed for $GAME_NAME (exit code: $VALIDATION_RESULT)" >> "$LOG_FILE"
    # Return non-zero to abort game launch
    exit 1
fi

# If validation succeeded, set up time tracking in background
echo "$(date) - Validation successful, launching game with time tracking" >> "$LOG_FILE"

# Start time tracking in background
(
    # Wait for game to launch
    sleep 5
    
    # Find the PID of the emulator
    if [[ "$EMULATOR" == *retroarch* ]]; then
        # For RetroArch-based emulators
        EMULATOR_PID=$(pgrep -f "retroarch")
    else
        # For standalone emulators, try to find by emulator name
        EMULATOR_PID=$(pgrep -f "$EMULATOR")
    fi
    
    # If no PID found, try a more general approach
    if [ -z "$EMULATOR_PID" ]; then
        EMULATOR_PID=$(ps aux | grep "$ROM" | grep -v grep | awk '{print $2}' | head -n 1)
    fi
    
    # Log the emulator PID
    echo "$(date) - Emulator PID: $EMULATOR_PID" >> "$LOG_FILE"
    
    if [ -n "$EMULATOR_PID" ]; then
        # Launch time tracker with 30 minute duration
        python3 /home/pi/arcade/time_tracker.py "$EMULATOR_PID" "$GAME_NAME" 30 >> "$LOG_FILE" 2>&1
    else
        echo "$(date) - Could not find emulator process" >> "$LOG_FILE"
    fi
) &

# Continue with game launch
exit 0
