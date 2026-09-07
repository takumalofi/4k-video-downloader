from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QPushButton

from app.icons import moon_icon, sun_icon


class ThemeToggleButton(QPushButton):
    themeToggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ghostBtn")
        self.setCheckable(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QSize(18, 18))
        self.setToolTip("Dark mode")
        self._update_icon()
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        self._update_icon()
        self.themeToggled.emit(checked)

    def _update_icon(self):
        if self.isChecked():
            self.setIcon(sun_icon(18))
            self.setToolTip("Light mode")
        else:
            self.setIcon(moon_icon(18))
            self.setToolTip("Dark mode")

    def retheme(self):
        self._update_icon()
