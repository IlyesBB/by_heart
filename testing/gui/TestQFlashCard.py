import unittest
from learn.deck import FlashCard
from gui.deck import QFlashCard
from copy import copy


class TestFlashCard(unittest.TestCase):
    def setUp(self):
        self.card = FlashCard("What?", "Yes")
        self.q_card = QFlashCard.from_flashcard(self.card)

    def testEq(self):
        self.assertEqual(self.card, self.q_card)


if __name__ == '__main__':
    unittest.main()
