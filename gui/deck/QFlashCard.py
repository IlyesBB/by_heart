from learn.deck import Deck, FlashCard
from PySide6.QtWidgets import QTreeWidgetItem
from typing import List


class QFlashCard(FlashCard, QTreeWidgetItem):
    """
    This class allows to display a FlashCard as a QTreeWidgetItem
    It is not supposed to have children
    """
    def __init__(self, question: str, correction: str):
        """
        Initializes the QFlashCard with the question as column 0 QTreeWidgetItem text
        """
        FlashCard.__init__(self, question, correction)
        QTreeWidgetItem.__init__(self, [self.question])

    @staticmethod
    def from_flashcard(card: FlashCard):
        """
        Creates a QFlashCard from a FlashCard, with no copy and with the same key
        @param card: Flashcard as base for the QFlashCard object
        @return: QFlashCard with the same attributes
        @rtype: QFlashCard
        """
        q_card = QFlashCard(card.question, card.correction)
        q_card.key = card.key
        return q_card

    def __copy__(self):
        """
        @rtype: QFlashCard
        """
        return self.from_flashcard(FlashCard.__copy__(self))

    def setText(self, column: int, text: str):
        """
        @param column: Column number of the text
        @param text: Text to display
        """
        QTreeWidgetItem.setText(self, column, text)
        # If the first column is set, then it corresponds to the flashcard question
        if column == 0:
            self.question = text

    def __repr__(self):
        return 'Q' + FlashCard.__repr__(self)
