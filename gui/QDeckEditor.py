from config import icons_directory
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from gui import QTreeDeck, QtExam
from PySide6.QtCore import Qt, Slot, QSize
from gui.deck import QDeck, QFlashCard
from learn.quizz import Examiner
from learn.pickle import DeckManager
import os
from PySide6.QtGui import QIcon


class QDeckEditor(QWidget):
    """
    Main window, allowing to view cards, edit them, move them...

    It's composed of:
    - Upper buttons for edit operations
    - The decks' tree
    - A lower button to start exam

    Upper buttons are defined in the class QDeckButtons of this file.
    The slots these buttons are connected are defined in QTreeDeck.
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("ByHeart")
        # Creation of subwidgets
        ##########################
        self.tree = QTreeDeck(self)
        self.buttons = QDeckButtons(parent=self)
        self.start_button = QPushButton('Start')
        self.start_button.setStyleSheet("font-size: 22px")
        self.exam = QtExam()
        # Adding widgets to layout
        ############################
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.buttons, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.start_button)
        # Connecting buttons to QTreeDeck's slots, and this class' slots
        ########################################################
        self.buttons.save_button.clicked.connect(self.tree.save)
        self.buttons.delete_button.clicked.connect(self.tree.remove)
        self.buttons.copy_button.clicked.connect(self.tree.copy)
        self.buttons.paste_button.clicked.connect(self.tree.paste)
        self.buttons.cut_button.clicked.connect(self.tree.cut)
        self.buttons.edit_button.clicked.connect(self.tree.edit_item)
        self.buttons.create_button.clicked.connect(self.tree.new)
        self.start_button.clicked.connect(self.start_exam)

    @Slot()
    def start_exam(self):
        """
        Called on exam start.

        There needs to be selected items to start the exam. It is possible to select a subset of deck to review.
        However, it is not possible to select multiple decks: The program will only choose the first one.
        It is also not possible to select cards from different decks: Program will throw an error.
        """
        if len(self.tree.selectedItems()) == 0:  # No selected element
            return None
        if len(set([item.parent() for item in self.tree.selectedItems()])) != 1:
            raise ValueError("Items selected for exam must be at same level")
        item = self.tree.selectedItems()[0]
        if isinstance(item, QFlashCard):
            # Selected flashcards
            #######################
            cards = self.tree.selectedItems()
            deck: QDeck = cards[0].parent()
            deck = deck.filter(lambda x: x in cards)
        elif isinstance(item, QDeck):
            # Selected a deck
            #######################
            deck = item
        else:
            raise TypeError('%s not of type QDeck or QFlashCard' % type(item))
        time_tracker = DeckManager.get_time_tracker(deck)
        scheduler = DeckManager.get_scheduler(deck)
        historian = DeckManager.get_historian(deck)
        examiner = Examiner(deck, historian, time_tracker, scheduler)
        self.exam.set_examiner(examiner)
        self.exam.showMaximized()


class QDeckButtons(QWidget):
    """
    Upper buttons of the main window, for flashcard edit operations.
    The following operations are supported:
    - Saving flashcards' contents
    - Creating a new flashcard/deck
    - Deleting a flashcard/deck
    - Cut/copy and paste flashcards
    - Edit a flashcard/deck

    A shortcut is defined for each of these operations.

    Buttons' icons are stored in 'icons_directory', defined in config.py
    """

    def __init__(self, button_size=(50, 50), parent=None):
        super().__init__(parent=None)
        # Creation of the button objects
        ##################################
        self.save_button = QPushButton(self)
        self.create_button = QPushButton(self)
        self.edit_button = QPushButton(self)
        self.copy_button = QPushButton(self)
        self.delete_button = QPushButton(self)
        self.cut_button = QPushButton(self)
        self.paste_button = QPushButton(self)

        # Defining buttons icon files and shortcuts values
        ###################################################
        # edit_buttons: List of all the buttons
        edit_buttons = [self.save_button, self.create_button, self.edit_button, self.copy_button, self.paste_button,
                        self.cut_button, self.delete_button]
        # icon_files: File names of the buttons icons, in order
        icon_files = ["sauvegarder", "add", "pencil", "copy", "paste", "cut-content-button", "trash"]
        # shortcuts:
        shortcuts = ["Ctrl+S", "Ctrl+N", "Ctrl+O", "Ctrl+C", "Ctrl+V", "Ctrl+X", "Delete"]

        # Setting buttons size, icon, shortcut and adding them to layout
        ####################################################################
        self.layout = QHBoxLayout(self)
        for button, icon_file, shortcut in zip(edit_buttons, icon_files, shortcuts):
            self.layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
            icon_path = os.path.join(icons_directory, icon_file + '.png')
            # noinspection PyTypeChecker
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(button_size[0] // 2, button_size[1] // 2))
            button.setShortcut(shortcut)
