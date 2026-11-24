# Python Number Guessing Game

Guess the secret number in as few attempts as possible. The game tells you
whether each guess is too high or too low. Uses only the Python standard library.

## Features

- Three difficulty levels with different ranges and attempt limits
- Higher/lower hints after every guess
- Best score (fewest attempts) saved per difficulty
- Play several rounds in a row

## Difficulty levels

| Level  | Range   | Attempts |
|--------|---------|----------|
| easy   | 1–50    | 10       |
| medium | 1–100   | 7        |
| hard   | 1–500   | 9        |

## Usage

```bash
python3 guessing_game.py               # medium
python3 guessing_game.py -d hard
python3 guessing_game.py --scores my_scores.json
```

```
=== Medium mode | best: 5 attempt(s) ===
I'm thinking of a number between 1 and 100. You have 7 attempts.
Guess #1: 50
Too high. 6 attempt(s) left.
Guess #2: 25
Too low. 5 attempt(s) left.
Guess #3: 37
Correct! You got it in 3 attempt(s).
New best score!
Play again? [y/N]
```

Best scores are saved to `~/.guess_scores.json` by default.

Tip: guessing the middle of the remaining range (binary search) always wins
within the attempt limit.

## Tests

The game takes injectable input and random-number functions, so it is fully testable:

```bash
python3 -m unittest test_guessing_game.py
```
