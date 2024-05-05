from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QRect
from config import project_directory
from gui.deck import generate_card_html
from learn.deck import FlashCard


class QFlashCardView(QWebEngineView):
    """
    Class to display a flashcard's content.

    Allows to select the card's faces to display.
    """
    def __init__(self, size=(700, 450), parent=None):
        super().__init__(parent)
        self.setObjectName(u"FlashCardViewer")
        self.setGeometry(QRect(0, 0, size[0], size[1]))
        self.reset()
        self.setWindowTitle("Flashcard view")

    def reset(self):
        self.setHtml(
            '<!DOCTYPE html>\
            <html lang="en">\
            <head>\
                <meta charset="UTF-8">\
            </head>\
            <body style="position: absolute; left: 50%; top: 50%;">\
                Press SPACE to start\
            </body>\
            </html>'
        )

    def set_card(self, card: FlashCard, face='both'):
        content = generate_card_html(card, face=face)
        self.setHtml(content, baseUrl=QUrl("file:///" + project_directory))
