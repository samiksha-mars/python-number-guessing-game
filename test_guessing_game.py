import tempfile
import unittest
from pathlib import Path

from guessing_game import ScoreBoard, check_guess, parse_guess, play_round


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def randint(self, low, high):
        return self.value


def scripted(*answers):
    feed = iter(answers)
    return lambda prompt: next(feed)


class RulesTest(unittest.TestCase):

    def test_check_guess(self):
        self.assertEqual(check_guess(10, 20), "low")
        self.assertEqual(check_guess(30, 20), "high")
        self.assertEqual(check_guess(20, 20), "correct")

    def test_parse_guess(self):
        self.assertEqual(parse_guess(" 42 ", 100), 42)
        self.assertIsNone(parse_guess("abc", 100))
        self.assertIsNone(parse_guess("0", 100))
        self.assertIsNone(parse_guess("101", 100))
        self.assertIsNone(parse_guess("-5", 100))

    def test_parse_guess_rejects_malformed_numbers(self):
        for raw in ("--5", "²", "-", ""):
            self.assertIsNone(parse_guess(raw, 100), raw)


class PlayRoundTest(unittest.TestCase):

    def test_win_returns_attempts_and_gives_hints(self):
        output = []
        attempts = play_round("medium", rng=FixedRandom(40),
                              input_fn=scripted("50", "30", "40"), output_fn=output.append)
        self.assertEqual(attempts, 3)
        self.assertIn("Too high", output[1])
        self.assertIn("Too low", output[2])

    def test_invalid_input_does_not_use_an_attempt(self):
        attempts = play_round("easy", rng=FixedRandom(7),
                              input_fn=scripted("seven", "7"), output_fn=lambda s: None)
        self.assertEqual(attempts, 1)

    def test_loss_returns_none_and_reveals_number(self):
        output = []
        guesses = ["1"] * 7
        self.assertIsNone(play_round("medium", rng=FixedRandom(99),
                                     input_fn=scripted(*guesses), output_fn=output.append))
        self.assertIn("The number was 99", output[-1])

    def test_secret_uses_difficulty_range(self):
        calls = []

        class RecordingRandom:
            def randint(self, low, high):
                calls.append((low, high))
                return low

        play_round("hard", rng=RecordingRandom(), input_fn=scripted("1"), output_fn=lambda s: None)
        self.assertEqual(calls, [(1, 500)])


class ScoreBoardTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "scores.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_records_only_better_scores(self):
        board = ScoreBoard(self.path)
        self.assertTrue(board.record("easy", 5))
        self.assertFalse(board.record("easy", 6))
        self.assertTrue(board.record("easy", 3))
        self.assertEqual(ScoreBoard(self.path).best("easy"), 3)

    def test_missing_or_corrupt_file_starts_empty(self):
        self.assertIsNone(ScoreBoard(self.path).best("hard"))
        self.path.write_text("not json")
        self.assertIsNone(ScoreBoard(self.path).best("hard"))


if __name__ == "__main__":
    unittest.main()
