import unittest
from learn.deck import FlashCard, Deck
from learn.pickle import JSONEncoder, JSONDecoder
import json
from copy import copy


class TestJSON(unittest.TestCase):
    def setUp(self):
        self.cards = [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)]
        self.deck = Deck("MyDeck", self.cards)

    def testEncodeDecode(self):
        deck_str = json.dumps(self.deck, cls=JSONEncoder)
        self.assertEqual(json.loads(deck_str, cls=JSONDecoder), self.deck)


if __name__ == '__main__':
    unittest.main()
