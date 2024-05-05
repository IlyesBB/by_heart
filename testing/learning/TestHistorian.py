import unittest
from learn.deck import FlashCard, Deck
from learn.quizz import Historian
from copy import copy
from pandas.testing import assert_frame_equal
import pandas as pd


class TestHistorian(unittest.TestCase):
    def setUp(self):
        self.deck = Deck("MyDeck", [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)])
        self.historian = Historian(self.deck)
        self.historian.add_record(self.deck.cards[2], 2, True)
        self.historian.add_record(self.deck.cards[2], 5, True)
        self.historian.add_record(self.deck.cards[2], 10, False)
        self.historian.add_record(self.deck.cards[8], 50, True)
        self.historian.add_record(self.deck.cards[1], 70, False)
        self.deck.key = 'test'

    def testGetCard(self):
        card = self.deck.cards[5]
        self.assertEqual(self.historian.get_card(card.key, self.deck), card)

    def testWriteReadRecords(self):
        self.historian.save()
        self.historian.save()
        historian = Historian(self.deck)
        df = pd.concat([self.historian.get_records(), self.historian.get_records()], axis=0)
        df = df.reset_index(drop=True)
        assert_frame_equal(historian.get_records(), df)
        self.historian.delete()


if __name__ == '__main__':
    unittest.main()
