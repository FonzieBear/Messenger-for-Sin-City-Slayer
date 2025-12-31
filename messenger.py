import random
import datetime
import sys
import json
import os
import base64
import getpass
from itertools import cycle

# ANSI Color Codes for Terminal Output
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[31m',      # Burgundy, Scarlet
    'GREEN': '\033[32m',    # Jade
    'YELLOW': '\033[33m',   # Golden, Olive
    'BLUE': '\033[34m',     # Cerulean, Indigo
    'MAGENTA': '\033[35m',  # Plum
    'CYAN': '\033[36m',     # Cyan, Mint
    'WHITE': '\033[37m',    # White
    'GREY': '\033[90m',     # Pewter, Gray, Black
    'BRIGHT_RED': '\033[91m', # Coral, Peach
    'BRIGHT_YELLOW': '\033[93m' # Lemon
}

# Mapping specific users to colors
USER_COLORS = {
    "Adair Burgundy": COLORS['RED'],
    "Alex Jade": COLORS['GREEN'],
    "Blue Coral": COLORS['BRIGHT_RED'],
    "Cricket Pewter": COLORS['GREY'],
    "Darby Cerulean": COLORS['BLUE'],
    "Dracen Gray": COLORS['GREY'],
    "Greenlee Black": COLORS['GREY'], 
    "Jude Plum": COLORS['MAGENTA'],
    "Lee Mint": COLORS['CYAN'],
    "Parson Golden": COLORS['YELLOW'],
    "Piper White": COLORS['WHITE'],
    "Ren Peach": COLORS['BRIGHT_RED'],
    "Rigny Cyan": COLORS['CYAN'],
    "Shan Lemon": COLORS['BRIGHT_YELLOW'],
    "Story Indigo": COLORS['BLUE'],
    "Waverly Scarlet": COLORS['RED'],
    "Whitney Whatley": COLORS['WHITE'],
    "Winter Olive": COLORS['YELLOW']
}

# The List: Alphabetized by First Name
USER_ORDER = [
    "Adair Burgundy",
    "Alex Jade",
    "Blue Coral",
    "Cricket Pewter",
    "Darby Cerulean",
    "Dracen Gray",
    "Greenlee Black",
    "Jude Plum",
    "Lee Mint",
    "Parson Golden",
    "Piper White",
    "Ren Peach",
    "Rigny Cyan",
    "Shan Lemon",
    "Story Indigo",
    "Waverly Scarlet",
    "Whitney Whatley",
    "Winter Olive"
]

class SecureMessagingSystem:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.filename = "messaging_data_secure.json"
        
        self._clear_screen()
        
        # Use getpass for secure, invisible input
        print("🔐 SYSTEM LOCKED")
        try:
            self.master_pin = getpass.getpass("Enter MASTER PIN to unlock (Typing will be invisible): ").strip()
        except Exception:
            self.master_pin = input("Enter MASTER PIN (Warning: Visible): ").strip()

        self._clear_screen()
        
        if not self.master_pin:
            print("❌ Master PIN cannot be empty. Exiting.")
            sys.exit()

        if os.path.exists(self.filename):
            success = self.load_data()
            if not success:
                print("❌ Failed to decrypt. Wrong Master PIN or corrupted file.")
                sys.exit()
        else:
            print(f"🆕 Creating new system encrypted with Master PIN.")
            self._initialize_users()

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _xor_cipher(self, text, key):
        return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(text, cycle(key)))

    def _colorize(self, text, color_code):
        return f"{color_code}{text}{COLORS['RESET']}"

    def get_user_color(self, username):
        return USER_COLORS.get(username, COLORS['WHITE'])

    def save_data(self):
        try:
            json_str = json.dumps(self.users)
            encrypted_str = self._xor_cipher(json_str, self.master_pin)
            b64_encoded = base64.b64encode(encrypted_str.encode()).decode()

            with open(self.filename, 'w') as f:
                f.write(b64_encoded)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                file_content = f.read()

            encrypted_str = base64.b64decode(file_content).decode()
            json_str = self._xor_cipher(encrypted_str, self.master_pin)
            self.users = json.loads(json_str)
            
            # Ensure hardcoded users exist AND have game data
            for name in USER_ORDER:
                if name not in self.users:
                    self.users[name] = {
                        'pin': f"{random.randint(0, 9999):04d}", 
                        'inbox': [],
                        'games_played': 0,
                        'high_score': 0
                    }
                else:
                    # Migration: Add game fields to existing users if missing
                    if 'games_played' not in self.users[name]:
                        self.users[name]['games_played'] = 0
                    if 'high_score' not in self.users[name]:
                        self.users[name]['high_score'] = 0
            
            print("✅ Access Granted.")
            return True

        except (json.JSONDecodeError, UnicodeDecodeError, Exception):
            return False

    def _initialize_users(self):
        print("--- FIRST RUN: GENERATING PINS ---")
        used_pins = set()
        
        for name in USER_ORDER:
            while True:
                pin = f"{random.randint(0, 9999):04d}"
                if pin not in used_pins:
                    used_pins.add(pin)
                    break
            
            self.users[name] = {
                'pin': pin,
                'inbox': [],
                'games_played': 0,
                'high_score': 0
            }
            
            color = self.get_user_color(name)
            print(f"Generated {self._colorize(name, color)}: {pin}")
        
        self.save_data()
        input("\nInitial setup complete. Write these down! Press Enter to continue...")
        self._clear_screen()

    def print_directory(self, show_pins=False):
        title = "ADMIN USER DIRECTORY (WITH PINS)" if show_pins else "USER DIRECTORY"
        print(f"\n--- {title} ---")
        
        if show_pins:
            print(f"{'#':<3} | {'USER':<25} | {'PIN':<6}")
            print("-" * 40)
            for idx, name in enumerate(USER_ORDER, 1):
                color = self.get_user_color(name)
                pin = self.users[name]['pin']
                print(f"{idx:<3} | {self._colorize(name, color):<35} | {pin:<6}")
        else:
            print(f"{'#':<3} | {'USER':<25}")
            print("-" * 30)
            for idx, name in enumerate(USER_ORDER, 1):
                color = self.get_user_color(name)
                print(f"{idx:<3} | {self._colorize(name, color):<35}")
            
        print("-" * 30)

    def login(self):
        print("\n--- LOGIN ---")
        try:
            pin = getpass.getpass("Enter your PIN (Typing will be invisible): ").strip()
        except Exception:
            pin = input("Enter your PIN: ").strip()
        
        if pin == self.master_pin:
            self._clear_screen()
            self.current_user = "ADMIN"
            print(f"✅ {COLORS['RED']}ADMIN ACCESS GRANTED.{COLORS['RESET']}")
            return

        found_user = None
        for user, data in self.users.items():
            if data['pin'] == pin:
                found_user = user
                break
        
        if found_user:
            self.current_user = found_user
            self._clear_screen()
            color = self.get_user_color(found_user)
            print(f"✅ Login successful! Welcome, {self._colorize(found_user, color)}.")
        else:
            print("❌ Invalid PIN.")

    def logout(self):
        self.current_user = None
        self._clear_screen()
        print("Logged out successfully.")

    def send_message(self):
        self.print_directory(show_pins=False)

        print("\n--- SEND MESSAGE ---")
        try:
            choice = input("Enter Recipient Number (1-18): ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(USER_ORDER):
                raise ValueError
            recipient_name = USER_ORDER[idx]
        except ValueError:
            print("❌ Invalid number.")
            return

        if self.current_user != "ADMIN" and recipient_name == self.current_user:
            print("⚠️ You cannot send messages to yourself.")
            return

        message_text = input(f"Message for {self._colorize(recipient_name, self.get_user_color(recipient_name))}: ").strip()
        if not message_text:
            print("⚠️ Cannot send an empty message.")
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        if self.current_user == "ADMIN":
            sender_display = f"{COLORS['RED']}ADMIN{COLORS['RESET']}"
        else:
            sender_display = self._colorize(self.current_user, self.get_user_color(self.current_user))

        formatted_message = f"[{timestamp}] From {sender_display}: {message_text}"
        
        self.users[recipient_name]['inbox'].append(formatted_message)
        self.save_data() 
        print(f"✅ Message sent to {recipient_name}.")

    def broadcast_message(self):
        print("\n--- BROADCAST MESSAGE ---")
        message_text = input("Enter message for ALL users: ").strip()
        if not message_text:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] *** {COLORS['RED']}BROADCAST FROM ADMIN{COLORS['RESET']} ***: {message_text}"

        for user in self.users:
            self.users[user]['inbox'].append(formatted_message)
        
        self.save_data()
        print(f"✅ Broadcast sent to {len(self.users)} users.")

    def clear_single_inbox(self):
        self.print_directory(show_pins=False)
        print("\n--- CLEAR USER INBOX ---")
        try:
            choice = input("Enter User Number to wipe (1-18): ").strip()
            idx = int(choice) - 1
            if idx < 0 or idx >= len(USER_ORDER):
                raise ValueError
            target_user = USER_ORDER[idx]
        except ValueError:
            print("❌ Invalid number.")
            return

        confirm = input(f"Are you sure you want to delete ALL messages for {target_user}? (y/n): ").lower()
        if confirm == 'y':
            self.users[target_user]['inbox'] = []
            self.save_data()
            print(f"✅ Inbox cleared for {target_user}.")
        else:
            print("❌ Action cancelled.")

    def clear_all_inboxes(self):
        print(f"\n--- {COLORS['RED']}DANGER: CLEAR ALL INBOXES{COLORS['RESET']} ---")
        confirm = input("Are you sure you want to delete EVERY message for ALL users? (y/n): ").lower()
        if confirm == 'y':
            for user in self.users:
                self.users[user]['inbox'] = []
            self.save_data()
            print(f"✅ {COLORS['RED']}ALL SYSTEM MESSAGES HAVE BEEN WIPED.{COLORS['RESET']}")
        else:
            print("❌ Action cancelled.")

    def view_inbox(self):
        color = self.get_user_color(self.current_user)
        print(f"\n--- INBOX FOR {self._colorize(self.current_user, color)} ---")
        inbox = self.users[self.current_user]['inbox']

        if not inbox:
            print("(No messages)")
        else:
            for msg in inbox:
                print(msg)
        input("\nPress Enter to return to menu...")

    def admin_view_all_inboxes(self):
        print(f"\n--- GLOBAL INBOX VIEWER ---")
        for name in USER_ORDER:
            inbox = self.users[name]['inbox']
            color = self.get_user_color(name)
            print(f"\n[{self._colorize(name, color)}] ({len(inbox)} messages)")
            if not inbox:
                print("  (Empty)")
            else:
                for msg in inbox:
                    print(f"  {msg}")
        input("\nPress Enter to return to menu...")

    # ==========================
    #  GAME LOGIC: CODE BREAKER
    # ==========================
    def play_code_breaker(self):
        user_data = self.users[self.current_user]
        
        # Check Limits - UPDATED TO 5
        MAX_GAMES = 5
        if user_data['games_played'] >= MAX_GAMES:
            print(f"\n🚫 {COLORS['RED']}MAXIMUM ATTEMPTS REACHED{COLORS['RESET']}")
            print(f"You have already played {MAX_GAMES} times.")
            print(f"Your High Score: {user_data['high_score']}")
            input("Press Enter to return...")
            return

        self._clear_screen()
        print(f"\n=== 🕵️‍♂️ {COLORS['CYAN']}CODE BREAKER MINIGAME{COLORS['RESET']} ===")
        print("Deduce the secret 4-digit code (0-9).")
        print("Feedback Legend:")
        print(f"  - {COLORS['GREEN']}Exact Match{COLORS['RESET']}: Correct number, Correct spot.")
        print(f"  - {COLORS['YELLOW']}Partial Match{COLORS['RESET']}: Correct number, Wrong spot.")
        print("\nAttempts Allowed: 10")
        input("Press Enter to START...")

        # Generate Secret (4 random digits)
        secret_code = [str(random.randint(0, 9)) for _ in range(4)]
        
        attempts = 0
        max_attempts = 10
        score = 0
        
        while attempts < max_attempts:
            print(f"\nAttempt {attempts + 1}/{max_attempts}")
            guess_str = input("Enter 4 digits: ").strip()

            # Validation
            if len(guess_str) != 4 or not guess_str.isdigit():
                print("⚠️ Invalid input. Must be exactly 4 digits.")
                continue

            attempts += 1
            guess = list(guess_str)

            # Calculate Exact Matches (Bulls)
            exact_matches = 0
            temp_secret = []
            temp_guess = []

            for s, g in zip(secret_code, guess):
                if s == g:
                    exact_matches += 1
                else:
                    temp_secret.append(s)
                    temp_guess.append(g)

            # Calculate Partial Matches (Cows)
            partial_matches = 0
            for g in temp_guess:
                if g in temp_secret:
                    partial_matches += 1
                    temp_secret.remove(g)  # Remove to prevent double counting

            # Display Feedback
            print(f"   Feedback: {COLORS['GREEN']}{exact_matches} Exact{COLORS['RESET']} | {COLORS['YELLOW']}{partial_matches} Partial{COLORS['RESET']}")

            # Win Condition
            if exact_matches == 4:
                score = (11 - attempts) * 100
                print(f"\n🎉 {COLORS['GREEN']}CODE BROKEN!{COLORS['RESET']}")
                print(f"You solved it in {attempts} attempts.")
                print(f"Score: {score}")
                break
        else:
            print(f"\n☠️ {COLORS['RED']}MISSION FAILED{COLORS['RESET']}")
            print(f"The code was: {''.join(secret_code)}")
            score = 0

        # Save Results
        user_data['games_played'] += 1
        if score > user_data['high_score']:
            user_data['high_score'] = score
            print(f"🏆 {COLORS['YELLOW']}NEW HIGH SCORE!{COLORS['RESET']}")
        
        self.save_data()
        input("\nPress Enter to return...")

    def admin_view_high_scores(self):
        print(f"\n--- 🏆 HIGH SCORE LEADERBOARD ---")
        
        # Sort users by high score (descending)
        ranked_users = sorted(
            self.users.items(), 
            key=lambda x: x[1]['high_score'], 
            reverse=True
        )

        print(f"{'RANK':<4} | {'USER':<25} | {'SCORE':<6} | {'PLAYS':<5}")
        print("-" * 50)
        
        for i, (name, data) in enumerate(ranked_users, 1):
            color = self.get_user_color(name)
            score = data['high_score']
            plays = data['games_played']
            # Updated display to show out of 5
            print(f"{i:<4} | {self._colorize(name, color):<35} | {score:<6} | {plays}/5")
        
        input("\nPress Enter to return...")

    # ==========================
    #       MAIN LOOPS
    # ==========================
    def run(self):
        while True:
            if self.current_user is None:
                print("\n=== SECURE MESSENGER ===")
                print("1. Login")
                print("2. View Directory")
                choice = input("Select option: ").strip()

                if choice == '1':
                    self.login()
                elif choice == '2':
                    self.print_directory(show_pins=False)
                else:
                    print("Invalid option.")

            elif self.current_user == "ADMIN":
                print(f"\n=== {COLORS['RED']}ADMIN DASHBOARD{COLORS['RESET']} ===")
                print("1. View User Directory (REVEAL PINS)")
                print("2. View ALL Inboxes")
                print("3. Send Message to User")
                print("4. Broadcast Message to ALL")
                print("5. Clear a User's Inbox")
                print("6. Clear ALL Inboxes")
                print(f"7. View High Scores") # Color Removed
                print("8. Logout")
                choice = input("Select option: ").strip()

                if choice == '1':
                    self.print_directory(show_pins=True)
                    input("\nPress Enter to return...")
                elif choice == '2':
                    self.admin_view_all_inboxes()
                elif choice == '3':
                    self.send_message()
                elif choice == '4':
                    self.broadcast_message()
                elif choice == '5':
                    self.clear_single_inbox()
                elif choice == '6':
                    self.clear_all_inboxes()
                elif choice == '7':
                    self.admin_view_high_scores()
                elif choice == '8':
                    self.logout()
                else:
                    print("Invalid option.")

            else:
                user_color = self.get_user_color(self.current_user)
                # Updated Logic for 5 games
                MAX_GAMES = 5
                games_left = MAX_GAMES - self.users[self.current_user]['games_played']
                
                print(f"\n=== DASHBOARD: {self._colorize(self.current_user, user_color)} ===")
                print("1. Read Inbox")
                print("2. Send Message")
                print(f"3. Play Code Breaker ({games_left} left)")
                print("4. Logout") # Moved to last
                choice = input("Select option: ").strip()

                if choice == '1':
                    self.view_inbox()
                elif choice == '2':
                    self.send_message()
                elif choice == '3':
                    self.play_code_breaker()
                elif choice == '4':
                    self.logout()
                else:
                    print("Invalid option.")

if __name__ == "__main__":
    app = SecureMessagingSystem()
    app.run()
    