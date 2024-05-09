import sys
from PySide6.QtCore import Qt, QTimer, Slot, QEvent, QSize
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtGui import QIcon
from gui.deck import QFlashCardView, QFlashCard
from learn.quizz import Examiner
import os
from config import icons_directory


class QtExam(QWidget):
    """
    Class to review flashcards and save review performance.

    The widget is composed of:
    - A web engine view, to display the flashcards
    - Below, a label displaying the elapsed time
    - At the right, 2 buttons to select success or failure for a flashcard

    It can be in 3 states:
    - Initial: Label and buttons are not displayed, and web engine is blank.
    - In-review: The front face of a flashcard is displaying, and the elapsed time is ticking.
    - After-review: Both faces of the flashcard is displaying. The elapsed time is frozen and the buttons are available.

    Need to hit space-bar to switch states. For the last state, need to push a button to go in-review again.
    """

    def __init__(self):
        super().__init__()

        # Creating subwidgets
        ##############################
        self.examiner: Examiner | None = None
        # self.timer: Will update the elapsed time regularly
        self.timer = QTimer(self)
        # self.timer_label: Label to display the elapsed time
        self.timer_label = QLabel(self)
        # self.exam_panel: The right-side buttons, to select success status after review
        self.buttons = QtPassFailButtons(self.timer_label, button_size=(50, 50))
        # self.card_viewer: QWebEngineView subclass instance to display flashcards
        self.card_viewer = QFlashCardView()

        # Setting layout
        ##############################
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.card_viewer, 9)
        self.layout.addWidget(self.buttons, 1)

        # Setting connections
        ##############################
        self.timer.timeout.connect(self.update_time)
        self.buttons.win.clicked.connect(self.set_pass)
        self.buttons.fail.clicked.connect(self.set_fail)
        self.buttons.win.hide()
        self.buttons.fail.hide()

        # Additional variables
        ##############################
        # self.success: Holds the success status for a flashcard
        self.success: bool | None = None
        self.card: QFlashCard | None = None

    def set_examiner(self, examiner: Examiner) -> None:
        """
        Sets the examiner for the flashcard review session. Needs to be used before
        """
        self.examiner = examiner

    def keyPressEvent(self, event) -> None:
        """
        Handles space-bar press.

        If state is 'In-review': Set to 'After-review'
        And the contrary.
        """
        # print(event.text(), event.modifiers())
        if event.key() == Qt.Key_Space and event.type() == QEvent.KeyPress:
            if self.buttons.fail.isDown() or self.buttons.win.isDown() or self.card is None:
                self.pick_return_card()
            elif self.examiner.has_picked_card():
                self.flip_card()

    def closeEvent(self, event) -> None:
        """
        When the widget is closed, resets it the 'initial' state
        """
        self.timer.stop()
        self.timer_label.setText('')
        self.examiner.end()
        self.card_viewer.reset()
        for button in [self.buttons.win, self.buttons.fail]:
            button.hide()
            button.setDown(False)
        self.card = None
        return QWidget.closeEvent(self, event)

    def pick_return_card(self) -> None:
        """
        Method used to pick a card and to save the previous card record:
        'Initial '-> 'In-review' state or 'After-review' -> 'In-review'
        Also:
        - Starts the timer
        - Sets success status to None
        """
        if self.buttons.fail.isDown() or self.buttons.win.isDown():
            self.examiner.return_card(self.card, self.buttons.win.isDown())
            self.card.set_next_review_text(self.examiner.deck)
            self.examiner.deck.set_next_review_text()
        self.card = self.examiner.pick_card()
        self.card_viewer.set_card(self.card, face='front')
        self.timer.start(100)
        for button in [self.buttons.win, self.buttons.fail]:
            button.hide()
            button.setDown(False)

    def flip_card(self) -> None:
        """
        Used to flip a flashcard when review is finished -> 'After-review' state

        Also:
        - Stops the timer
        - Displays the success status buttons
        """
        self.timer.stop()
        self.card_viewer.set_card(self.card, face='both')
        self.buttons.win.show()
        self.buttons.fail.show()

    @Slot()
    def update_time(self) -> None:
        """
        Slot to update the elapsed time while in-review.

        If the flashcard has a target response time, the background of the timer will get more red as it's value gets
        close to the target time. Else, the background will not change.
        """
        # Setting timer background value
        ##################################
        # duration: Elapsed time in seconds since the flashcard was picked
        duration: float = self.examiner.get_duration()
        self.timer_label.setText("%.1fs" % duration)

        # Setting timer background style
        #################################
        target_time: float = self.examiner.time_tracker.get_target_time(self.card)
        if target_time is not None:  # If target time is set
            # noinspection PyTypeChecker
            alpha = min(1, duration / target_time)
            red = int(alpha * 255)
            self.timer_label.setStyleSheet("background-color: rgba(%d,0,0,%.1f); font-size:28px; border-radius: 5px; "
                                           "padding: 3px;" % (red, alpha))
        else:  # If not target time
            self.timer_label.setStyleSheet("font-size:28px; border-radius: 5px; padding: 3px;")

    @Slot()
    def set_pass(self) -> None:
        self.buttons.fail.setDown(False)
        self.buttons.win.setDown(True)

    @Slot()
    def set_fail(self) -> None:
        self.buttons.fail.setDown(True)
        self.buttons.win.setDown(False)


class QtPassFailButtons(QWidget):
    """
    Pass and fail buttons to push at the end of a flashcard review.

    Shortcuts:
    - Enter: Pass
    - Shift+Enter: Fail
    """

    def __init__(self, timer: QLabel, button_size=(50, 50), parent=None):
        super().__init__(parent=parent)
        # Creating subwidgets
        ##############################
        self.fail = QPassFailButton(True, size=button_size, parent=self)
        self.win = QPassFailButton(False, size=button_size, parent=self)
        self.win.setShortcut('Return')
        self.fail.setShortcut('Shift+Return')
        self.win.setToolTip('Correct response (Return)')
        self.fail.setToolTip('Wrong response (Shift+Return)')
        # Setting layout
        ##############################
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.fail, alignment=Qt.AlignCenter)
        self.layout.addWidget(timer, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.win, alignment=Qt.AlignCenter)


class QPassFailButton(QPushButton):
    """
    A button (fail or pass).

    Icons are set with images in icons_directory (config.py)
    """

    def __init__(self, fail: bool, size=(50, 50), parent=None):
        super().__init__(parent=parent)
        self.setMinimumSize(size[0], size[1])

        icon_file = 'remove.png' if fail else 'check-button.png'
        icon_path = os.path.join(icons_directory, icon_file)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(size[0] // 2, size[1] // 2))
