import unittest
from learn.deck import FlashCard, Deck
from learn.quizz import Scheduler
from copy import copy
import pandas as pd
from config import intervals


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.deck = Deck("MyDeck", [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)])
        self.scheduler = Scheduler(self.deck)
        for ind, card in enumerate(self.deck):
            for i in range(ind):
                self.scheduler.next_box(card)

    def testInit(self):
        scheduler = Scheduler(self.deck)
        for ind, card in enumerate(self.deck):
            self.assertEqual(scheduler.get_box(card), 0)

    def testGet(self):
        for ind, card in enumerate(self.deck):
            self.assertEqual(self.scheduler.get_box(card), ind)

    def testReadWriteIntervals(self):
        self.scheduler.save()
        self.assertEqual(Scheduler(self.deck).box, self.scheduler.box)
        self.scheduler.delete()


if __name__ == '__main__':
    unittest.main()
