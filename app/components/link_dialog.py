import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from app.icons import search_icon
from app import i18n


def extract_url(text):
    text = (text or "").strip()
    if not text:
        return ""
    match = re.search(r"https?://\S+", text)
    if match:
        return match.group(0).rstrip(")\"'<>").rstrip(".,;")
    if " " not in text:
        host = text.split("/")[0]
        if "." in host:
            match = re.search(r"https?://\S+", "https://" + text)
            if match:
                return match.group(0).rstrip(")\"'<>").rstrip(".,;")
    return ""


class LinkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.tr("enter_link"))
        self.setModal(True)
        self.setFixedWidth(560)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 18, 20, 16)
        lay.setSpacing(12)

        title = QLabel(i18n.tr("enter_link"))
        title.setObjectName("dialogTitle")
        lay.addWidget(title)

        info = QLabel(
            i18n.tr("clipboard_no_link") + "\n" + i18n.tr("enter_link_hint")
        )
        info.setStyleSheet("color:#8A94A0; font-size:13px;")
        lay.addWidget(info)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://www.youtube.com/watch?v=...")
        clipboard = self._clipboard_text()
        if clipboard:
            self.url_edit.setText(clipboard)
        self.url_edit.addAction(search_icon(16), QLineEdit.LeadingPosition)
        clear_action = QAction("✕", self)
        clear_action.setToolTip("Clear")
        clear_action.triggered.connect(self.url_edit.clear)
        self.url_edit.addAction(clear_action, QLineEdit.TrailingPosition)
        self.url_edit.returnPressed.connect(self._go)
        row.addWidget(self.url_edit, 1)

        self.go_btn = QPushButton(i18n.tr("go"))
        self.go_btn.setCursor(Qt.PointingHandCursor)
        self.go_btn.setFixedSize(80, 36)
        self.go_btn.setStyleSheet(
            "QPushButton { background:#55B900; color:#FFFFFF; border:none;"
            " border-radius:4px; font-size:13px; }"
            "QPushButton:hover { background:#4FA600; }"
        )
        self.go_btn.clicked.connect(self._go)
        row.addWidget(self.go_btn)

        lay.addLayout(row)
        self.url_edit.setFocus()
        self.url_edit.selectAll()

    @staticmethod
    def _clipboard_text():
        from PySide6.QtGui import QGuiApplication
        return QGuiApplication.clipboard().text().strip()

    def _go(self):
        if self.url():
            self.accept()
        else:
            self.info.setText(i18n.tr("invalid_link"))
            self.info.setStyleSheet("color:#C62828; font-size:12px;")

    def url(self):
        return extract_url(self.url_edit.text())
