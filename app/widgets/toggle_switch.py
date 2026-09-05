from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QAbstractButton

from app.theme import PRIMARY


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(46, 24)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        track = QColor(PRIMARY) if self.isChecked() else QColor("#C9CDD2")
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(track))
        p.drawRoundedRect(QRectF(0, 0, 46, 24), 12, 12)
        kx = 34 if self.isChecked() else 12
        p.setBrush(QBrush(QColor("#FFFFFF")))
        p.drawEllipse(QPointF(kx, 12), 9, 9)
        if self.isChecked():
            pen = QPen(QColor(PRIMARY), 1.8)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            p.setPen(pen)
            p.drawLine(QPointF(kx - 3.5, 12), QPointF(kx - 0.8, 14.8))
            p.drawLine(QPointF(kx - 0.8, 14.8), QPointF(kx + 4, 9))
        else:
            pen = QPen(QColor("#A6ADB4"), 1.6)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawLine(QPointF(kx - 3, 12), QPointF(kx + 3, 12))
