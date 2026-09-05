from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QSizePolicy

from app.components.download_tabs import DownloadTabs
from app.components.download_list import DownloadList


class ContentArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:#FFFFFF;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.tabs = DownloadTabs()
        lay.addWidget(self.tabs)

        self.list = DownloadList()
        self.list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll = scroll
        self._apply_style()
        scroll.setWidget(self.list)
        lay.addWidget(scroll, 1)

    def retheme(self):
        self._apply_style()

    def _apply_style(self):
        from app import theme
        c = theme.colors()
        self.setStyleSheet(f"background:{c['bg']};")
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background:{c['bg']}; border:none; }}"
        )
