import os
import threading

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QComboBox,
    QStackedWidget,
    QWidget,
    QFrame,
    QSizePolicy,
    QFileDialog,
)

from app import theme
from app import i18n
from app.icons import gear_icon, sliders_icon, bell_icon, connection_icon
from app.widgets.toggle_switch import ToggleSwitch
from engine import yt_dlp_binary

BROWSER_CHOICES = ("None", "Chrome", "Firefox", "Edge", "Brave", "Safari", "Opera")
SPEED_CHOICES = ("Unlimited", "1M", "2M", "5M", "10M")


class SettingsPanel(QDialog):
    updateFinished = Signal(bool, str)
    connectionSaved = Signal(dict)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.tr("settings"))
        self.setModal(True)
        self.setFixedSize(620, 540)
        self.settings = dict(settings)
        self._snapshot_connection()

        c = theme.colors()
        self.setStyleSheet(
            f"QDialog {{ background:{c['panel']}; }}"
            "QComboBox { background:#FFFFFF; border:1px solid #D9D9D9;"
            " border-radius:4px; padding:5px 10px; color:#111418; font-size:13px; }"
            "QComboBox::drop-down { border:none; width:26px; }"
            "QComboBox QAbstractItemView { background:#FFFFFF; color:#111418;"
            " selection-background-color:#F1F2F3; selection-color:#111418; }"
            "QLineEdit { background:#FFFFFF; border:1px solid #D9D9D9;"
            " border-radius:4px; padding:5px 10px; color:#111418; font-size:13px; }"
            "QPushButton#settingsBtn { background:#F1F2F3; border:1px solid #DDDFE2;"
            " border-radius:4px; padding:6px 14px; color:#111418; font-size:13px; }"
            "QPushButton#settingsBtn:hover { background:#E8EAEC; }"
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._sidebar = QFrame()
        self._sidebar.setFixedWidth(180)
        self._sidebar.setStyleSheet(
            f"QFrame {{ background:{c['panel2']}; border:none; }}"
        )
        side_lay = QVBoxLayout(self._sidebar)
        side_lay.setContentsMargins(10, 14, 10, 14)
        side_lay.setSpacing(2)

        self._side_buttons = {}
        pages = [
            ("general", i18n.tr("general"), gear_icon(18)),
            ("advanced", i18n.tr("advanced"), sliders_icon(18)),
            ("connection", i18n.tr("connection"), connection_icon(18)),
            ("notification", i18n.tr("notification"), bell_icon(18)),
        ]
        for key, label, icon in pages:
            btn = QPushButton("  " + label)
            btn.setIcon(icon)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(36)
            btn.setStyleSheet(
                "QPushButton { text-align:left; border:none; border-radius:4px;"
                " background:transparent; color:#111418; font-size:14px;"
                " padding:6px 8px; }"
                "QPushButton:checked { background:%s; font-weight:700; color:#000000; }"
                "QPushButton:hover:!checked { background:%s; }"
                % (c["hover"], c["menu_hover"])
            )
            btn.clicked.connect(lambda checked=False, k=key: self._switch_page(k))
            side_lay.addWidget(btn)
            self._side_buttons[key] = btn
        side_lay.addStretch()
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        content.addWidget(self._sidebar)
        self._stack = QStackedWidget()
        content.addWidget(self._stack, 1)
        root.addLayout(content, 1)

        self._stack.addWidget(self._page_general())
        self._stack.addWidget(self._page_advanced())
        self._stack.addWidget(self._page_connection())
        self._stack.addWidget(self._page_notification())

        self._side_buttons["general"].setChecked(True)

        self._bottom_bar = QWidget()
        bottom = QHBoxLayout(self._bottom_bar)
        bottom.setContentsMargins(20, 10, 20, 12)
        bottom.addStretch()
        cancel_btn = QPushButton(i18n.tr("cancel"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedSize(90, 32)
        cancel_btn.setStyleSheet(
            f"QPushButton {{ background:{c['hover']}; color:{c['text']}; border:none;"
            " border-radius:4px; font-size:13px; }"
        )
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedSize(90, 32)
        ok_btn.setStyleSheet(
            f"QPushButton {{ background:{theme.PRIMARY}; color:#FFFFFF; border:none;"
            " border-radius:4px; font-size:13px; }"
            f"QPushButton:hover {{ background:{theme.PRIMARY_HOVER}; }}"
        )
        ok_btn.clicked.connect(self._apply)
        bottom.addWidget(cancel_btn)
        bottom.addWidget(ok_btn)
        root.addWidget(self._bottom_bar)

    def _switch_page(self, key):
        index = {"general": 0, "advanced": 1, "connection": 2, "notification": 3}[key]
        self._stack.setCurrentIndex(index)
        for k, btn in self._side_buttons.items():
            btn.setChecked(k == key)
        self._bottom_bar.setVisible(key != "connection")

    def _page_title(self, text):
        title = QLabel(text)
        title.setStyleSheet(
            "color:#000000; font-size:18px; font-weight:600;"
            " background:transparent;"
        )
        return title

    def _new_page(self, page_title):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)
        lay.addWidget(self._page_title(page_title))
        return page, lay

    @staticmethod
    def _separator():
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{theme.colors()['border_soft']}; border:none;")
        return line

    def _page_general(self):
        c = theme.colors()
        page, lay = self._new_page(i18n.tr("general"))

        lang_label = QLabel(i18n.tr("language"))
        lang_label.setFixedWidth(150)
        lang_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        self.language = QComboBox()
        self.language.addItems(("English", "Tiếng Việt"))
        self.language.setCurrentText(
            "Tiếng Việt" if self.settings.get("language", "en") == "vi" else "English"
        )
        self.language.setFixedWidth(234)
        lang_row = QHBoxLayout()
        lang_row.setContentsMargins(0, 0, 0, 0)
        lang_row.setSpacing(8)
        lang_row.addWidget(lang_label)
        lang_row.addStretch()
        lang_row.addWidget(self.language)
        lay.addLayout(lang_row)
        lay.addWidget(self._separator())

        folder_label = QLabel(i18n.tr("save_to"))
        folder_label.setFixedWidth(150)
        folder_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        self.folder_edit = QLineEdit(self.settings.get("save_folder", "D:/"))
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setCursor(Qt.PointingHandCursor)
        self.folder_edit.setToolTip("Click to choose folder")
        self.folder_edit.installEventFilter(self)
        folder_row = QHBoxLayout()
        folder_row.setContentsMargins(0, 0, 0, 0)
        folder_row.setSpacing(8)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(self.folder_edit, 1)
        lay.addLayout(folder_row)
        lay.addWidget(self._separator())

        self.autostart_toggle = ToggleSwitch()
        self.autostart_toggle.setChecked(bool(self.settings.get("autostart", True)))
        self._add_toggle_row(lay, i18n.tr("autostart_on_paste"), self.autostart_toggle)
        lay.addWidget(self._separator())

        self.engine_label = QLabel(f"yt-dlp {yt_dlp_binary.get_version() or 'not found'}")
        self.engine_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        self.update_btn = QPushButton(i18n.tr("update_engine"))
        self.update_btn.setObjectName("settingsBtn")
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.clicked.connect(self._start_engine_update)
        engine_row = QHBoxLayout()
        engine_row.setContentsMargins(0, 0, 0, 0)
        engine_row.setSpacing(8)
        engine_row.addWidget(self.engine_label)
        engine_row.addStretch()
        engine_row.addWidget(self.update_btn)
        lay.addLayout(engine_row)
        lay.addStretch()
        return page

    def _page_advanced(self):
        c = theme.colors()
        page, lay = self._new_page(i18n.tr("advanced"))

        par_label = QLabel(i18n.tr("parallel_downloads"))
        par_label.setFixedWidth(150)
        par_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        self.parallel = QComboBox()
        self.parallel.addItems(("1", "2", "3", "4", "5"))
        self.parallel.setCurrentText(str(int(self.settings.get("parallel", 2))))
        self.parallel.setFixedWidth(240)
        par_row = QHBoxLayout()
        par_row.setContentsMargins(0, 0, 0, 0)
        par_row.setSpacing(8)
        par_row.addWidget(par_label)
        par_row.addStretch()
        par_row.addWidget(self.parallel)
        lay.addLayout(par_row)
        lay.addWidget(self._separator())

        cookies_label = QLabel(i18n.tr("cookies_from"))
        cookies_label.setFixedWidth(150)
        cookies_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        self.cookies = QComboBox()
        self.cookies.addItems(BROWSER_CHOICES)
        current = self.settings.get("cookies_browser", "None")
        if current not in BROWSER_CHOICES:
            current = "None"
        self.cookies.setCurrentText(current)
        self.cookies.setFixedWidth(240)
        cookies_row = QHBoxLayout()
        cookies_row.setContentsMargins(0, 0, 0, 0)
        cookies_row.setSpacing(8)
        cookies_row.addWidget(cookies_label)
        cookies_row.addStretch()
        cookies_row.addWidget(self.cookies)
        lay.addLayout(cookies_row)
        lay.addStretch()
        return page

    def _proxy_row(self, label_text, widget):
        c = theme.colors()
        label = QLabel(label_text)
        label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        widget.setFixedSize(240, 32)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(label)
        row.addStretch()
        row.addWidget(widget)
        return row

    def _snapshot_connection(self):
        self._conn_snapshot = {
            "speed_limit": self.settings.get("speed_limit", "Unlimited"),
            "proxy_enabled": self.settings.get("proxy_enabled", False),
            "proxy_type": self.settings.get("proxy_type", "http"),
            "proxy_host": self.settings.get("proxy_host", ""),
            "proxy_port": self.settings.get("proxy_port", ""),
            "proxy_login": self.settings.get("proxy_login", ""),
            "proxy_password": self.settings.get("proxy_password", ""),
        }

    def _page_connection(self):
        c = theme.colors()
        page, lay = self._new_page(i18n.tr("connection"))
        conn_lay = lay

        speed_label = QLabel(i18n.tr("speed_limit"))
        speed_label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        conn_lay.addWidget(speed_label)

        self.speed = QComboBox()
        self.speed.addItems(SPEED_CHOICES)
        self.speed.setCurrentText(self._conn_snapshot["speed_limit"])
        self.speed.setFixedWidth(240)
        conn_lay.addWidget(self.speed)

        hint = QLabel(i18n.tr("speed_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color:{c['muted']}; font-size:11px; background:transparent;")
        conn_lay.addWidget(hint)
        conn_lay.addSpacing(8)
        conn_lay.addWidget(self._separator())
        conn_lay.addSpacing(4)

        self.proxy_toggle = ToggleSwitch()
        self.proxy_toggle.setChecked(self._conn_snapshot["proxy_enabled"])
        proxy_box = QFrame()
        proxy_box.setStyleSheet(
            f"QFrame {{ background:{c['panel2']}; border:none; border-radius:4px; }}"
        )
        proxy_lay = QVBoxLayout(proxy_box)
        proxy_lay.setContentsMargins(16, 10, 16, 14)
        proxy_lay.setSpacing(12)

        proxy_toggle_row = QHBoxLayout()
        proxy_toggle_row.setContentsMargins(0, 0, 0, 0)
        proxy_title = QLabel(i18n.tr("enable_proxy"))
        proxy_title.setStyleSheet(
            f"color:{c['text']}; font-size:13px; font-weight:600; background:transparent;"
        )
        proxy_toggle_row.addWidget(proxy_title)
        proxy_toggle_row.addStretch()
        proxy_toggle_row.addWidget(self.proxy_toggle)
        proxy_lay.addLayout(proxy_toggle_row)

        self.proxy_fields = QWidget()
        fields_lay = QVBoxLayout(self.proxy_fields)
        fields_lay.setContentsMargins(0, 0, 0, 0)
        fields_lay.setSpacing(12)

        self.proxy_type = QComboBox()
        self.proxy_type.addItems(("http", "https", "socks4", "socks5"))
        self.proxy_type.setCurrentText(self._conn_snapshot["proxy_type"])
        fields_lay.addLayout(self._proxy_row(i18n.tr("proxy_type"), self.proxy_type))

        self.proxy_host = QLineEdit(self._conn_snapshot["proxy_host"])
        self.proxy_host.setPlaceholderText("proxy.example.com")
        fields_lay.addLayout(self._proxy_row(i18n.tr("host"), self.proxy_host))

        self.proxy_port = QLineEdit(self._conn_snapshot["proxy_port"])
        self.proxy_port.setPlaceholderText("8080")
        from PySide6.QtGui import QIntValidator
        self.proxy_port.setValidator(QIntValidator(1, 65535))
        fields_lay.addLayout(self._proxy_row(i18n.tr("port"), self.proxy_port))

        self.proxy_login = QLineEdit(self._conn_snapshot["proxy_login"])
        fields_lay.addLayout(self._proxy_row(i18n.tr("login"), self.proxy_login))

        self.proxy_password = QLineEdit(self._conn_snapshot["proxy_password"])
        self.proxy_password.setEchoMode(QLineEdit.Password)
        fields_lay.addLayout(self._proxy_row(i18n.tr("password"), self.proxy_password))

        proxy_lay.addWidget(self.proxy_fields)

        conn_btn_row = QHBoxLayout()
        conn_btn_row.setContentsMargins(0, 2, 0, 0)
        conn_btn_row.setSpacing(12)
        self.proxy_cancel_btn = QPushButton(i18n.tr("cancel"))
        self.proxy_cancel_btn.setCursor(Qt.PointingHandCursor)
        self.proxy_cancel_btn.setFixedHeight(38)
        self.proxy_cancel_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{c['text']}; border:none;"
            " font-size:13px; }"
            f"QPushButton:hover {{ background:{c['hover']}; border-radius:4px; }}"
        )
        self.proxy_cancel_btn.clicked.connect(self._cancel_connection)
        self.proxy_save_btn = QPushButton(i18n.tr("save"))
        self.proxy_save_btn.setCursor(Qt.PointingHandCursor)
        self.proxy_save_btn.setFixedHeight(38)
        self.proxy_save_btn.setStyleSheet(
            f"QPushButton {{ background:{theme.PRIMARY}; color:#FFFFFF; border:none;"
            " border-radius:4px; font-size:13px; }"
            f"QPushButton:hover {{ background:{theme.PRIMARY_HOVER}; }}"
        )
        self.proxy_save_btn.clicked.connect(self._save_connection)
        conn_btn_row.addWidget(self.proxy_cancel_btn, 1)
        conn_btn_row.addWidget(self.proxy_save_btn, 2)
        proxy_lay.addLayout(conn_btn_row)

        self.proxy_fields.setVisible(self.proxy_toggle.isChecked())
        self.proxy_cancel_btn.setVisible(self.proxy_toggle.isChecked())
        self.proxy_save_btn.setVisible(self.proxy_toggle.isChecked())
        self.proxy_toggle.toggled.connect(self._on_proxy_toggled)
        conn_lay.addWidget(proxy_box)
        conn_lay.addStretch()
        return page

    def _on_proxy_toggled(self, checked):
        self.proxy_fields.setVisible(checked)
        self.proxy_cancel_btn.setVisible(checked)
        self.proxy_save_btn.setVisible(checked)

    def _save_connection(self):
        if self.proxy_toggle.isChecked():
            host = self.proxy_host.text().strip()
            port = self.proxy_port.text().strip()
            if not host or not port:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    i18n.tr("enable_proxy"),
                    i18n.tr("invalid_link"),
                )
                return
        self.settings["speed_limit"] = self.speed.currentText()
        self.settings["proxy_enabled"] = self.proxy_toggle.isChecked()
        self.settings["proxy_type"] = self.proxy_type.currentText()
        self.settings["proxy_host"] = self.proxy_host.text().strip()
        self.settings["proxy_port"] = self.proxy_port.text().strip()
        self.settings["proxy_login"] = self.proxy_login.text()
        self.settings["proxy_password"] = self.proxy_password.text()
        self._snapshot_connection()
        self.connectionSaved.emit(dict(self.settings))

    def _cancel_connection(self):
        self.speed.setCurrentText(self._conn_snapshot["speed_limit"])
        self.proxy_toggle.setChecked(self._conn_snapshot["proxy_enabled"])
        self.proxy_type.setCurrentText(self._conn_snapshot["proxy_type"])
        self.proxy_host.setText(self._conn_snapshot["proxy_host"])
        self.proxy_port.setText(self._conn_snapshot["proxy_port"])
        self.proxy_login.setText(self._conn_snapshot["proxy_login"])
        self.proxy_password.setText(self._conn_snapshot["proxy_password"])

    def _page_notification(self):
        page, lay = self._new_page(i18n.tr("notification"))

        self.notify_finished = ToggleSwitch()
        self.notify_finished.setChecked(bool(self.settings.get("notify_finished", True)))
        self._add_toggle_row(lay, i18n.tr("notify_finished"), self.notify_finished)

        self.notify_sound = ToggleSwitch()
        self.notify_sound.setChecked(bool(self.settings.get("notify_sound", True)))
        self._add_toggle_row(lay, i18n.tr("notify_sound"), self.notify_sound)
        lay.addWidget(self._separator())

        self.confirm_exit = ToggleSwitch()
        self.confirm_exit.setChecked(bool(self.settings.get("confirm_exit", True)))
        self._add_toggle_row(lay, i18n.tr("confirm_exit"), self.confirm_exit)
        lay.addStretch()
        return page

    def _add_toggle_row(self, lay, text, toggle):
        c = theme.colors()
        label = QLabel(text)
        label.setStyleSheet(f"color:{c['text']}; font-size:13px; background:transparent;")
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(label)
        row.addStretch()
        row.addWidget(toggle)
        lay.addLayout(row)

    def eventFilter(self, obj, event):
        if obj is self.folder_edit and event.type() == QEvent.MouseButtonPress:
            chosen = QFileDialog.getExistingDirectory(
                self, "Select download folder", self.folder_edit.text()
            )
            if chosen:
                self.folder_edit.setText(os.path.normpath(chosen))
            return True
        return super().eventFilter(obj, event)

    def _apply(self):
        self.settings["save_folder"] = self.folder_edit.text()
        self.settings["parallel"] = int(self.parallel.currentText())
        self.settings["autostart"] = self.autostart_toggle.isChecked()
        self.settings["cookies_browser"] = self.cookies.currentText()
        self.settings["speed_limit"] = self.speed.currentText()
        self.settings["language"] = (
            "vi" if self.language.currentText() == "Tiếng Việt" else "en"
        )
        self.settings["notify_finished"] = self.notify_finished.isChecked()
        self.settings["notify_sound"] = self.notify_sound.isChecked()
        self.settings["confirm_exit"] = self.confirm_exit.isChecked()
        self.settings["proxy_enabled"] = self.proxy_toggle.isChecked()
        self.settings["proxy_type"] = self.proxy_type.currentText()
        self.settings["proxy_host"] = self.proxy_host.text().strip()
        self.settings["proxy_port"] = self.proxy_port.text().strip()
        self.settings["proxy_login"] = self.proxy_login.text()
        self.settings["proxy_password"] = self.proxy_password.text()
        self.accept()

    def _start_engine_update(self):
        self.update_btn.setEnabled(False)
        self.update_btn.setText("Updating...")
        threading.Thread(target=self._engine_update_worker, daemon=True).start()

    def _engine_update_worker(self):
        ok, msg = yt_dlp_binary.update()
        self.updateFinished.emit(ok, msg)

    def _on_engine_update_finished(self, ok, msg):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("Update engine")
        version = yt_dlp_binary.get_version()
        self.engine_label.setText(f"yt-dlp {version or 'not found'}")
        from PySide6.QtWidgets import QMessageBox
        if ok:
            QMessageBox.information(
                self, "Update engine",
                (msg or "Engine updated.") + f"\n\nCurrent version: {version}",
            )
        else:
            QMessageBox.warning(self, "Update engine", msg or "Update failed.")
