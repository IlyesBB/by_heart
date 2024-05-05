from gui import QDeckEditor

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication()
    deck_editor = QDeckEditor()
    deck_editor.showMaximized()
    sys.exit(app.exec())
