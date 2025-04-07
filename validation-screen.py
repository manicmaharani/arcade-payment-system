#!/usr/bin/env python3
"""
Arcade Payment System - Code Validation Screen
Handles Konami-style code validation with joystick input
"""
import os
import sys
import json
import time
import pygame
import tkinter as tk
from tkinter import font
from datetime import datetime

# Configuration
CONFIG = {
    "fullscreen": True,          # Run in fullscreen mode
    "timeout": 60,               # Seconds to enter code
    "database": "/home/pi/arcade/codes.json"  # Demo code database
}

# Color definitions
COLORS = {
    "UP": "#ff0055",      # Pink
    "DOWN": "#00ffaa",    # Cyan
    "LEFT": "#00ffaa",    # Cyan
    "RIGHT": "#ffff00",   # Yellow
    "A": "#ff0055",       # Pink
    "B": "#00ffaa",       # Cyan
    "X": "#ffff00",       # Yellow
    "Y": "#ffffff",       # White
    "background": "#000000",  # Black
    "text": "#ffffff",    # White
    "highlight": "#6f42c1",  # Purple
    "correct": "#00ff00", # Green
    "incorrect": "#ff0000"  # Red
}

class ValidationScreen:
    """Code validation screen with joystick input handling"""
    
    def __init__(self, root, game_name):
        """Initialize the validation screen"""
        self.root = root
        self.game_name = game_name
        self.time_remaining = CONFIG["timeout"]
        self.timer_id = None
        self.poll_id = None
        self.expected_sequence = []
        self.user_sequence = []
        self.entry_complete = False
        self.validation_result = False
        self.last_input_time = 0  # For debouncing
        
        # Initialize pygame for joystick input
        pygame.init()
        pygame.joystick.init()
        
        # Set up joystick
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Found joystick: {self.joystick.get_name()}")
        else:
            print("No joystick detected!")
            
        # Load demo code
        self.load_code()
            
        # Build the UI
        self.setup_ui()
        
        # Start input polling and timer
        self.poll_id = self.root.after(50, self.poll_input)
        self.timer_id = self.root.after(1000, self.update_timer)
        
    def load_code(self):
        """Load a code from the demo database"""
        try:
            if os.path.exists(CONFIG["database"]):
                with open(CONFIG["database"], 'r') as f:
                    codes = json.load(f)
                    
                # Find a code for this game
                for code in codes:
                    if code.get("game") == self.game_name and not code.get("used", False):
                        # Check if code is expired
                        if "expires_at" not in code or code["expires_at"] > time.time():
                            self.expected_sequence = code.get("sequence", [])
                            break
            
            # If no valid code found or no database exists, use a demo code
            if not self.expected_sequence:
                print("Using demo code")
                self.expected_sequence = ["UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT"]
                
        except Exception as e:
            print(f"Error loading code: {e}")
            # Use a fallback code
            self.expected_sequence = ["UP", "UP", "DOWN", "DOWN", "LEFT", "RIGHT", "LEFT", "RIGHT"]
    
    def setup_ui(self):
        """Create the user interface"""
        # Configure window
        self.root.title(f"Enter Code for {self.game_name}")
        self.root.configure(bg=COLORS["background"])
        self.root.geometry("800x480")  # Standard RetroPie resolution
        
        if CONFIG["fullscreen"]:
            self.root.attributes("-fullscreen", True)
        
        # Title
        title_font = font.Font(family="Arial", size=32, weight="bold")
        self.title = tk.Label(
            self.root,
            text=self.game_name,
            fg=COLORS["highlight"],
            bg=COLORS["background"],
            font=title_font
        )
        self.title.pack(pady=(20, 5))
        
        # Instructions
        instruction_font = font.Font(family="Arial", size=16)
        self.instruction = tk.Label(
            self.root,
            text="ENTER SECRET CODE TO PLAY",
            fg=COLORS["UP"],
            bg=COLORS["background"],
            font=instruction_font
        )
        self.instruction.pack(pady=(0, 20))
        
        # Code display frame
        self.code_frame = tk.Frame(
            self.root,
            bg=COLORS["background"],
            highlightbackground=COLORS["highlight"],
            highlightthickness=2,
            bd=0
        )
        self.code_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # Code display label
        code_label = tk.Label(
            self.code_frame,
            text="ENTER THIS SEQUENCE:",
            fg=COLORS["text"],
            bg=COLORS["background"],
            font=font.Font(family="Arial", size=12)
        )
        code_label.pack(pady=(10, 5))
        
        # Code sequence display
        self.sequence_frame = tk.Frame(
            self.code_frame,
            bg=COLORS["background"]
        )
        self.sequence_frame.pack(pady=(5, 15))
        
        # Display the code sequence
        for move in self.expected_sequence:
            self.create_move_icon(self.sequence_frame, move)
        
        # User input frame
        self.input_frame = tk.Frame(
            self.root,
            bg=COLORS["background"],
            highlightbackground=COLORS["highlight"],
            highlightthickness=2,
            bd=0
        )
        self.input_frame.pack(fill=tk.X, padx=50, pady=(0, 20))
        
        # User input label
        input_label = tk.Label(
            self.input_frame,
            text="YOUR INPUT:",
            fg=COLORS["text"],
            bg=COLORS["background"],
            font=font.Font(family="Arial", size=12)
        )
        input_label.pack(pady=(10, 5))
        
        # User input display
        self.input_container = tk.Frame(
            self.input_frame,
            bg=COLORS["background"]
        )
        self.input_container.pack(pady=(5, 15))
        
        # Create empty slots for user input
        self.input_slots = []
        for _ in range(len(self.expected_sequence)):
            slot = tk.Canvas(
                self.input_container,
                width=40,
                height=40,
                bg=COLORS["background"],
                highlightbackground=COLORS["text"],
                highlightthickness=1
            )
            # Draw dashed circle
            slot.create_oval(5, 5, 35, 35, outline=COLORS["text"], dash=(3, 3))
            slot.pack(side=tk.LEFT, padx=5)
            self.input_slots.append(slot)
        
        # Status message
        self.status = tk.Label(
            self.root,
            text="ENTER FIRST MOVE...",
            fg=COLORS["text"],
            bg=COLORS["background"],
            font=font.Font(family="Arial", size=14)
        )
        self.status.pack(pady=(0, 15))
        
        # Timer bar
        timer_frame = tk.Frame(self.root, bg=COLORS["background"])
        timer_frame.pack(fill=tk.X, padx=100, pady=(0, 15))
        
        self.timer_canvas = tk.Canvas(
            timer_frame,
            width=600,
            height=20,
            bg=COLORS["background"],
            highlightbackground=COLORS["text"],
            highlightthickness=1
        )
        self.timer_canvas.pack()
        
        self.timer_bar = self.timer_canvas.create_rectangle(
            0, 0, 600, 20,
            fill=COLORS["highlight"]
        )
        
        self.timer_label = tk.Label(
            timer_frame,
            text=f"TIME REMAINING: {self.time_remaining} SEC",
            fg=COLORS["text"],
            bg=COLORS["background"],
            font=font.Font(family="Arial", size=10)
        )
        self.timer_label.pack(pady=(5, 0))
        
        # Help text
        help_text = tk.Label(
            self.root,
            text="USE JOYSTICK AND BUTTONS TO ENTER CODE",
            fg="#aaaaaa",
            bg=COLORS["background"],
            font=font.Font(family="Arial", size=10)
        )
        help_text.pack(side=tk.BOTTOM, pady=15)
        
        # Key bindings for keyboard fallback/testing
        self.root.bind("<Up>", lambda e: self.handle_input("UP"))
        self.root.bind("<Down>", lambda e: self.handle_input("DOWN"))
        self.root.bind("<Left>", lambda e: self.handle_input("LEFT"))
        self.root.bind("<Right>", lambda e: self.handle_input("RIGHT"))
        self.root.bind("a", lambda e: self.handle_input("A"))
        self.root.bind("b", lambda e: self.handle_input("B"))
        self.root.bind("x", lambda e: self.handle_input("X"))
        self.root.bind("y", lambda e: self.handle_input("Y"))
        self.root.bind("<Escape>", lambda e: self.cancel())
    
    def create_move_icon(self, parent, move):
        """Create an icon representing a move"""
        color = COLORS.get(move, COLORS["text"])
        
        # Create canvas for the icon
        icon = tk.Canvas(
            parent,
            width=40,
            height=40,
            bg=COLORS["background"],
            highlightthickness=0
        )
        
        # Draw the appropriate shape based on the move
        if move == "UP":
            icon.create_polygon(10, 30, 20, 10, 30, 30, fill=color)
            icon.create_rectangle(15, 30, 25, 35, fill=color)
        elif move == "DOWN":
            icon.create_polygon(10, 10, 20, 30, 30, 10, fill=color)
            icon.create_rectangle(15, 5, 25, 10, fill=color)
        elif move == "LEFT":
            icon.create_polygon(30, 10, 10, 20, 30, 30, fill=color)
            icon.create_rectangle(30, 15, 35, 25, fill=color)
        elif move == "RIGHT":
            icon.create_polygon(10, 10, 30, 20, 10, 30, fill=color)
            icon.create_rectangle(5, 15, 10, 25, fill=color)
        else:  # Button
            icon.create_oval(5, 5, 35, 35, fill=color, outline=COLORS["text"], width=2)
            icon.create_text(20, 20, text=move, fill=COLORS["text"])
        
        icon.pack(side=tk.LEFT, padx=5)
        return icon
    
    def poll_input(self):
        """Poll for joystick input"""
        if self.joystick and not self.entry_complete:
            # Process pygame events
            pygame.event.pump()
            
            # Check joystick position (with dead zone)
            x_axis = self.joystick.get_axis(0)
            y_axis = self.joystick.get_axis(1)
            
            # Use a threshold to avoid accidental inputs
            if y_axis < -0.7:  # UP
                self.handle_input("UP")
            elif y_axis > 0.7:  # DOWN
                self.handle_input("DOWN")
            elif x_axis < -0.7:  # LEFT
                self.handle_input("LEFT")
            elif x_axis > 0.7:  # RIGHT
                self.handle_input("RIGHT")
            
            # Check buttons
            for i, btn in enumerate(["A", "B", "X", "Y"]):
                if i < self.joystick.get_numbuttons() and self.joystick.get_button(i):
                    self.handle_input(btn)
        
        # Schedule next poll if not complete
        if not self.entry_complete:
            self.poll_id = self.root.after(50, self.poll_input)
    
    def handle_input(self, move):
        """Handle user input of a move"""
        # Ignore if entry is complete or input is full
        if self.entry_complete or len(self.user_sequence) >= len(self.expected_sequence):
            return
        
        # Simple debounce to prevent multiple inputs
        current_time = time.time()
        if current_time - self.last_input_time < 0.3:
            return
        
        self.last_input_time = current_time
        
        # Add the move
        self.user_sequence.append(move)
        
        # Update display
        self.update_user_input()
        
        # Check if sequence is complete
        if len(self.user_sequence) == len(self.expected_sequence):
            self.entry_complete = True
            self.validate_sequence()
        else:
            # Update status for next input
            next_idx = len(self.user_sequence) + 1
            total = len(self.expected_sequence)
            self.status.config(text=f"ENTER NEXT MOVE ({next_idx}/{total})")
    
    def update_user_input(self):
        """Update the display of user input"""
        for i, move in enumerate(self.user_sequence):
            # Get the slot canvas
            slot = self.input_slots[i]
            
            # Clear the slot
            slot.delete("all")
            
            # Get color for this move
            color = COLORS.get(move, COLORS["text"])
            
            # Draw the appropriate shape based on the move
            if move == "UP":
                slot.create_polygon(10, 30, 20, 10, 30, 30, fill=color)
                slot.create_rectangle(15, 30, 25, 35, fill=color)
            elif move == "DOWN":
                slot.create_polygon(10, 10, 20, 30, 30, 10, fill=color)
                slot.create_rectangle(15, 5, 25, 10, fill=color)
            elif move == "LEFT":
                slot.create_polygon(30, 10, 10, 20, 30, 30, fill=color)
                slot.create_rectangle(30, 15, 35, 25, fill=color)
            elif move == "RIGHT":
                slot.create_polygon(10, 10, 30, 20, 10, 30, fill=color)
                slot.create_rectangle(5, 15, 10, 25, fill=color)
            else:  # Button
                slot.create_oval(5, 5, 35, 35, fill=color, outline=COLORS["text"], width=2)
                slot.create_text(20, 20, text=move, fill=COLORS["text"])
            
            # Add indicator for correct/incorrect
            is_correct = (i < len(self.expected_sequence) and move == self.expected_sequence[i])
            indicator_color = COLORS["correct"] if is_correct else COLORS["incorrect"]
            slot.create_oval(15, 35, 25, 45, fill=indicator_color)
        
        # Highlight the current position if not complete
        if len(self.user_sequence) < len(self.expected_sequence):
            current_idx = len(self.user_sequence)
            self.input_slots[current_idx].create_oval(
                0, 0, 40, 40,
                outline=COLORS["highlight"],
                width=2,
                dash=(5, 3)
            )
    
    def validate_sequence(self):
        """Check if the entered sequence matches the expected one"""
        is_valid = (self.user_sequence == self.expected_sequence)
        
        if is_valid:
            self.validation_result = True
            self.mark_code_used()
            self.status.config(text="CODE CORRECT! LAUNCHING GAME...", fg=COLORS["correct"])
            self.root.after(2000, self.success)
        else:
            self.status.config(text="INCORRECT CODE! TRY AGAIN.", fg=COLORS["incorrect"])
            self.root.after(2000, self.reset_input)
    
    def mark_code_used(self):
        """Mark the code as used in the database"""
        try:
            if os.path.exists(CONFIG["database"]):
                with open(CONFIG["database"], 'r') as f:
                    codes = json.load(f)
                
                # Find and mark the code
                for code in codes:
                    if code.get("game") == self.game_name and code.get("sequence") == self.expected_sequence:
                        code["used"] = True
                        code["used_at"] = int(time.time())
                        break
                
                # Write back to database
                with open(CONFIG["database"], 'w') as f:
                    json.dump(codes, f, indent=2)
        except Exception as e:
            print(f"Error marking code as used: {e}")
    
    def reset_input(self):
        """Reset the user input for another try"""
        self.user_sequence = []
        self.entry_complete = False
        
        # Clear input slots
        for slot in self.input_slots:
            slot.delete("all")
            slot.create_oval(5, 5, 35, 35, outline=COLORS["text"], dash=(3, 3))
        
        self.status.config(text="ENTER FIRST MOVE...", fg=COLORS["text"])
        
        # Restart input polling if needed
        if not self.poll_id:
            self.poll_id = self.root.after(50, self.poll_input)
    
    def update_timer(self):
        """Update the countdown timer"""
        self.time_remaining -= 1
        
        # Update display
        self.timer_label.config(text=f"TIME REMAINING: {self.time_remaining} SEC")
        
        # Update timer bar
        progress = self.time_remaining / CONFIG["timeout"]
        bar_width = int(600 * progress)
        self.timer_canvas.coords(self.timer_bar, 0, 0, bar_width, 20)
        
        # Check if time's up
        if self.time_remaining <= 0:
            self.entry_complete = True
            self.status.config(text="TIME'S UP! CODE EXPIRED.", fg=COLORS["incorrect"])
            self.root.after(2000, self.cancel)
            return
        
        # Schedule next update if not complete
        if not self.entry_complete:
            self.timer_id = self.root.after(1000, self.update_timer)
    
    def success(self):
        """Close with success"""
        self.cleanup()
        self.root.destroy()
        sys.exit(0)  # Exit with success code
    
    def cancel(self):
        """Cancel and exit"""
        self.cleanup()
        self.root.destroy()
        sys.exit(1)  # Exit with error code
    
    def cleanup(self):
        """Clean up resources"""
        # Cancel any pending timers
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        if self.poll_id:
            self.root.after_cancel(self.poll_id)
        
        # Clean up pygame
        if pygame.joystick.get_count() > 0:
            pygame.joystick.quit()
        pygame.quit()

def main():
    """Main entry point"""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python validation_screen.py <game_name>")
        sys.exit(1)
    
    game_name = sys.argv[1]
    
    # Create and run the validation screen
    root = tk.Tk()
    app = ValidationScreen(root, game_name)
    root.mainloop()

if __name__ == "__main__":
    main()
