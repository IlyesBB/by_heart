from learn.deck import Deck
from PySide6.QtWidgets import QTreeWidgetItem
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Qt
from gui.deck import QFlashCard
from typing import List
from learn.pickle import DeckManager
from datetime import datetime as dt
from typing import List, Iterator, Callable


class QDeck(Deck, QTreeWidgetItem):
    """
    This class allows to display a Deck as a QTreeWidgetItem
    It is supposed to have only one level of children, which are its flashcards
    """

    def __init__(self, title: str, cards: List[QFlashCard] = None):
        """
        Adds the QFlashCard objects as children of th QDeck
        """
        super().__init__(title, cards)
        QTreeWidgetItem.__init__(self, [self.title, ''])
        card: QFlashCard
        for card in self.cards:
            self.addChild(card)

    @staticmethod
    def from_deck(deck: Deck):
        """
        Creates a QDeck from a Deck, with no copy and with the same key
        @param deck: Deck as base for the QDeck object
        @return: QDeck with the same attributes
        @rtype: QDeck
        """
        for ind, card in enumerate(deck):
            q_card = QFlashCard.from_flashcard(card)
            q_card.set_next_review_text(deck)
            deck[ind] = q_card
        # noinspection PyTypeChecker
        q_deck = QDeck(deck.title, deck.cards)
        q_deck.key = deck.key
        q_deck.set_next_review_text()
        return q_deck

    def get_next_review_days(self) -> None | int:
        next_review_days = [card.get_next_review_days(self) for card in self if card.is_enabled()]
        next_review_days = [days for days in next_review_days if days is not None]
        if not next_review_days:
            return
        return min(next_review_days)

    def set_next_review_text(self):
        """
        Sets the duration until next review in column 1
        """
        # Setting text
        ###############
        days_next_review_in = self.get_next_review_days()
        if days_next_review_in is None:
            self.setText(1, '')
            return
        if days_next_review_in != 0:
            self.setText(1, str(days_next_review_in) + ' ' + ('days' if abs(days_next_review_in) > 1 else 'day'))
        else:
            self.setText(1, 'Today')
        # Setting background
        #####################
        color = QColor.fromRgb(255, 0, 0, 127) if days_next_review_in < 0 else QColor.fromRgb(0, 0, 0, 255)
        self.setForeground(1, QBrush(color, Qt.SolidPattern))

    def add_card(self, card: QFlashCard):
        self.rename_duplicate_card(card)  # In case another card has the same question
        self.cards.append(card)
        self.addChild(card)

    def __iter__(self):
        return iter(self.cards)

    def insert_card(self, index: int, card: QFlashCard):
        self.rename_duplicate_card(card)
        self.insertChild(index, card)
        Deck.insert_card(self, index, card)

    def rename_duplicate_card(self, card: QFlashCard) -> None:
        """
        If the QFlashCard has the same question as one in the QDeck, adds a suffix to the card's question.
        """
        count_duplicates = 0
        name = card.question
        while card.text(0) in [d_card.text(0) for d_card in self.cards]:
            count_duplicates += 1
            card.setText(0, name + '(%s)' % count_duplicates)

    def remove_card(self, card: QFlashCard) -> None:
        Deck.remove_card(self, card)
        self.removeChild(card)

    def clear(self):
        self.cards.clear()
        self.takeChildren()

    def __copy__(self):
        """
        @rtype: QDeck
        """
        return self.from_deck(Deck.__copy__(self))

    def setText(self, column, text):
        """
        @param column: Column number of the text
        @param text: Text to display
        """
        QTreeWidgetItem.setText(self, column, text)
        # If the first column is set, then it corresponds to the deck's title
        if column == 0:
            self.title = text

    def filter(self, func: Callable[[QFlashCard], bool]):
        # noinspection PyTypeChecker
        cards = list(filter(func, self))
        deck_copy = QDeck(self.title)
        deck_copy.cards = cards
        deck_copy.key = self.key
        return deck_copy
