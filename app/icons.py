import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPixmap,
    QPainter,
    QPen,
    QBrush,
    QColor,
    QIcon,
    QPainterPath,
)

from app import theme as _theme

GREEN = QColor("#55B900")
WHITE = QColor("#FFFFFF")


def _pm(size=20, dpr=3):
    pm = QPixmap(int(size * dpr), int(size * dpr))
    pm.setDevicePixelRatio(dpr)
    pm.fill(Qt.transparent)
    return pm


def _pen(color, w=1.6):
    pen = QPen(color, w)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    return pen


def _gray():
    return QColor(_theme.colors()["muted"])


def _txt():
    return QColor(_theme.colors()["text"])


def youtube_icon(size=20):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(WHITE))
    p.drawRoundedRect(QRectF(1, 3.5, 18, 13), 4, 4)
    p.setBrush(QBrush(GREEN))
    path = QPainterPath()
    path.moveTo(8.4, 7.4)
    path.lineTo(14.2, 10)
    path.lineTo(8.4, 12.6)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(pm)


def folder_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.5))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(2.5, 15)
    path.lineTo(2.5, 4.5)
    path.lineTo(7.5, 4.5)
    path.lineTo(9.5, 6.5)
    path.lineTo(16.8, 6.5)
    path.lineTo(16.8, 15)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(pm)


def connection_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.6))
    p.setBrush(Qt.NoBrush)
    for y in (3.2, 8, 12.8):
        p.drawRoundedRect(QRectF(3, y, 14, 3.4), 1.7, 1.7)
    p.end()
    return QIcon(pm)


def sliders_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.6))
    p.drawLine(QPointF(3, 6), QPointF(17, 6))
    p.drawLine(QPointF(3, 13), QPointF(17, 13))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(_gray()))
    p.drawEllipse(QPointF(12, 6), 2.6, 2.6)
    p.drawEllipse(QPointF(6.5, 13), 2.6, 2.6)
    p.end()
    return QIcon(pm)


def bell_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.6))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(5.5, 12)
    path.quadTo(5.5, 12, 5.5, 11.5)
    path.quadTo(5.5, 5, 10, 5)
    path.quadTo(14.5, 5, 14.5, 11.5)
    path.lineTo(16, 13.5)
    path.lineTo(4, 13.5)
    path.closeSubpath()
    p.drawPath(path)
    p.drawArc(QRectF(8.6, 14.6, 2.8, 2.4), 180 * 16, 180 * 16)
    p.end()
    return QIcon(pm)


def _pm_bg():
    return QColor("#FFFFFF")


def moon_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(_gray()))
    path = QPainterPath()
    path.addEllipse(QRectF(3, 2, 13.5, 13.5))
    cut = QPainterPath()
    cut.addEllipse(QRectF(7.5, 0, 13.5, 13.5))
    p.drawPath(path.subtracted(cut))
    p.end()
    return QIcon(pm)


def sun_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.4))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(9, 9), 3.1, 3.1)
    for i in range(8):
        rad = math.radians(i * 45.0)
        p.drawLine(
            QPointF(9 + 5.2 * math.cos(rad), 9 + 5.2 * math.sin(rad)),
            QPointF(9 + 7.4 * math.cos(rad), 9 + 7.4 * math.sin(rad)),
        )
    p.end()
    return QIcon(pm)


def paste_icon(size=20):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(GREEN))
    p.setPen(_pen(WHITE, 1.6))
    p.drawRoundedRect(QRectF(4.5, 4, 11, 14), 2, 2)
    p.setBrush(QColor(GREEN))
    p.drawRoundedRect(QRectF(8, 2.2, 4, 3.8), 1, 1)
    p.setPen(_pen(WHITE, 1.6))
    p.drawRoundedRect(QRectF(8, 2.2, 4, 3.8), 1, 1)
    p.drawLine(QPointF(10, 8.5), QPointF(10, 13.5))
    p.drawLine(QPointF(8, 11.5), QPointF(10, 13.8))
    p.drawLine(QPointF(10, 13.8), QPointF(12, 11.5))
    p.end()
    return QIcon(pm)


def gear_icon(size=20):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.5))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(10, 10), 3.1, 3.1)
    for i in range(8):
        rad = math.radians(i * 45.0)
        p.drawLine(
            QPointF(10 + 5.6 * math.cos(rad), 10 + 5.6 * math.sin(rad)),
            QPointF(10 + 8.2 * math.cos(rad), 10 + 8.2 * math.sin(rad)),
        )
    p.end()
    return QIcon(pm)


def sidebar_icon(size=20):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.5))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRectF(2.2, 3.2, 15.6, 13.6), 3, 3)
    p.drawLine(QPointF(7.4, 3.6), QPointF(7.4, 16.4))
    p.end()
    return QIcon(pm)


def search_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.6))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(8, 8), 4.6, 4.6)
    p.drawLine(QPointF(11.4, 11.4), QPointF(15.4, 15.4))
    p.end()
    return QIcon(pm)


def sort_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.6))
    p.drawLine(QPointF(7, 13.5), QPointF(7, 4.5))
    p.drawLine(QPointF(4.6, 6.9), QPointF(7, 4.5))
    p.drawLine(QPointF(7, 4.5), QPointF(9.4, 6.9))
    p.drawLine(QPointF(12, 4.5), QPointF(12, 13.5))
    p.drawLine(QPointF(9.6, 11.1), QPointF(12, 13.5))
    p.drawLine(QPointF(12, 13.5), QPointF(14.4, 11.1))
    p.end()
    return QIcon(pm)


def globe_icon(size=22):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(_gray(), 1.4))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(11, 11), 7.6, 7.6)
    p.drawLine(QPointF(3.4, 11), QPointF(18.6, 11))
    p.save()
    p.translate(11, 11)
    p.scale(3.4 / 7.6, 1.0)
    p.translate(-11, -11)
    p.drawEllipse(QPointF(11, 11), 7.6, 7.6)
    p.restore()
    p.end()
    return QIcon(pm)


def dots_icon(size=18):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(_gray()))
    for y in (4.6, 10, 15.4):
        p.drawEllipse(QPointF(10, y), 1.5, 1.5)
    p.end()
    return QIcon(pm)


def chevron_down(size=9, color=None, width=1.2):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(color if color is not None else _gray(), width))
    a = QPointF(0.24 * size, 0.36 * size)
    b = QPointF(0.50 * size, 0.64 * size)
    c = QPointF(0.76 * size, 0.36 * size)
    p.drawLine(a, b)
    p.drawLine(b, c)
    p.end()
    return pm


def chevron_right(size=9, color=None, width=1.2):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(color if color is not None else _gray(), width))
    a = QPointF(0.36 * size, 0.24 * size)
    b = QPointF(0.62 * size, 0.50 * size)
    c = QPointF(0.36 * size, 0.76 * size)
    p.drawLine(a, b)
    p.drawLine(b, c)
    p.end()
    return pm


def check_icon(size=14, color=None, width=1.8):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(color if color is not None else _txt(), width))
    p.drawLine(QPointF(3, 7.5), QPointF(6, 10.5))
    p.drawLine(QPointF(6, 10.5), QPointF(11.5, 4))
    p.end()
    return pm


def key_icon(size=20, color=GREEN):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(_pen(color, 1.6))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(6.2, 10), 2.9, 2.9)
    p.drawLine(QPointF(9.1, 10), QPointF(16.6, 10))
    p.drawLine(QPointF(13.4, 10), QPointF(13.4, 12.9))
    p.drawLine(QPointF(16.2, 10), QPointF(16.2, 12.4))
    p.end()
    return QIcon(pm)


def cookie_icon(size=18, color=None):
    if color is None:
        color = _txt()
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    fill = QColor(color)
    fill.setAlpha(30)
    body = QPainterPath()
    body.addEllipse(QPointF(10.4, 10.6), 7.4, 7.4)
    bite = QPainterPath()
    bite.addEllipse(QPointF(16.9, 4.5), 3.9, 3.9)
    shape = body.subtracted(bite)
    p.fillPath(shape, QBrush(fill))
    p.strokePath(shape, _pen(color, 1.6))
    p.setPen(_pen(color, 1.0))
    p.setBrush(QBrush(color))
    for cx, cy, r in ((7.2, 8.2, 1.15), (10.8, 12.6, 1.5), (7.9, 13.6, 0.9), (12.3, 7.4, 0.75)):
        p.drawEllipse(QPointF(cx, cy), r, r)
    for cx, cy, r in ((18.7, 9.3, 0.55), (20.3, 6.9, 0.45)):
        p.drawEllipse(QPointF(cx, cy), r, r)
    p.end()
    return QIcon(pm)


def sparkle_icon(size=16, color=GREEN):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(color))
    path = QPainterPath()
    c, r = size / 2.0, size / 2.0 - 1
    k = 0.18
    path.moveTo(c, c - r)
    path.quadTo(c + k * r, c - k * r, c + r, c)
    path.quadTo(c + k * r, c + k * r, c, c + r)
    path.quadTo(c - k * r, c + k * r, c - r, c)
    path.quadTo(c - k * r, c - k * r, c, c - r)
    p.drawPath(path)
    p.end()
    return QIcon(pm)


def app_icon(size=64):
    pm = _pm(size)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(GREEN))
    p.drawRoundedRect(QRectF(2, 2, size - 4, size - 4), 14, 14)
    p.setBrush(QBrush(WHITE))
    cx, cy, r = size / 2.0, size / 2.0, size * 0.24
    path = QPainterPath()
    path.moveTo(cx - r * 0.75, cy - r)
    path.lineTo(cx + r, cy)
    path.lineTo(cx - r * 0.75, cy + r)
    path.closeSubpath()
    p.drawPath(path)
    p.end()
    return QIcon(pm)
