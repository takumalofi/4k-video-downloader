from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMenu, QWidgetAction

from app.widgets.dropdown_button import DropdownButton
from app.widgets.menu_row import MenuRow
from app import i18n


class ModeDropdown(DropdownButton):
    modeChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(i18n.tr("download"), i18n.tr("video"), parent)
        self._mode = "video"
        self._build_menu()
        self.setMenu(self._menu)

    def mode(self):
        return self._mode

    def restore(self, mode):
        self._mode = mode
        self._row_video.set_checked(mode == "video")
        self._row_audio.set_checked(mode == "audio")
        self.set_value(i18n.tr("video") if mode == "video" else i18n.tr("audio"))

    def _build_menu(self):
        menu = QMenu(self)
        menu.setMinimumWidth(210)

        self._row_video = MenuRow(i18n.tr("video"))
        wa_video = QWidgetAction(menu)
        wa_video.setDefaultWidget(self._row_video)
        menu.addAction(wa_video)

        self._row_audio = MenuRow(i18n.tr("audio"))
        wa_audio = QWidgetAction(menu)
        wa_audio.setDefaultWidget(self._row_audio)
        menu.addAction(wa_audio)

        self._row_video.clicked.connect(lambda: self._select("video"))
        self._row_audio.clicked.connect(lambda: self._select("audio"))
        self._row_video.set_checked(True)
        self._menu = menu

    def _select(self, mode):
        self._mode = mode
        self._row_video.set_checked(mode == "video")
        self._row_audio.set_checked(mode == "audio")
        self.set_value(i18n.tr("video") if mode == "video" else i18n.tr("audio"))
        self.modeChanged.emit(mode)
        self._menu.hide()
