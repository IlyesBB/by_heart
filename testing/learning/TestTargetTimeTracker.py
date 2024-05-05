import unittest
from learn.deck import FlashCard, Deck
from learn.quizz import TargetTimeTracker
from copy import copy
import pandas as pd


class TestTargetTimeTracker(unittest.TestCase):
    def setUp(self):
        self.deck = Deck("MyDeck", [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)])
        self.time_tracker = TargetTimeTracker(self.deck)
        for ind, card in enumerate(self.deck):
            self.time_tracker.set_target_time(card, ind * 3 / 2)

    def testGetTargetTime(self):
        self.assertEqual(self.time_tracker.get_target_time(self.deck[0]), 0)
        self.assertEqual(self.time_tracker.get_target_time(self.deck[1]), 1.5)
        card_unknown = FlashCard("Question", "Correction")
        self.assertIsNone(self.time_tracker.get_target_time(card_unknown))

    def testReadWriteTargetTime(self):
        self.time_tracker.save()
        self.assertEqual(TargetTimeTracker(self.deck).target_time, self.time_tracker.target_time)
        self.time_tracker.delete()


if __name__ == '__main__':
    unittest.main()
