import unittest
from learn.deck import FlashCard
from copy import copy


class TestFlashCard(unittest.TestCase):
    def setUp(self):
        self.card = FlashCard("What?", "Yes")

    def testCopy(self):
        card = copy(self.card)
        self.assertEqual(card.question, self.card.question)
        self.assertEqual(card.correction, self.card.correction)
        self.assertNotEqual(card.key, self.card.key)

    def testEq(self):
        self.assertEqual(self.card, self.card)
        self.assertNotEqual(self.card, copy(self.card))


if __name__ == '__main__':
    unittest.main()
