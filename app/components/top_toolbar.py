from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout

from app.components.paste_link_button import PasteLinkButton
from app.components.mode_dropdown import ModeDropdown
from app.components.quality_dropdown import QualityDropdown
from app.components.platform_dropdown import PlatformDropdown
from app.components.save_location_dropdown import SaveLocationDropdown
from app.components.theme_toggle_button import ThemeToggleButton
from app import theme


class TopToolbar(QFrame):
    pasteRequested = Signal()
    modeChanged = Signal(str)
    qualityChanged = Signal(str)
    platformChanged = Signal(str)
    locationChanged = Signal(str)
    settingsRequested = Signal()

    def __init__(self, parent=None, prefs=None):
        super().__init__(parent)
        self.setObjectName("topToolbar")
        self.setFixedHeight(70)
        self.setStyleSheet(
            "QFrame#topToolbar { background:#FFFFFF; border-bottom:1px solid #ECECEC; }"
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(16)

        self.paste_btn = PasteLinkButton()
        self.paste_btn.clicked.connect(self.pasteRequested.emit)
        lay.addWidget(self.paste_btn)
        lay.addSpacing(2)

        self.mode_dd = ModeDropdown()
        self.mode_dd.modeChanged.connect(self.modeChanged.emit)
        lay.addWidget(self.mode_dd)

        self.quality_dd = QualityDropdown()
        self.quality_dd.qualityChanged.connect(self.qualityChanged.emit)
        self.mode_dd.modeChanged.connect(self.quality_dd.set_mode)
        lay.addWidget(self.quality_dd)

        self.platform_dd = PlatformDropdown()
        self.platform_dd.platformChanged.connect(self.platformChanged.emit)
        lay.addWidget(self.platform_dd)

        self.save_dd = SaveLocationDropdown()
        self.save_dd.locationChanged.connect(self.locationChanged.emit)
        lay.addWidget(self.save_dd)

        lay.addStretch()

        self.theme_btn = ThemeToggleButton()
        lay.addWidget(self.theme_btn)

    def retheme(self):
        c = theme.colors()
        self.setStyleSheet(
            "QFrame#topToolbar {"
            f" background:{c['panel']}; border-bottom:1px solid {c['border_soft']};"
            " }"
        )
