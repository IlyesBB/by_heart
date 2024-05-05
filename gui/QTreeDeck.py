from PySide6.QtWidgets import QTreeWidget, QAbstractItemView
from learn.deck import FlashCard
from learn.pickle import DeckManager
from gui.deck import QDeck, QFlashCard, QDeckTitleEdit, QFlashCardEdit
from copy import copy
from PySide6.QtCore import Slot
from learn.pickle import DeckManager
from learn.quizz import TargetTimeTracker, Scheduler


class QTreeDeck(QTreeWidget):
    """
    Tree representing the decks and their flashcards.

    First level elements are QDecks and second are QFlashcards.

    Also implements the methods to create, edit, save, delete, copy/cut and paste the tree items.
    Those methods are slots to be connected in QDeckEditor class.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Creation of subwidgets
        ##############################
        self.decks = [QDeck.from_deck(deck) for deck in DeckManager.load()]
        self.deck_title_editor = QDeckTitleEdit()
        self.card_editor = QFlashCardEdit()

        # Instance parameters
        ##########################
        self.setColumnCount(1)
        self.setHeaderLabels(["Decks"])
        self.insertTopLevelItems(0, self.decks)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setStyleSheet("font-size: 16px")

        # Connections and additional variables
        #######################################
        self.itemDoubleClicked.connect(self.double_click_item)
        self.has_cut = False
        self.deck_cut: QDeck = QDeck('')

    @Slot()
    def double_click_item(self, item: QDeck | QFlashCard, column_no: int) -> None:
        """
        Displays the flashcard if it was double-clicked.
        """
        if isinstance(item, QFlashCard) and column_no == 0:
            self.card_editor.viewer.set_card(item, face='both')
            self.card_editor.viewer.show()

    @Slot()
    def remove(self) -> None:
        """
        Deletes the selected elements at object and file system levels.
        Can only select cards of the same deck or decks.
        """
        selected: [QFlashCard | QDeck] = self.selectedItems()
        if not selected or not self.selection_at_same_level():
            return None  # No selection, or cards from different decks, or mix of cards and decks
        selected: [QFlashCard] | [QDeck]
        if isinstance(selected[0], QDeck):
            # Delete decks
            ################
            selected: [QDeck]
            for deck in selected:
                QTreeWidget.takeTopLevelItem(self, self.decks.index(deck))
                DeckManager.remove(deck)
                self.decks.remove(deck)
        elif isinstance(selected[0], QFlashCard):
            # Delete flashcards
            ####################
            selected: [QFlashCard]
            DeckManager.remove_cards(selected, selected[0].parent())

    @Slot()
    def copy(self) -> None:
        """
        Copies the selected elements. Can only copy flashcards.

        If decks are selected, will copy the flashcards they contain.
        If flashcards are selected, they must be from same deck.

        All cut cards are moved in an auxiliary deck
        """
        selected: [QFlashCard | QDeck] = self.selectedItems()
        DeckManager.clear(self.deck_cut)
        if not selected or not self.selection_at_same_level():
            return None  # No selection, or cards from different decks, or mix of cards and decks
        selected: [QFlashCard] | [QDeck]
        if isinstance(selected[0], QDeck):
            # Selected: Deck list -> list of cards of the decks
            selected: [QDeck]
            selected = [card for deck in selected for card in deck.cards]
        selected: [QFlashCard]
        self.deck_cut.add_cards([copy(card) for card in selected])
        self.has_cut = False

    @Slot()
    def cut(self) -> None:
        """
        Cuts the selected elements. Can only cut flashcards.

        If decks are selected, will cut the flashcards they contain.
        If flashcards are selected, they must be from same deck.

        All cut cards are moved in an auxiliary deck
        """
        selected: [QFlashCard | QDeck] = self.selectedItems()
        DeckManager.clear(self.deck_cut)
        if not selected or not self.selection_at_same_level():
            return None  # No selection, or cards from different decks, or mix of cards and decks
        selected: [QFlashCard] | [QDeck]
        if isinstance(selected[0], QFlashCard):
            # Cut flashcards
            ################
            selected: [QFlashCard]
            parent: QDeck = selected[0].parent()
            DeckManager.move_cards(selected, parent, self.deck_cut)
        elif isinstance(selected[0], QDeck):
            # Cut decks
            ################
            selected: [QDeck]
            for deck in selected:
                DeckManager.move_cards(copy(deck.cards), deck, self.deck_cut)
        self.has_cut = True

    @Slot()
    def paste(self) -> None:
        """
        Pastes the previously copied/cut elements in/next to selected element

        If multiple selections, will take the first.

        If selected a flashcard, pastes the cards in the same deck after the selected card
        If selected a deck, pastes the cards in the beginning of the deck
        """
        selected: [QFlashCard | QDeck] = self.selectedItems()
        if len(self.deck_cut) == 0 or not selected:
            return None
        # Index for insertion
        #######################
        item: QFlashCard | QDeck = selected[0]
        deck = item if isinstance(item, QDeck) else item.parent()
        index = 0 if isinstance(item, QDeck) else deck.indexOfChild(item) + 1
        # Insertion
        #############
        if self.has_cut:
            DeckManager.move_cards(copy(self.deck_cut.cards), self.deck_cut, deck, index_destination=index)
        else:
            deck.insert_cards(index, [copy(card) for card in self.deck_cut])
        self.has_cut = False

    @Slot()
    def edit_item(self) -> None:
        """
        Used to edit tree elements.

        If multiple selections, will take the first.

        If selected a flashcard, shows the QFlashCardEdit widget
        If selected a deck, shows the QDeckTitleEdit widget
        """
        if len(self.selectedItems()) == 0:
            return None
        item: QFlashCard | QDeck = self.selectedItems()[0]
        if isinstance(item, QDeck):
            self.deck_title_editor.set_deck(item)
            self.deck_title_editor.show()
        elif isinstance(item, QFlashCard):
            target_time_tracker = DeckManager.get_time_tracker(item.parent())
            self.card_editor.set_card(item, target_time_tracker)
            self.card_editor.show()

    @Slot()
    def new(self) -> None:
        """
        Used to create tree elements.

        If no selection, creates a deck and shows the QDeckTitleEdit widget
        If selected a deck, creates a card in that deck and shows the QFlashCardEdit widget
        """
        if len(self.selectedItems()) == 0:
            # No selection
            ##################
            new_item = QDeck('-- Enter deck name --')
            self.insertTopLevelItem(0, new_item)
            self.decks.append(new_item)
        else:
            # Selected a Deck
            ##################
            item: QFlashCard | QDeck = self.selectedItems()[0]
            parent: QDeck = item if isinstance(item, QDeck) else item.parent()
            new_item = QFlashCard('-- Enter a question --', '-- Enter a correction --')
            parent.add_card(new_item)
        self.clearSelection()
        self.setCurrentItem(new_item)
        self.edit_item()

    @Slot()
    def save(self) -> None:
        """
        Saves the decks and related cards data in the file system
        """
        for deck in self.decks:
            DeckManager.save(deck)
        for deck in DeckManager.decks:
            if deck not in self.decks:
                DeckManager.delete(deck)

    def selection_at_same_level(self) -> bool:
        """
        @return: True if selected cards from different decks, or mix of cards and decks
        """
        return len(set([item.parent() for item in self.selectedItems()])) == 1


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication()
    tree = QTreeDeck()
    tree.show()
    sys.exit(app.exec())
