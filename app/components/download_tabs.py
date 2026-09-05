from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QLineEdit

from app.icons import search_icon, sort_icon
from app import theme
from app import i18n

TAB_KEYS = ["All", "Video", "Audio", "Playlists", "Channels"]
_TAB_I18N = {
    "All": "all",
    "Video": "video",
    "Audio": "audio",
    "Playlists": "playlists",
    "Channels": "channels",
}


def _tab_qss(c):
    return f"""
QFrame#tabsRow {{ background:{c['panel']}; border-bottom:1px solid {c['border_soft']}; }}
QPushButton[tabBtn="true"] {{
    border:none; background:transparent; color:{c['muted']};
    padding:13px 8px 15px; border-bottom:3px solid transparent; font-size:14px;
}}
QPushButton[tabBtn="true"][active="true"] {{
    color:{c['text_strong']}; font-weight:600; border-bottom:3px solid #55B900;
}}
QPushButton[tabBtn="true"]:hover {{ color:{c['text']}; }}
"""


class DownloadTabs(QFrame):
    tabChanged = Signal(str)
    searchChanged = Signal(str)
    sortToggled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("tabsRow")
        self.setFixedHeight(48)
        self.setStyleSheet(_tab_qss(theme.colors()))
        self._active = "All"
        self._desc = False

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(2)

        self._tab_buttons = {}
        for key in TAB_KEYS:
            btn = QPushButton(i18n.tr(_TAB_I18N[key]))
            btn.setProperty("tabBtn", True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(48)
            btn.clicked.connect(lambda checked=False, n=key: self.set_active(n))
            lay.addWidget(btn)
            self._tab_buttons[key] = btn
        self._sync_tab_styles()

        lay.addStretch()

        self.count_label = QLabel("1 item")
        self.count_label.setStyleSheet(
            f"color:{theme.colors()['muted']}; font-size:13px;"
            " padding-right:2px; background:transparent;"
        )
        self.count_label.setFixedHeight(48)
        self.count_label.setAlignment(Qt.AlignVCenter)
        lay.addWidget(self.count_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search")
        self.search_edit.setFixedWidth(150)
        self.search_edit.setVisible(False)
        self.search_edit.textChanged.connect(self.searchChanged.emit)
        lay.addWidget(self.search_edit)

        self.search_btn = QPushButton()
        self.search_btn.setObjectName("ghostBtn")
        self.search_btn.setFixedSize(30, 30)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setIcon(search_icon(17))
        self.search_btn.setToolTip("Search")
        self.search_btn.clicked.connect(self._toggle_search)
        lay.addWidget(self.search_btn)

        self.sort_btn = QPushButton()
        self.sort_btn.setObjectName("ghostBtn")
        self.sort_btn.setFixedSize(30, 30)
        self.sort_btn.setCursor(Qt.PointingHandCursor)
        self.sort_btn.setIcon(sort_icon(17))
        self.sort_btn.setToolTip("Sort")
        self.sort_btn.clicked.connect(self._toggle_sort)
        lay.addWidget(self.sort_btn)

    def active_tab(self):
        return self._active

    def set_active(self, name):
        self._active = name
        self._sync_tab_styles()
        self.tabChanged.emit(name)

    def set_count(self, count):
        self.count_label.setText(i18n.items_label(count))

    def retheme(self):
        c = theme.colors()
        self.setStyleSheet(_tab_qss(c))
        self.count_label.setStyleSheet(
            f"color:{c['muted']}; font-size:13px;"
            " padding-right:2px; background:transparent;"
        )
        self.search_btn.setIcon(search_icon(17))
        self.sort_btn.setIcon(sort_icon(17))

    def _toggle_search(self):
        self.search_edit.setVisible(not self.search_edit.isVisible())
        if self.search_edit.isVisible():
            self.search_edit.setFocus()
        else:
            self.search_edit.clear()

    def _toggle_sort(self):
        self._desc = not self._desc
        self.sortToggled.emit()

    def _sync_tab_styles(self):
        for name, btn in self._tab_buttons.items():
            btn.setProperty("active", "true" if name == self._active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
