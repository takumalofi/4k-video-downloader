import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from app.theme import apply_theme
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    apply_theme(app)
    w = MainWindow()
    w.show()
    w.add_download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def check():
        items = w.content.list.items()
        assert len(items) == 1, f"expected 1 item, got {len(items)}"
        assert items[0].kind == "video"
        print("SMOKE OK")

    QTimer.singleShot(400, check)
    QTimer.singleShot(700, app.quit)
    app.exec()
    print("DONE")


if __name__ == "__main__":
    main()
