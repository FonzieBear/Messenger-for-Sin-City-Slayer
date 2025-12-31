# game.py
import random
from utils import clear_screen, colorize
from config import COLORS, MAX_GAMES

def play_code_breaker(user_data, save_callback):
    """
    Runs the game loop.
    user_data: The dictionary for the current user.
    save_callback: A function to call to save data after the game.
    """
    
    if user_data['games_played'] >= MAX_GAMES:
        print(f"\n🚫 {COLORS['RED']}MAXIMUM ATTEMPTS REACHED{COLORS['RESET']}")
        print(f"You have already played {MAX_GAMES} times.")
        print(f"Your High Score: {user_data['high_score']}")
        input("Press Enter to return...")
        return

    clear_screen()
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

        if len(guess_str) != 4 or not guess_str.isdigit():
            print("⚠️ Invalid input. Must be exactly 4 digits.")
            continue

        attempts += 1
        guess = list(guess_str)

        # Calculate Matches
        exact_matches = 0
        temp_secret = []
        temp_guess = []

        for s, g in zip(secret_code, guess):
            if s == g:
                exact_matches += 1
            else:
                temp_secret.append(s)
                temp_guess.append(g)

        partial_matches = 0
        for g in temp_guess:
            if g in temp_secret:
                partial_matches += 1
                temp_secret.remove(g)

        print(f"   Feedback: {COLORS['GREEN']}{exact_matches} Exact{COLORS['RESET']} | {COLORS['YELLOW']}{partial_matches} Partial{COLORS['RESET']}")

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
    
    save_callback()
    input("\nPress Enter to return...")

