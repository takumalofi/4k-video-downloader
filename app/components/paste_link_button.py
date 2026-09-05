from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QPushButton

from app.icons import paste_icon
from app import i18n


class PasteLinkButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(i18n.tr("paste_link"), parent)
        self.setObjectName("pasteBtn")
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedSize(170, 42)
        self.setIcon(paste_icon(20))
        self.setIconSize(QSize(20, 20))
        self.setStyleSheet(
            "QPushButton#pasteBtn { background:#55B900; color:#FFFFFF; border:none;"
            " border-radius:4px; font-size:14px; outline:none; padding-left:6px; }"
            "QPushButton#pasteBtn:hover { background:#4FA600; }"
            "QPushButton#pasteBtn:pressed { background:#479500; }"
        )
