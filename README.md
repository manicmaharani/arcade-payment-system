# Arcade Payment System
System Components:

Code Validation Screen: Python script using Pygame for input
RunCommand Hook: Intercepts game launches
Time Tracking: Monitors gameplay and enforces time limits
Code Database: Stores demo codes for testing

# Project Structure
/home/pi/
├── arcade/
│   ├── codes.json               # Demo code database
│   ├── logs/                    # Log directory
│   ├── validation_screen.py     # Code entry UI
│   ├── time_tracker.py          # Time limit enforcement
│   └── install.sh               # Installation script
└── .bashrc                      # Modified to run setup


validation_screen.py - The main validation screen UI with joystick input handling
time_tracker.py - Time tracking script that enforces game time limits
runcommand-onstart.sh - RetroPie integration hook script
codes.json - Sample codes database with demo codes
install.sh - Installation script


# we need to go through these docs for the runcommand script: https://retropie.org.uk/docs/Runcommand/


Player selects Pac-Man
  → EmulationStation calls runcommand.sh
    → runcommand.sh executes our runcommand-onstart.sh
      → Our script launches validation_screen.py with "Pac-Man" parameter
        → Player enters the code sequence with joystick/buttons
          → If correct: Game launches + time tracking begins
          → If incorrect: Back to game selection
