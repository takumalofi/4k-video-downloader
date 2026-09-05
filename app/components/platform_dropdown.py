from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMenu

from app.widgets.dropdown_button import DropdownButton
from app import i18n


class PlatformDropdown(DropdownButton):
    platformChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(i18n.tr("for_"), "Windows", parent)
        menu = QMenu(self)
        for p in ("Windows", "macOS", "Linux"):
            act = menu.addAction(p)
            act.triggered.connect(lambda checked=False, name=p: self._pick(name))
        self.setMenu(menu)

    def _pick(self, name):
        self.set_value(name)
        self.platformChanged.emit(name)
