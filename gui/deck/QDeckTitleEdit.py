from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Slot
from gui.deck import QDeck


class QDeckTitleEdit(QWidget):
    """
    This widget is used to edit a deck's title

    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.deck = None
        self.title = QLineEdit(self.deck.title if self.deck is not None else '', parent=self)
        self.save_button = QPushButton("Save")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.save_button)
        # Buttons
        self.save_button.clicked.connect(self.save)

    def set_deck(self, deck: QDeck):
        self.deck = deck
        self.title.setText(self.deck.title)

    @Slot()
    def save(self):
        self.deck.setText(0, self.title.text())
        self.hide()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    card_ = FlashCard("This is my question", "This is my response", ['MyTag'])

    app = QApplication()
    card_editor = QFlashCardEditor(card_)
    card_editor.showMaximized()
    sys.exit(app.exec())
