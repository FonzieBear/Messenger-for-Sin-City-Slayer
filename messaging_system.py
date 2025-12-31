# messaging_system.py
import json
import os
import sys
import random
import base64
import datetime
from config import FILENAME, USER_ORDER, COLORS, MAX_GAMES
from utils import clear_screen, get_secure_input, xor_cipher, colorize, get_user_color
from game import play_code_breaker

class SecureMessagingSystem:
    def __init__(self):
        self.users = {}
        self.current_user = None
        
        clear_screen()
        print("🔐 SYSTEM LOCKED")
        self.master_pin = get_secure_input("Enter MASTER PIN to unlock (Typing will be invisible)")
        clear_screen()
        
        if not self.master_pin:
            print("❌ Master PIN cannot be empty. Exiting.")
            sys.exit()

        if os.path.exists(FILENAME):
            if not self.load_data():
                print("❌ Failed to decrypt. Wrong Master PIN or corrupted file.")
                sys.exit()
        else:
            print(f"🆕 Creating new system encrypted with Master PIN.")
            self._initialize_users()

    def save_data(self):
        try:
            json_str = json.dumps(self.users)
            encrypted_str = xor_cipher(json_str, self.master_pin)
            b64_encoded = base64.b64encode(encrypted_str.encode()).decode()

            with open(FILENAME, 'w') as f:
                f.write(b64_encoded)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_data(self):
        try:
            with open(FILENAME, 'r') as f:
                file_content = f.read()

            encrypted_str = base64.b64decode(file_content).decode()
            json_str = xor_cipher(encrypted_str, self.master_pin)
            self.users = json.loads(json_str)
            
            # Migration/Validation check
            for name in USER_ORDER:
                if name not in self.users:
                    self.users[name] = {
                        'pin': f"{random.randint(0, 9999):04d}", 'inbox': [],
                        'games_played': 0, 'high_score': 0
                    }
                else:
                    if 'games_played' not in self.users[name]: self.users[name]['games_played'] = 0
                    if 'high_score' not in self.users[name]: self.users[name]['high_score'] = 0
            
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
                'pin': pin, 'inbox': [],
                'games_played': 0, 'high_score': 0
            }
            print(f"Generated {colorize(name, get_user_color(name))}: {pin}")
        
        self.save_data()
        input("\nInitial setup complete. Write these down! Press Enter to continue...")
        clear_screen()

    def print_directory(self, show_pins=False):
        title = "ADMIN USER DIRECTORY (WITH PINS)" if show_pins else "USER DIRECTORY"
        print(f"\n--- {title} ---")
        if show_pins:
            print(f"{'#':<3} | {'USER':<25} | {'PIN':<6}")
            print("-" * 40)
            for idx, name in enumerate(USER_ORDER, 1):
                c = get_user_color(name)
                print(f"{idx:<3} | {colorize(name, c):<35} | {self.users[name]['pin']:<6}")
        else:
            print(f"{'#':<3} | {'USER':<25}")
            print("-" * 30)
            for idx, name in enumerate(USER_ORDER, 1):
                c = get_user_color(name)
                print(f"{idx:<3} | {colorize(name, c):<35}")
        print("-" * 30)

    def login(self):
        print("\n--- LOGIN ---")
        pin = get_secure_input("Enter your PIN")
        
        if pin == self.master_pin:
            clear_screen()
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
            clear_screen()
            c = get_user_color(found_user)
            print(f"✅ Login successful! Welcome, {colorize(found_user, c)}.")
        else:
            print("❌ Invalid PIN.")

    def logout(self):
        self.current_user = None
        clear_screen()
        print("Logged out successfully.")

    def send_message(self):
        self.print_directory(show_pins=False)
        print("\n--- SEND MESSAGE ---")
        try:
            idx = int(input("Enter Recipient Number (1-18): ").strip()) - 1
            if idx < 0 or idx >= len(USER_ORDER): raise ValueError
            recipient_name = USER_ORDER[idx]
        except ValueError:
            print("❌ Invalid number.")
            return

        if self.current_user != "ADMIN" and recipient_name == self.current_user:
            print("⚠️ You cannot send messages to yourself.")
            return

        msg_text = input(f"Message for {colorize(recipient_name, get_user_color(recipient_name))}: ").strip()
        if not msg_text: return

        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if self.current_user == "ADMIN":
            sender_display = f"{COLORS['RED']}ADMIN{COLORS['RESET']}"
        else:
            sender_display = colorize(self.current_user, get_user_color(self.current_user))

        formatted = f"[{ts}] From {sender_display}: {msg_text}"
        self.users[recipient_name]['inbox'].append(formatted)
        self.save_data()
        print(f"✅ Message sent to {recipient_name}.")

    def broadcast_message(self):
        print("\n--- BROADCAST MESSAGE ---")
        msg_text = input("Enter message for ALL users: ").strip()
        if not msg_text: return
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] *** {COLORS['RED']}BROADCAST FROM ADMIN{COLORS['RESET']} ***: {msg_text}"
        for user in self.users: self.users[user]['inbox'].append(formatted)
        self.save_data()
        print(f"✅ Broadcast sent.")

    def clear_inboxes(self, mode="single"):
        if mode == "single":
            self.print_directory(show_pins=False)
            try:
                idx = int(input("Enter User Number to wipe: ").strip()) - 1
                target = USER_ORDER[idx]
            except: return
            if input(f"Delete ALL messages for {target}? (y/n): ").lower() == 'y':
                self.users[target]['inbox'] = []
                self.save_data()
                print("✅ Inbox cleared.")
        else:
            print(f"\n--- {COLORS['RED']}DANGER: CLEAR ALL INBOXES{COLORS['RESET']} ---")
            if input("Delete EVERY message for ALL users? (y/n): ").lower() == 'y':
                for u in self.users: self.users[u]['inbox'] = []
                self.save_data()
                print("✅ All messages wiped.")

    def reset_game_stats(self):
        print(f"\n--- {COLORS['RED']}DANGER: RESET LEADERBOARD{COLORS['RESET']} ---")
        print("This will reset ALL high scores to 0.")
        print("It will also give EVERY user 5 fresh attempts.")
        if input("Are you sure? (y/n): ").lower() == 'y':
            for user in self.users:
                self.users[user]['high_score'] = 0
                self.users[user]['games_played'] = 0
            self.save_data()
            print("✅ Leaderboard and play counts have been reset.")
        else:
            print("❌ Action cancelled.")

    def view_inbox(self):
        c = get_user_color(self.current_user)
        print(f"\n--- INBOX FOR {colorize(self.current_user, c)} ---")
        inbox = self.users[self.current_user]['inbox']
        if not inbox: print("(No messages)")
        else:
            for msg in inbox: print(msg)
        input("\nPress Enter to return to menu...")

    def admin_view_all_inboxes(self):
        print(f"\n--- GLOBAL INBOX VIEWER ---")
        for name in USER_ORDER:
            inbox = self.users[name]['inbox']
            c = get_user_color(name)
            print(f"\n[{colorize(name, c)}] ({len(inbox)} messages)")
            if not inbox: print("  (Empty)")
            else:
                for msg in inbox: print(f"  {msg}")
        input("\nPress Enter to return to menu...")

    def admin_view_high_scores(self):
        print(f"\n--- 🏆 HIGH SCORE LEADERBOARD ---")
        ranked = sorted(self.users.items(), key=lambda x: x[1]['high_score'], reverse=True)
        print(f"{'RANK':<4} | {'USER':<25} | {'SCORE':<6} | {'PLAYS':<5}")
        print("-" * 50)
        for i, (name, data) in enumerate(ranked, 1):
            c = get_user_color(name)
            print(f"{i:<4} | {colorize(name, c):<35} | {data['high_score']:<6} | {data['games_played']}/{MAX_GAMES}")
        input("\nPress Enter to return...")

    def run(self):
        while True:
            if self.current_user is None:
                print("\n=== SECURE MESSENGER ===")
                print("1. Login")
                print("2. View Directory")
                choice = input("Select option: ").strip()
                if choice == '1': self.login()
                elif choice == '2': self.print_directory()
                else: print("Invalid option.")
            elif self.current_user == "ADMIN":
                print(f"\n=== {COLORS['RED']}ADMIN DASHBOARD{COLORS['RESET']} ===")
                print("1. View User Directory (REVEAL PINS)")
                print("2. View ALL Inboxes")
                print("3. Send Message to User")
                print("4. Broadcast Message to ALL")
                print("5. Clear a User's Inbox")
                print("6. Clear ALL Inboxes")
                print("7. View High Scores")
                print("8. Reset Game Data (Scores & Plays)")
                print("9. Logout")
                choice = input("Select option: ").strip()
                if choice == '1': self.print_directory(True); input("Press Enter...")
                elif choice == '2': self.admin_view_all_inboxes()
                elif choice == '3': self.send_message()
                elif choice == '4': self.broadcast_message()
                elif choice == '5': self.clear_inboxes("single")
                elif choice == '6': self.clear_inboxes("all")
                elif choice == '7': self.admin_view_high_scores()
                elif choice == '8': self.reset_game_stats()
                elif choice == '9': self.logout()
            else:
                c = get_user_color(self.current_user)
                games_left = MAX_GAMES - self.users[self.current_user]['games_played']
                print(f"\n=== DASHBOARD: {colorize(self.current_user, c)} ===")
                print("1. Read Inbox")
                print("2. Send Message")
                print(f"3. Play Code Breaker ({games_left} left)")
                print("4. Logout")
                choice = input("Select option: ").strip()
                if choice == '1': self.view_inbox()
                elif choice == '2': self.send_message()
                elif choice == '3': play_code_breaker(self.users[self.current_user], self.save_data)
                elif choice == '4': self.logout()
