"""Terminal number guessing game."""

import argparse
import json
import random
import sys
from pathlib import Path

DIFFICULTIES = {
    "easy": {"high": 50, "attempts": 10},
    "medium": {"high": 100, "attempts": 7},
    "hard": {"high": 500, "attempts": 9},
}
DEFAULT_SCORES = Path.home() / ".guess_scores.json"


def check_guess(guess, secret):
    """Return 'low', 'high' or 'correct'."""
    if guess < secret:
        return "low"
    if guess > secret:
        return "high"
    return "correct"


def parse_guess(raw, high):
    """Return the guess as an int, or None if it isn't a number between 1 and high."""
    raw = raw.strip()
    if not raw.lstrip("-").isdigit():
        return None
    value = int(raw)
    return value if 1 <= value <= high else None


class ScoreBoard:
    """Best (lowest) number of attempts per difficulty, stored as JSON."""

    def __init__(self, path=DEFAULT_SCORES):
        self.path = Path(path)
        try:
            self.scores = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.scores = {}

    def best(self, difficulty):
        return self.scores.get(difficulty)

    def record(self, difficulty, attempts):
        """Save the score if it beats the best one; return True if it is a new best."""
        best = self.best(difficulty)
        if best is not None and attempts >= best:
            return False
        self.scores[difficulty] = attempts
        self.path.write_text(json.dumps(self.scores, indent=2), encoding="utf-8")
        return True


def play_round(difficulty, rng=random, input_fn=input, output_fn=print):
    """Play one round. Return the number of attempts used, or None if the player lost."""
    settings = DIFFICULTIES[difficulty]
    high, max_attempts = settings["high"], settings["attempts"]
    secret = rng.randint(1, high)
    output_fn(f"I'm thinking of a number between 1 and {high}. You have {max_attempts} attempts.")

    attempts = 0
    while attempts < max_attempts:
        guess = parse_guess(input_fn(f"Guess #{attempts + 1}: "), high)
        if guess is None:
            output_fn(f"Please enter a whole number from 1 to {high}.")
            continue
        attempts += 1
        result = check_guess(guess, secret)
        if result == "correct":
            output_fn(f"Correct! You got it in {attempts} attempt(s).")
            return attempts
        left = max_attempts - attempts
        output_fn(f"Too {result}. {left} attempt(s) left.")
    output_fn(f"Out of attempts! The number was {secret}.")
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Guess the secret number.")
    parser.add_argument("-d", "--difficulty", choices=list(DIFFICULTIES), default="medium")
    parser.add_argument("--scores", default=DEFAULT_SCORES, help="where best scores are saved")
    args = parser.parse_args(argv)

    board = ScoreBoard(args.scores)
    try:
        while True:
            best = board.best(args.difficulty)
            print(f"\n=== {args.difficulty.title()} mode"
                  + (f" | best: {best} attempt(s)" if best else "") + " ===")
            attempts = play_round(args.difficulty)
            if attempts is not None and board.record(args.difficulty, attempts):
                print("New best score!")
            if input("Play again? [y/N] ").strip().lower() != "y":
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("Thanks for playing!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
