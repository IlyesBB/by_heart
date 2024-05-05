from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot
from gui.deck import QFlashCardView, QFlashCard
from learn.quizz import TargetTimeTracker


class QFlashCardEdit(QWidget):
    """
    This widget is displayed on edit of a flashcard
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.card: QFlashCard | None = None
        self.target_time_tracker: TargetTimeTracker | None = None
        self.viewer = QFlashCardView()
        self.layout = QVBoxLayout(self)
        # Header with target time and card key
        #######################################
        header = QWidget(self)
        header.layout = QHBoxLayout(header)
        # Target time
        ################
        self.target_time_widget = QWidget(header)
        self.target_time_widget.layout = QHBoxLayout(self.target_time_widget)
        self.target_time = QLabel('')
        self.reset_target_time_button = QPushButton("Reset")
        self.target_time_widget.layout.addWidget(self.target_time)
        self.target_time_widget.layout.addWidget(self.reset_target_time_button)
        header.layout.addWidget(self.target_time_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        # Card key label
        ###################
        self.card_key = QLabel('')
        self.card_key.setStyleSheet('color: rgba(180,180,180,1)')
        header.layout.addWidget(self.card_key, alignment=Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(header)
        # Text editors
        ################
        self.question = QTextEdit('', parent=self)
        self.correction = QTextEdit('', parent=self)
        self.layout.addWidget(self.question)
        self.layout.addWidget(self.correction)
        # Lower buttons
        ################
        self.buttons_widget = QWidget(self)
        self.save_button = QPushButton("Save")
        self.preview_button = QPushButton("Preview")
        self.buttons_widget.layout = QHBoxLayout(self.buttons_widget)
        self.buttons_widget.layout.addWidget(self.save_button)
        self.buttons_widget.layout.addWidget(self.preview_button)
        self.layout.addWidget(self.buttons_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        # Signals
        ##########
        self.save_button.clicked.connect(self.save)
        self.preview_button.clicked.connect(self.preview)
        self.reset_target_time_button.clicked.connect(self.reset_target_time)

    def set_card(self, card: QFlashCard, target_time_tracker: TargetTimeTracker):
        self.card = card
        self.target_time_tracker = target_time_tracker
        self.question.setPlainText(card.question)
        self.correction.setPlainText(card.correction)
        self.question.setStyleSheet('')
        self.correction.setStyleSheet('')
        self.card_key.setText(self.card.key)
        target_time = self.target_time_tracker.get_target_time(self.card)
        if target_time is not None:
            self.target_time.setText("Target time: %.1fs" % target_time)
        else:
            self.target_time.setText("Target time: ____s")

    @Slot()
    def reset_target_time(self):
        self.target_time_tracker.set_target_time(self.card, None)
        self.target_time.setText("Target time: ____s")

    @Slot()
    def save(self):
        self.card.setText(0, self.question.toPlainText())
        self.card.correction = self.correction.toPlainText()
        self.target_time_tracker.save()

    @Slot()
    def preview(self):
        self.viewer.set_card(self.card, face='both')
        self.viewer.show()
