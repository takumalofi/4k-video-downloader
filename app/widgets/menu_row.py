from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout

from app.icons import check_icon


class MenuRow(QFrame):
    clicked = Signal()

    def __init__(self, text, right="none", icon=None, value=None, height=40, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_Hover)
        self.setFixedHeight(height)
        self.setCursor(Qt.PointingHandCursor)
        self._hover = False
        self._right = right
        self._checked = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 12, 0)
        lay.setSpacing(8)

        self._text = QLabel(text)
        self._text.setStyleSheet(self._text_style())
        lay.addWidget(self._text)
        if icon is not None:
            ic = QLabel()
            ic.setPixmap(icon.pixmap(16, 16))
            ic.setStyleSheet("background:transparent;")
            ic.setFixedSize(16, 16)
            ic.setScaledContents(True)
            lay.addWidget(ic)

        lay.addStretch()

        self._badge = None
        if value is not None:
            self._badge = QLabel(value)
            self._badge.setStyleSheet(self._badge_style())
            lay.addWidget(self._badge)

        if right == "chevron":
            extra = QLabel()
            extra.setPixmap(_gray_chevron())
            extra.setStyleSheet("background:transparent;")
            extra.setFixedSize(9, 9)
            extra.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lay.addSpacing(-2)
            lay.addWidget(extra)

        self._right_label = QLabel()
        self._right_label.setStyleSheet("background:transparent;")
        self._right_label.setFixedWidth(16)
        self._right_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(self._right_label)

        self._update_style()

    def set_checked(self, checked):
        self._checked = checked
        if checked:
            self._right_label.setPixmap(check_icon(14))
        else:
            self._right_label.clear()
        self._right_label.setFixedWidth(16)

    def set_value(self, value):
        if self._badge is not None:
            self._badge.setText(value)

    def retheme(self):
        self._text.setStyleSheet(self._text_style())
        if self._badge is not None:
            self._badge.setStyleSheet(self._badge_style())
        self._update_style()
        if self._right == "check":
            self.set_checked(self._checked)

    def _text_style(self):
        from app import theme
        return f"color:{theme.colors()['text']}; font-size:14px; background:transparent;"

    def _badge_style(self):
        from app import theme
        c = theme.colors()
        return (
            f"color:{c['text']}; font-size:12px; background:{c['hover']};"
            " border-radius:3px; padding:1px 5px;"
        )

    def enterEvent(self, event):
        self._hover = True
        self._update_style()

    def leaveEvent(self, event):
        self._hover = False
        self._update_style()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def _update_style(self):
        from app import theme
        bg = theme.colors()["menu_hover"] if self._hover else "transparent"
        self.setStyleSheet(f"MenuRow {{ background:{bg}; border:none; }}")


def _gray_chevron():
    from app.icons import chevron_right
    return chevron_right(9)
