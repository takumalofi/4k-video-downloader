from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel

from app import theme
from app import i18n


class StatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(28)
        self._apply_style()

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 12, 0)
        lay.setSpacing(0)

        self.info_label = QLabel("0 items")
        lay.addWidget(self.info_label)

        lay.addStretch()

        self.folder_label = QLabel("D:/")
        lay.addWidget(self.folder_label)

        self._apply_label_styles()

        self._total = 0
        self._downloading = 0
        self._speed = ""

    def set_items(self, total):
        self._total = total
        self._update()

    def set_downloading(self, n):
        self._downloading = n
        self._update()

    def set_speed(self, speed):
        self._speed = speed
        self._update()

    def set_folder(self, path):
        path = path.replace("\\", "/")
        self.folder_label.setText(path)

    def retheme(self):
        self._apply_style()
        self._apply_label_styles()

    def _apply_style(self):
        c = theme.colors()
        self.setStyleSheet(
            "QFrame#statusBar {"
            f" background:{c['panel2']}; border-top:1px solid {c['border']};"
            " }"
        )

    def _apply_label_styles(self):
        c = theme.colors()
        self.info_label.setStyleSheet(
            f"color:{c['text']}; font-size:12px; background:transparent; border:none;"
        )
        self.folder_label.setStyleSheet(
            f"color:{c['muted']}; font-size:12px; background:transparent; border:none;"
        )

    def _update(self):
        parts = [i18n.items_label(self._total)]
        if self._downloading > 0:
            parts.append(f"{self._downloading} {i18n.tr('downloading_word')}")
        if self._speed:
            parts.append(self._speed)
        self.info_label.setText(" • ".join(parts))

    @staticmethod
    def _plural(n, word):
        return f"{n} {word}" if n == 1 else f"{n} {word}s"
