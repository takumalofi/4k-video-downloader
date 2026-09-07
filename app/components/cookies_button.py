from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import QPushButton, QMenu, QWidgetAction

from app.icons import cookie_icon, _txt
from app.widgets.menu_row import MenuRow
from app import i18n

BROWSERS = ("None", "Chrome", "Firefox", "Edge", "Brave", "Safari", "Opera")


class CookiesButton(QPushButton):
    cookiesChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ghostBtn")
        self.setFocusPolicy(Qt.NoFocus)
        self.setFixedSize(34, 34)
        self.setCursor(Qt.PointingHandCursor)
        self._browser = "None"
        self._rows = {}
        self._build_menu()
        self.clicked.connect(self._open_menu)
        self._update()

    def _open_menu(self):
        self._menu.exec(self.mapToGlobal(QPoint(0, self.height() + 4)))

    def restore(self, browser):
        self._apply(browser)

    def browser(self):
        return self._browser

    def _build_menu(self):
        menu = QMenu(self)
        menu.setMinimumWidth(190)
        for name in BROWSERS:
            row = MenuRow(name)
            wa = QWidgetAction(menu)
            wa.setDefaultWidget(row)
            menu.addAction(wa)
            row.clicked.connect(lambda n=name: self._select(n))
            self._rows[name] = row
        self._menu = menu

    def _select(self, name):
        self._apply(name)
        self.cookiesChanged.emit(name)
        self._menu.hide()

    def _apply(self, name):
        self._browser = name
        for n, row in self._rows.items():
            row.set_checked(n == name)
        self._update()

    def _update(self):
        self.setIcon(cookie_icon(18, _txt()))
        self.setToolTip(f"{i18n.tr('cookies_short')}: {self._browser}")

    def retheme(self):
        self._update()
