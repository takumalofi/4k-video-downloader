import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMenu, QFileDialog

from app.widgets.dropdown_button import DropdownButton
from app import i18n


class SaveLocationDropdown(DropdownButton):
    locationChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(i18n.tr("save_to"), "D:/", parent)
        self._path = "D:/"
        menu = QMenu(self)
        act_d = menu.addAction("D:/")
        act_d.triggered.connect(lambda: self._pick("D:/"))
        act_dl = menu.addAction(os.path.expanduser("~/Downloads"))
        act_dl.triggered.connect(lambda: self._pick(os.path.expanduser("~/Downloads")))
        menu.addSeparator()
        act_browse = menu.addAction("Browse...")
        act_browse.triggered.connect(self._browse)
        self.setMenu(menu)

    def _pick(self, path):
        self._path = path
        self.set_value(self._short(path))
        self.locationChanged.emit(path)

    def _browse(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select download folder", self._path)
        if chosen:
            self._pick(os.path.normpath(chosen))

    def _short(self, path):
        path = path.replace("\\", "/")
        if len(path) > 12:
            return path[:10] + "…/"
        return path
