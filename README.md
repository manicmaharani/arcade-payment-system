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
