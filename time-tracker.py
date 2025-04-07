#!/usr/bin/env python3
"""
Arcade Payment System - Time Tracker
Monitors game processes and terminates them after time limit
"""
import sys
import os
import time
import signal
import logging
from datetime import datetime

# Configure logging
LOG_FILE = "/home/pi/arcade/logs/time_tracker.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(message)s')

def track_game_time(pid, game_name, minutes):
    """Track a game and terminate it after specified time"""
    logging.info(f"Started tracking {game_name} (PID: {pid}) for {minutes} minutes")
    
    end_time = time.time() + (minutes * 60)
    
    try:
        # Monitor the game
        while time.time() < end_time:
            # Check if process still exists
            try:
                os.kill(int(pid), 0)  # Signal 0 tests if process exists
            except OSError:
                # Game already closed
                logging.info(f"Game {game_name} closed before time limit")
                return
                
            # Wait 10 seconds before checking again
            time.sleep(10)
            
        # Time's up - terminate the game
        logging.info(f"Time expired for {game_name}, terminating")
        try:
            # First try a graceful termination
            os.kill(int(pid), signal.SIGTERM)
            
            # Wait a moment to let it close
            time.sleep(2)
            
            # Check if it's still running
            try:
                os.kill(int(pid), 0)
                # If we get here, process still exists, force kill
                os.kill(int(pid), signal.SIGKILL)
                logging.info(f"Force killed {game_name}")
            except OSError:
                # Process already terminated
                pass
                
        except Exception as e:
            logging.error(f"Error terminating game: {e}")
            
    except Exception as e:
        logging.error(f"Time tracking error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python time_tracker.py <pid> <game_name> <minutes>")
        sys.exit(1)
        
    pid = sys.argv[1]
    game_name = sys.argv[2]
    minutes = int(sys.argv[3])
    
    track_game_time(pid, game_name, minutes)
