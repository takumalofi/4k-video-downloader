import sys

from PySide6.QtWidgets import QApplication

from app.theme import apply_theme
from app.main_window import MainWindow
from app.icons import app_icon


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("4K Video Downloader+")
    app.setWindowIcon(app_icon(64))
    apply_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
