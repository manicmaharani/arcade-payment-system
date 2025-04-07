# Arcade Payment System
## System Overview

The system consists of two main components:

1. **Code Validation Screen**: Intercepts game launches and requires code entry
2. **Time Tracking System**: Monitors gameplay and enforces time limits

# Project Structure

/home/pi/
├── arcade/
│   ├── codes.json               # Demo code database
│   ├── logs/                    # Log directory
│   ├── validation_screen.py     # Code entry UI
│   ├── time_tracker.py          # Time limit enforcement
│   └── install.sh               # Installation script
└── .bashrc                      # Modified to run setup


validation_screen.py - The main validation screen UI with joystick input handling \
time_tracker.py - Time tracking script that enforces game time limits \
runcommand-onstart.sh - RetroPie integration hook script \
codes.json - Sample codes database with demo codes \
install.sh - Installation script \


# we need to go through these docs for the runcommand script: https://retropie.org.uk/docs/Runcommand/


Player selects Pac-Man
  → EmulationStation calls runcommand.sh
    → runcommand.sh executes our runcommand-onstart.sh
      → Our script launches validation_screen.py with "Pac-Man" parameter
        → Player enters the code sequence with joystick/buttons
          → If correct: Game launches + time tracking begins
          → If incorrect: Back to game selection


