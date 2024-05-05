import unittest
from learn.deck import FlashCard, Deck
from gui.deck import QFlashCard, QDeck
from copy import copy


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.cards = [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)]
        self.deck = Deck("MyDeck", self.cards)
        self.q_deck = QDeck.from_deck(self.deck)

    def testEq(self):
        self.assertEqual(self.deck, self.q_deck)


if __name__ == '__main__':
    unittest.main()
