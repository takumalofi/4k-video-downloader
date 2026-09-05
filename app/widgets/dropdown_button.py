from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QPushButton,
    QLabel,
    QHBoxLayout,
    QWidget,
)

from app.icons import chevron_down


class DropdownButton(QPushButton):
    def __init__(self, prefix, value, parent=None):
        super().__init__(parent)
        self.setObjectName("ddBtn")
        self.setFlat(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(42)

        self._prefix = QLabel(prefix)
        self._prefix.setStyleSheet("color:#8A94A0; font-size:13px; background:transparent;")
        self._value = QLabel(value)
        self._value.setStyleSheet(
            "color:#111418; font-size:13px; font-weight:600; background:transparent;"
        )
        self._chevron = QLabel()
        self._chevron.setPixmap(chevron_down(9))
        self._chevron.setStyleSheet("background:transparent;")

        row = QWidget()
        row.setAttribute(Qt.WA_TransparentForMouseEvents)
        row.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(6, 0, 6, 0)
        lay.setSpacing(5)
        lay.addWidget(self._prefix)
        lay.addWidget(self._value)
        lay.addSpacing(1)
        lay.addWidget(self._chevron)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(row)

    def sizeHint(self):
        if self.layout():
            return self.layout().sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        if self.layout():
            return self.layout().sizeHint()
        return super().minimumSizeHint()

    def set_value(self, value):
        self._value.setText(value)

    def value(self):
        return self._value.text()

    def retheme(self):
        from app import theme
        c = theme.colors()
        self._prefix.setStyleSheet(
            f"color:{c['muted']}; font-size:13px; background:transparent;"
        )
        self._value.setStyleSheet(
            f"color:{c['text_strong']}; font-size:13px; font-weight:600;"
            " background:transparent;"
        )
