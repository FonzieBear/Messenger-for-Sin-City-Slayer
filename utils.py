# utils.py
import os
import sys
import getpass
from itertools import cycle
from config import COLORS, USER_COLORS

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def xor_cipher(text, key):
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(text, cycle(key)))

def colorize(text, color_code):
    return f"{color_code}{text}{COLORS['RESET']}"

def get_user_color(username):
    return USER_COLORS.get(username, COLORS['WHITE'])

def get_secure_input(prompt_text):
    """Handles masked input logic safely across OSs."""
    try:
        # getpass usually handles masking automatically (invisible typing)
        # We manually add the colon here for consistency
        return getpass.getpass(f"{prompt_text}: ").strip()
    except Exception:
        # Fallback for IDEs that don't support getpass
        return input(f"{prompt_text} (Warning: Visible): ").strip()
