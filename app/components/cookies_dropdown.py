from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QWidgetAction

from app.widgets.dropdown_button import DropdownButton
from app.widgets.menu_row import MenuRow
from app import i18n

BROWSERS = ("None", "Chrome", "Firefox", "Edge", "Brave", "Safari", "Opera")


class CookiesDropdown(DropdownButton):
    cookiesChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(i18n.tr("cookies_short"), "None", parent)
        self._browser = "None"
        self._rows = {}
        self._build_menu()
        self.setMenu(self._menu)

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
        self.set_value(name)
