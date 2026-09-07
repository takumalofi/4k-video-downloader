import os
import re
import uuid

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QActionGroup, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QSystemTrayIcon,
)

from app.components.top_toolbar import TopToolbar
from app.components.content_area import ContentArea
from app.components.status_bar import StatusBar
from app.components.settings_panel import SettingsPanel
from app.components.link_dialog import LinkDialog, extract_url
from app.components.delete_confirm_dialog import confirm_delete
from app.icons import app_icon
from app import i18n
from app.preferences import load_prefs, save_prefs
from engine import YtDlpEngine
from engine.yt_dlp_engine import fmt_speed


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selections = load_prefs()
        i18n.set_language(self.selections.get("language", "en"))

        self.setWindowTitle("4K Video Downloader+")
        self.setWindowIcon(app_icon(64))
        self.resize(950, 650)
        self.setMinimumSize(950, 650)

        self.mode = self.selections.get("mode", "video")
        self.quality = self.selections.get("video_quality", "720p")
        self.fps = self.selections.get("fps", "Highest")
        self.video_codec = self.selections.get("video_codec", "H264")
        self.audio_codec = self.selections.get("audio_codec", "Auto")
        self.platform = self.selections.get("platform", "Windows")
        self.save_location = self.selections.get("save_location", "D:/")
        self.settings = {
            "save_folder": self.save_location,
            "parallel": int(self.selections.get("parallel", 2)),
            "autostart": self.selections.get("autostart", True),
            "cookies_browser": self.selections.get("cookies_browser", "None"),
            "language": self.selections.get("language", "en"),
            "speed_limit": self.selections.get("speed_limit", "Unlimited"),
            "notify_finished": self.selections.get("notify_finished", True),
            "notify_sound": self.selections.get("notify_sound", True),
            "confirm_exit": self.selections.get("confirm_exit", True),
            "proxy_enabled": self.selections.get("proxy_enabled", False),
            "proxy_type": self.selections.get("proxy_type", "http"),
            "proxy_host": self.selections.get("proxy_host", ""),
            "proxy_port": self.selections.get("proxy_port", ""),
            "proxy_login": self.selections.get("proxy_login", ""),
            "proxy_password": self.selections.get("proxy_password", ""),
        }

        self.toolbar = TopToolbar(prefs=self.selections)
        self.content = ContentArea()
        self.status_bar = StatusBar()
        self.status_bar.set_folder(self.save_location)

        self.engine = YtDlpEngine(self)
        self.engine.cookies_browser = self.settings["cookies_browser"]
        self.engine.speed_limit = self.settings["speed_limit"]
        self.engine.proxy = self._build_proxy_url(self.settings)
        self._task_item = {}
        self._speeds = {}
        self._queue = []
        self.content.list.host = self

        self._tray = QSystemTrayIcon(app_icon(64), self)
        self._tray.show()

        self._build_menu_bar()

        central_lay = self._build_central()
        self._wire_signals()

        if self.selections.get("theme_dark", False):
            tb = self.toolbar.theme_btn
            tb.blockSignals(True)
            tb.setChecked(True)
            tb.blockSignals(False)
            self._toggle_dark(True)

        QTimer.singleShot(1500, self._check_engine_update)

    def _build_central(self):
        from PySide6.QtWidgets import QWidget, QVBoxLayout

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.toolbar)
        lay.addWidget(self.content, 1)
        lay.addWidget(self.status_bar)
        self.setCentralWidget(central)
        return central

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(i18n.tr("menu_file"))
        act_paste = QAction(i18n.tr("paste_link"), self)
        act_paste.setShortcut("Ctrl+Shift+V")
        act_paste.triggered.connect(self._paste_flow)
        file_menu.addAction(act_paste)
        act_settings = QAction(i18n.tr("settings") + "...", self)
        act_settings.setShortcut("Ctrl+,")
        act_settings.triggered.connect(self._open_settings)
        file_menu.addAction(act_settings)
        file_menu.addSeparator()
        act_exit = QAction(i18n.tr("exit"), self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        edit_menu = menu_bar.addMenu(i18n.tr("menu_edit"))
        act_clear = QAction(i18n.tr("clear_list"), self)
        act_clear.triggered.connect(self._clear_list)
        edit_menu.addAction(act_clear)

        view_menu = menu_bar.addMenu(i18n.tr("menu_view"))
        act_search = QAction(i18n.tr("search"), self)
        act_search.setShortcut("Ctrl+F")
        act_search.triggered.connect(self.content.tabs._toggle_search)
        view_menu.addAction(act_search)

        help_menu = menu_bar.addMenu(i18n.tr("menu_help"))
        act_about = QAction(i18n.tr("about"), self)
        act_about.triggered.connect(self._about)
        help_menu.addAction(act_about)

    def _wire_signals(self):
        self.toolbar.pasteRequested.connect(self._paste_flow)
        self.toolbar.modeChanged.connect(self._on_mode_changed)
        self.toolbar.qualityChanged.connect(self._set_quality)
        self.toolbar.mode_dd.restore(self.mode)
        self.toolbar.quality_dd.restore(
            self.mode,
            self.selections.get("video_quality", "720p"),
            self.selections.get("audio_quality", "Highest"),
            self.selections.get("fps", "Highest"),
        )
        self.toolbar.quality_dd.fpsChanged.connect(self._set_fps)
        self.toolbar.quality_dd.videoCodecChanged.connect(self._set_video_codec)
        self.toolbar.quality_dd.audioCodecChanged.connect(self._set_audio_codec)
        self.toolbar.platformChanged.connect(lambda p: setattr(self, "platform", p))
        self.toolbar.locationChanged.connect(lambda l: setattr(self, "save_location", l))
        self.toolbar.settingsRequested.connect(self._open_settings)
        self.toolbar.theme_btn.themeToggled.connect(self._toggle_dark)
        self.toolbar.cookiesChanged.connect(self._set_cookies_browser)
        self.toolbar.cookies_btn.restore(self.selections.get("cookies_browser", "None"))

        self.toolbar.modeChanged.connect(self._remember_mode)
        self.toolbar.platformChanged.connect(self._remember_platform)
        self.toolbar.locationChanged.connect(self._remember_location)

        self.content.tabs.tabChanged.connect(self.content.list.set_tab)
        self.content.tabs.searchChanged.connect(self.content.list.set_search)
        self.content.tabs.sortToggled.connect(self.content.list.toggle_order)
        self.content.list.countChanged.connect(self.content.tabs.set_count)
        self.content.list.countChanged.connect(self.status_bar.set_items)
        self.toolbar.locationChanged.connect(self.status_bar.set_folder)

        self.engine.metadataResolved.connect(self._on_metadata)
        self.engine.metadataFailed.connect(self._on_metadata_failed)
        self.engine.progressChanged.connect(self._on_progress)
        self.engine.stateChanged.connect(self._on_state)
        self.engine.completedInfo.connect(self._on_completed_info)

    def _set_quality(self, q):
        self.quality = q
        key = "audio_quality" if self.mode == "audio" else "video_quality"
        self.selections[key] = q
        save_prefs(self.selections)
        self._on_prefs_changed()

    def _set_fps(self, f):
        self.fps = f
        self.selections["fps"] = f
        save_prefs(self.selections)
        self._on_prefs_changed()

    def _on_prefs_changed(self):
        for it in list(self.content.list.items()):
            if it.state in ("downloading", "paused") and it.start_params:
                it.pending_restart = True
                it.set_state("restarting")
                self.engine.pause(it.task_id)

    def _paste_flow(self):
        text = QGuiApplication.clipboard().text()
        url = self._extract_url(text)
        if url:
            self.add_download(url)
            return
        dlg = LinkDialog(self)
        if dlg.exec() == LinkDialog.Accepted:
            url = dlg.url()
            if url:
                self.add_download(url)
            else:
                QMessageBox.warning(
                    self,
                    i18n.tr("paste_link"),
                    i18n.tr("invalid_link"),
                )

    @staticmethod
    def _extract_url(text):
        return extract_url(text)

    def add_download(self, url):
        url = url.strip()
        if not url:
            return
        is_playlist = "playlist" in url.lower()
        kind = "playlist" if is_playlist else self.mode
        item = self.content.list.add_download(url, kind)
        task_id = uuid.uuid4().hex
        item.task_id = task_id
        self._task_item[task_id] = item
        item.pauseRequested.connect(self._pause_item)
        item.resumeRequested.connect(self._resume_item)
        item.cancelRequested.connect(self._cancel_item)
        item.changed.connect(self._update_downloading_count)
        item.removed.connect(self._on_item_removed)
        self.engine.resolve_metadata(task_id, url)
        self._update_downloading_count()

    def _item_for(self, task_id):
        return self._task_item.get(task_id)

    def _on_metadata(self, task_id, title, thumb_bytes):
        item = self._item_for(task_id)
        if not item:
            return
        item.set_title(title)
        item.set_thumb(thumb_bytes)
        if self.settings.get("autostart", True):
            self._enqueue_or_start(item)
        else:
            item.set_state("paused")

    def _enqueue_or_start(self, item):
        limit = max(1, int(self.settings.get("parallel", 2)))
        if self._active_downloads() < limit:
            self._start_download(item)
        else:
            item.set_state("queued")
            self._queue.append(item)

    def _active_downloads(self):
        return sum(
            1 for i in self.content.list.items() if i.state == "downloading"
        )

    def _start_next_queued(self):
        limit = max(1, int(self.settings.get("parallel", 2)))
        while self._queue and self._active_downloads() < limit:
            nxt = self._queue.pop(0)
            if nxt.task_id in self._task_item and nxt.state == "queued":
                self._start_download(nxt)

    def _on_metadata_failed(self, task_id, message):
        item = self._item_for(task_id)
        if item:
            item.set_state("error", message)

    def _start_download(self, item):
        params = {
            "url": item.url,
            "mode": self.mode,
            "quality": self.quality,
            "outdir": self.save_location,
            "is_playlist": item.kind == "playlist",
            "fps": self.fps,
            "title": item.title if item.title != item.url else None,
            "codec": self.audio_codec if self.mode == "audio" else self.video_codec,
        }
        item.start_params = params
        self.engine.start(item.task_id, **params)

    def _on_progress(self, task_id, pct, speed_bps, eta_s, total):
        item = self._item_for(task_id)
        if not item:
            return
        item.set_progress(pct, speed_bps, eta_s, total)
        if speed_bps:
            self._speeds[task_id] = speed_bps
        total_speed = sum(self._speeds.values())
        self.status_bar.set_speed(fmt_speed(total_speed) if total_speed else "")

    def _on_state(self, task_id, state, message):
        item = self._item_for(task_id)
        if not item:
            return
        if state == "completed" and message:
            item.file_path = message
        item.set_state(state, message)
        if state in ("paused", "cancelled") and item.pending_restart:
            item.pending_restart = False
            if item.task_id in self._task_item:
                if item.start_params:
                    self.engine.start(item.task_id, **item.start_params)
                else:
                    self._start_download(item)
                return
        if state in ("completed", "error", "cancelled", "paused"):
            self._speeds.pop(task_id, None)
        total_speed = sum(self._speeds.values())
        self.status_bar.set_speed(fmt_speed(total_speed) if total_speed else "")
        self._update_downloading_count()
        if state in ("completed", "error", "cancelled", "paused"):
            self._start_next_queued()
        if state == "completed":
            self._notify_finished(item)

    def _notify_finished(self, item):
        if not self.settings.get("notify_finished", True):
            return
        if self.settings.get("notify_sound", True):
            QApplication.beep()
        title = item.title if item.title != item.url else "4K Video Downloader+"
        self._tray.showMessage(
            "4K Video Downloader+",
            f"{title[:60]} - {i18n.tr('status_completed')}",
            QSystemTrayIcon.Information,
            5000,
        )

    def _on_completed_info(self, task_id, meta):
        item = self._item_for(task_id)
        if item:
            item.set_meta(meta)

    def _pause_item(self, item):
        if item.task_id:
            self.engine.pause(item.task_id)

    def _resume_item(self, item):
        if item.task_id:
            if item.start_params:
                self.engine.start(item.task_id, **item.start_params)
            else:
                self._start_download(item)

    def _cancel_item(self, item):
        if item.state == "queued":
            if item in self._queue:
                self._queue.remove(item)
            item.set_state("cancelled")
            self._start_next_queued()
            return
        if item.task_id:
            self.engine.cancel(item.task_id)

    def has_downloading(self):
        return any(
            i.state == "downloading" for i in self.content.list.items()
        )

    def has_paused(self):
        return any(i.state == "paused" for i in self.content.list.items())

    def pause_all(self):
        for it in self.content.list.items():
            if it.state == "downloading":
                self.engine.pause(it.task_id)

    def resume_all(self):
        for it in list(self.content.list.items()):
            if it.state == "paused":
                self._resume_item(it)

    def paste_link(self):
        self._paste_flow()

    def delete_item(self, item):
        confirmed, permanent = confirm_delete(
            self,
            i18n.tr("delete_item_title"),
            i18n.tr("delete_item_msg"),
        )
        if not confirmed:
            return
        if permanent:
            self._delete_files([item])
        self._on_item_removed(item)
        item.removed.emit(item)

    def delete_all(self):
        confirmed, permanent = confirm_delete(
            self,
            i18n.tr("delete_all_title"),
            i18n.tr("delete_all_msg"),
        )
        if not confirmed:
            return
        items = list(self.content.list.items())
        if permanent:
            self._delete_files(items)
        for it in items:
            self._on_item_removed(it)
            it.removed.emit(it)

    def _delete_files(self, items):
        errors = []
        for it in items:
            path = getattr(it, "file_path", "")
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError as exc:
                    errors.append(f"{os.path.basename(path)}: {exc}")
        if errors:
            QMessageBox.warning(
                self,
                "Delete",
                "Could not delete some files:\n" + "\n".join(errors[:5]),
            )

    def _on_item_removed(self, item):
        if item in self._queue:
            self._queue.remove(item)
        if item.task_id:
            if item.state == "downloading":
                self.engine.cancel(item.task_id)
            self._task_item.pop(item.task_id, None)
            self._speeds.pop(item.task_id, None)
        self._start_next_queued()

    def _update_downloading_count(self, item=None):
        downloading = sum(
            1
            for i in self.content.list.items()
            if i.state in ("retrieving", "downloading")
        )
        self.status_bar.set_downloading(downloading)

    def _on_mode_changed(self, mode):
        self.mode = mode
        self.quality = self.toolbar.quality_dd.current_quality()
        self._on_prefs_changed()

    def _open_settings(self):
        old_lang = self.settings.get("language", "en")
        dlg = SettingsPanel(self.settings, self)
        dlg.connectionSaved.connect(self._apply_connection_settings)
        if dlg.exec() == SettingsPanel.Accepted:
            self._apply_settings_dict(dlg.settings)
            if self.selections["language"] != old_lang:
                QMessageBox.information(self, i18n.tr("settings"), i18n.tr("restart_for_language"))

    def _apply_connection_settings(self, settings):
        self._apply_settings_dict(settings)

    def _apply_settings_dict(self, settings):
        old_lang = self.settings.get("language", "en")
        self.settings = dict(settings)
        self.save_location = self.settings.get("save_folder", self.save_location)
        self.selections["save_location"] = self.save_location
        self.selections["cookies_browser"] = self.settings.get("cookies_browser", "None")
        self.selections["speed_limit"] = self.settings.get("speed_limit", "Unlimited")
        self.selections["language"] = self.settings.get("language", "en")
        self.selections["notify_finished"] = self.settings.get("notify_finished", True)
        self.selections["notify_sound"] = self.settings.get("notify_sound", True)
        self.selections["confirm_exit"] = self.settings.get("confirm_exit", True)
        self.selections["autostart"] = self.settings.get("autostart", True)
        self.selections["parallel"] = self.settings.get("parallel", 2)
        self.selections["proxy_enabled"] = self.settings.get("proxy_enabled", False)
        self.selections["proxy_type"] = self.settings.get("proxy_type", "http")
        self.selections["proxy_host"] = self.settings.get("proxy_host", "")
        self.selections["proxy_port"] = self.settings.get("proxy_port", "")
        self.selections["proxy_login"] = self.settings.get("proxy_login", "")
        self.selections["proxy_password"] = self.settings.get("proxy_password", "")
        save_prefs(self.selections)
        self.engine.cookies_browser = self.selections["cookies_browser"]
        self.engine.speed_limit = self.selections["speed_limit"]
        self.engine.proxy = self._build_proxy_url(self.settings)
        self.status_bar.set_folder(self.save_location)
        if self.selections["language"] != old_lang:
            QMessageBox.information(self, i18n.tr("settings"), i18n.tr("restart_for_language"))

    @staticmethod
    def _build_proxy_url(settings):
        if not settings.get("proxy_enabled"):
            return None
        from urllib.parse import quote
        host = (settings.get("proxy_host") or "").strip()
        port = (settings.get("proxy_port") or "").strip()
        if not host or not port:
            return None
        ptype = settings.get("proxy_type", "http")
        login = settings.get("proxy_login", "")
        password = settings.get("proxy_password", "")
        if login:
            return f"{ptype}://{quote(login, safe='')}:{quote(password, safe='')}@{host}:{port}"
        return f"{ptype}://{host}:{port}"

    def _toggle_dark(self, dark):
        from PySide6.QtWidgets import QApplication
        from app.theme import apply_theme
        apply_theme(QApplication.instance(), dark=dark)
        for widget in QApplication.allWidgets():
            if hasattr(widget, "retheme"):
                widget.retheme()
        self.selections["theme_dark"] = dark
        save_prefs(self.selections)

    def _clear_list(self):
        for item in list(self.content.list.items()):
            item.removed.emit(item)

    def _about(self):
        QMessageBox.about(
            self,
            i18n.tr("about"),
            i18n.tr("about_body"),
        )

    def _remember_mode(self, mode):
        self.selections["mode"] = mode
        save_prefs(self.selections)

    def _remember_platform(self, platform):
        self.selections["platform"] = platform
        save_prefs(self.selections)

    def _remember_location(self, location):
        self.selections["save_location"] = location
        save_prefs(self.selections)

    def _check_engine_update(self):
        from app.components import update_manager
        from engine import yt_dlp_binary
        if not yt_dlp_binary.ytdlp_path():
            return
        checker = getattr(self, "_update_checker", None)
        if checker is not None and checker.isRunning():
            return
        runner = getattr(self, "_update_runner", None)
        if runner is not None and runner.isRunning():
            return
        self._update_checker = update_manager.UpdateChecker()

        def on_checked(current, latest):
            if not update_manager.is_newer(current, latest):
                return
            runner = getattr(self, "_update_runner", None)
            if runner is not None and runner.isRunning():
                return
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle(i18n.tr("update_available_title"))
            box.setText(i18n.tr("update_available_text") % (latest, current or "?"))
            yes = box.addButton(QMessageBox.Yes)
            box.addButton(QMessageBox.No)
            box.exec()
            if box.clickedButton() is yes:
                self._update_runner = update_manager.run_update(self)

        self._update_checker.checked.connect(on_checked)
        self._update_checker.start()

    def closeEvent(self, event):
        if self.settings.get("confirm_exit", True) and (
            self.has_downloading() or self.has_paused()
        ):
            answer = QMessageBox.question(
                self,
                i18n.tr("confirm_exit_title"),
                i18n.tr("confirm_exit_msg"),
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
        save_prefs(self.selections)
        super().closeEvent(event)
    def _set_video_codec(self, codec):
        self.video_codec = codec
        self.selections["video_codec"] = codec
        save_prefs(self.selections)
        self._on_prefs_changed()

    def _set_cookies_browser(self, browser):
        self.selections["cookies_browser"] = browser
        self.settings["cookies_browser"] = browser
        self.engine.cookies_browser = browser
        save_prefs(self.selections)

    def _set_audio_codec(self, codec):
        self.audio_codec = codec
        self.selections["audio_codec"] = codec
        save_prefs(self.selections)
        self._on_prefs_changed()
