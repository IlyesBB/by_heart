import unittest
from learn.deck import FlashCard, Deck
from copy import copy


class TestDeck(unittest.TestCase):
    def setUp(self):
        self.cards = [FlashCard("Q%d?" % i, "R%d" % i) for i in range(10)]
        self.deck = Deck("MyDeck", self.cards)

    def testFilter(self):
        func = lambda x: int(x.correction[-1]) % 2 == 0
        sub_deck = self.deck.filter(func)
        self.assertEqual(sub_deck.key, self.deck.key)
        self.assertEqual(sub_deck.cards, [self.cards[i] for i in range(len(self.cards)) if i % 2 == 0])

    def testCopy(self):
        deck = copy(self.deck)
        for i, card in enumerate(deck):
            self.assertEqual(card.question, self.deck.cards[i].question)
            self.assertEqual(card.correction, self.deck.cards[i].correction)
            self.assertNotEqual(card.key, self.deck.cards[i].key)

    def testEq(self):
        self.assertEqual(self.deck, self.deck)
        self.assertNotEqual(self.deck, copy(self.deck))
        func = lambda x: int(x.correction[-1]) % 2 == 0
        self.assertNotEqual(self.deck.filter(func), self.deck)


if __name__ == '__main__':
    unittest.main()
