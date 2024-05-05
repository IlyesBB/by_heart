import unittest
from learn.deck import FlashCard, Deck
from learn.quizz import Historian, TargetTimeTracker, Scheduler, Picker
from copy import copy
from config import sample_size, warmup_size, factor_max

total_size = sample_size + warmup_size


class TestPicker(unittest.TestCase):
    def setUp(self):
        self.deck = Deck("MyDeck", [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)])
        self.historian: Historian = Historian(self.deck)
        self.time_tracker = TargetTimeTracker(self.deck)
        self.scheduler = Scheduler(self.deck)
        self.picker = Picker(self.deck, self.historian, self.time_tracker, self.scheduler)

    def assertScoreEqual(self, card: FlashCard, score: int):
        return self.assertEqual(self.picker.score(card, self.historian.get_records()), score)

    def testInitTargetTime(self):
        card = self.picker.pick_card()
        for i in range(total_size):
            self.assertScoreEqual(card, -1)
            self.assertEqual(self.picker.pick_card(), card)
            self.historian.add_record(card, 5.8, True)
        self.assertScoreEqual(card, 4)
        self.assertEqual(self.time_tracker.get_target_time(card), 5.8)
        self.assertNotEqual(self.picker.pick_card(), card)

    def testInitTargetTimeFailure(self):
        card = self.deck[0]
        for i in range(total_size - 1):
            self.historian.add_record(card, 5.8, True)
        self.historian.add_record(card, 5.8, False)
        self.assertScoreEqual(card, -1)
        for i in range(sample_size):
            self.assertScoreEqual(card, -1)
            self.historian.add_record(card, 6.7, True)
        self.assertScoreEqual(card, 2)
        self.assertEqual(self.time_tracker.get_target_time(card), 6.7)

    def testFalseResponse(self):
        for card in self.deck:
            for i in range(total_size):
                self.historian.add_record(card, 5.8, True)
                self.picker.score(card)
        card = self.deck[0]
        self.scheduler.next_box(card)
        self.scheduler.next_box(card)
        self.historian.add_record(card, 5.8, False)
        self.assertScoreEqual(card, 0)
        self.assertEqual(self.scheduler.get_box(card), 0)
        self.assertEqual(self.picker.pick_card(), card)

    def testTargetTimeReset(self):
        for card in self.deck:
            for i in range(total_size):
                self.historian.add_record(card, 5.8, True)
                self.picker.score(card)
        card = self.deck[0]
        for i in range(total_size):
            self.historian.add_record(card, 5.8 * (factor_max + 1), True)
            self.picker.score(card)
        self.assertEqual(self.time_tracker.get_target_time(card), 5.8 * (factor_max + 1))

    def testTargetTimeExceeded(self):
        for card in self.deck:
            for i in range(total_size):
                self.historian.add_record(card, 5.8, True)
                self.picker.score(card)
        card = self.deck[0]
        self.scheduler.next_box(card)
        self.scheduler.next_box(card)
        for i in range(sample_size + 1, 1, -1):
            self.historian.add_record(card, 5.8 * (factor_max + i), True)
            self.picker.score(card)
        self.assertScoreEqual(card, 0)
        self.assertEqual(self.scheduler.get_box(card), 1)

    def testRevisionTimePassed(self):
        # TODO: Find a way to test this
        pass


if __name__ == '__main__':
    unittest.main()
