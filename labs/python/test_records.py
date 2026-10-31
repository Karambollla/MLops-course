import unittest
from records import summarize


class RecordTests(unittest.TestCase):
    def test_counts_only_valid_positive_durations(self):
        self.assertEqual(summarize([{"duration": 2}, {"duration": 4}]), {"count": 2, "mean": 3.0})

    def test_empty_and_invalid_records(self):
        self.assertEqual(summarize([]), {"count": 0, "mean": None})
        self.assertEqual(summarize([{}, {"duration": -1}, {"duration": "2"}, {"duration": True}]), {"count": 0, "mean": None})


if __name__ == "__main__":
    unittest.main()
