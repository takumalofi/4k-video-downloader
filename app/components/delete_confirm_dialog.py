from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QFont, QPixmap, QPen
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QSizePolicy,
)

from app import theme
from app import i18n


def _question_pixmap(diameter=40):
    dpr = 3
    pm = QPixmap(int(diameter * dpr), int(diameter * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(theme.PRIMARY))
    p.drawEllipse(0, 0, diameter, diameter)
    pen = QPen(QColor("#FFFFFF"))
    pen.setWidth(2)
    p.setPen(pen)
    font = QFont("Segoe UI", int(diameter * 0.48))
    font.setBold(True)
    p.setFont(font)
    p.drawText(QRect(0, 0, diameter, diameter), Qt.AlignCenter, "?")
    p.end()
    return pm


class DeleteConfirmDialog(QDialog):
    def __init__(self, parent=None, title="", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(320)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self._drag_pos = None
        self.confirmed = False
        self.permanent = False

        c = theme.colors()
        self.setStyleSheet(
            "QDialog { background:%s; border:1px solid %s; }" % (c["panel"], c["border"])
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 24)
        root.setSpacing(22)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { background:transparent; border:none; color:%s;"
            " font-size:14px; border-radius:4px; }"
            "QPushButton:hover { background:%s; }" % (c["muted"], c["hover"])
        )
        close_btn.clicked.connect(self.reject)
        top.addWidget(close_btn)
        root.addLayout(top)

        icon_label = QLabel()
        icon_label.setPixmap(_question_pixmap(40))
        icon_label.setAlignment(Qt.AlignCenter)
        root.addWidget(icon_label, alignment=Qt.AlignHCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "color:%s; font-size:16px; font-weight:600; background:transparent;"
            % c["text"]
        )
        root.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(
            "color:%s; font-size:13px; background:transparent;" % c["text"]
        )
        root.addWidget(msg_label)

        self.checkbox = QCheckBox(i18n.tr("permanently_delete"))
        self.checkbox.setStyleSheet(
            f"QCheckBox {{ font-size:13px; color:{c['text']}; }}"
        )
        checkbox_row = QHBoxLayout()
        checkbox_row.addStretch()
        checkbox_row.addWidget(self.checkbox)
        checkbox_row.addStretch()
        root.addLayout(checkbox_row)

        root.addSpacing(4)

        self.delete_btn = QPushButton(i18n.tr("delete"))
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.delete_btn.setStyleSheet(
            "QPushButton { background:%s; color:#FFFFFF; border:none;"
            " border-radius:4px; font-size:14px; }"
            "QPushButton:hover { background:%s; }"
            % (theme.PRIMARY, theme.PRIMARY_HOVER)
        )
        self.delete_btn.clicked.connect(self._on_delete)
        root.addWidget(self.delete_btn)

        root.addSpacing(-8)

        self.cancel_btn = QPushButton(i18n.tr("cancel"))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background:%s; color:%s; border:none;"
            " border-radius:4px; font-size:14px; }"
            "QPushButton:hover { background:%s; }"
            % (c["hover"], c["text"], c["border_soft"])
        )
        self.cancel_btn.clicked.connect(self.reject)
        root.addWidget(self.cancel_btn)

    def _on_delete(self):
        self.confirmed = True
        self.permanent = self.checkbox.isChecked()
        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)


def confirm_delete(parent, title, message):
    dlg = DeleteConfirmDialog(parent, title, message)
    dlg.exec()
    return dlg.confirmed, dlg.permanent
