from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from app.components.download_item import DownloadItem
from app.components.context_menu import show_item_menu

_TAB_FILTER = {
    "All": None,
    "Video": "video",
    "Audio": "audio",
    "Playlists": "playlist",
    "Channels": "channel",
}


class DownloadList(QWidget):
    countChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._tab = "All"
        self._search = ""
        self._desc = True
        self.host = None

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 10, 16, 16)
        self._lay.setSpacing(8)
        self._lay.addStretch()

    def items(self):
        return list(self._items)

    def add_download(self, url, kind):
        item = DownloadItem(url, kind)
        item.removed.connect(self._remove)
        item.more_btn.clicked.connect(
            lambda checked=False, it=item: show_item_menu(
                it,
                it.more_btn.mapToGlobal(it.more_btn.rect().bottomLeft()),
                self.host,
            )
        )
        self._items.insert(0, item)
        self._relayout()
        self._apply_filter()
        self.countChanged.emit(len(self._items))
        return item

    def set_tab(self, tab):
        self._tab = tab
        self._apply_filter()

    def set_search(self, text):
        self._search = text.lower()
        self._apply_filter()

    def set_order_desc(self, desc):
        self._desc = desc
        self._relayout()

    def toggle_order(self):
        self.set_order_desc(not self._desc)

    def _remove(self, item):
        if item in self._items:
            self._items.remove(item)
            item.setParent(None)
            item.deleteLater()
            self._relayout()
            self._apply_filter()
            self.countChanged.emit(len(self._items))

    def _relayout(self):
        while self._lay.count():
            self._lay.takeAt(0)
        items = list(reversed(self._items)) if self._desc else list(self._items)
        for item in items:
            self._lay.addWidget(item)
        self._lay.addStretch()

    def _apply_filter(self):
        allowed = _TAB_FILTER.get(self._tab)
        for item in self._items:
            match_tab = allowed is None or item.kind == allowed
            match_search = self._search in item.url.lower()
            item.setVisible(match_tab and match_search)
