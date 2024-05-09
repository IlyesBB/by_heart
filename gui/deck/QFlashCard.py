from learn.deck import Deck, FlashCard
from learn.pickle import DeckManager
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from typing import List
from datetime import datetime as dt


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
        QTreeWidgetItem.__init__(self, [self.question, ''])

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

    def set_next_review_in(self, deck: Deck):
        """
        Sets the duration until next review in column 1
        """
        records = DeckManager.get_historian(deck).get_records()
        card_records = records[records['Card'] == self]
        if len(card_records) == 0:
            return
        # Setting text
        ###############
        days_until_next_review = DeckManager.get_scheduler(deck).get_interval(self).days
        days_since_last_review = (dt.now() - card_records['Date'].iloc[-1]).days
        days_next_review_in = days_until_next_review - days_since_last_review
        if days_next_review_in != 0:
            self.setText(1, str(days_next_review_in) + ' ' + ('days' if abs(days_next_review_in) > 1 else 'day'))
        else:
            self.setText(1, 'Today')
        # Setting background
        #####################
        if days_next_review_in < 0:
            background = self.background(1)
            background.setColor(QColor.fromRgb(255, 0, 0, 127))
            background.setStyle(Qt.SolidPattern)
            self.setBackground(1, background)

    def __repr__(self):
        return 'Q' + FlashCard.__repr__(self)
