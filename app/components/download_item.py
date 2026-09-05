from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFontMetrics, QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QProgressBar,
    QSizePolicy,
)
import os
import subprocess

from app.icons import dots_icon, folder_icon
from app import theme
from app import i18n
from engine.yt_dlp_engine import fmt_size, fmt_speed, fmt_eta, fmt_duration


def open_item_folder(item):
    target = getattr(item, "file_path", "")
    if target and os.path.exists(target):
        subprocess.Popen(["explorer", "/select,", os.path.normpath(target)])
        return
    folder = (item.start_params or {}).get("outdir", "")
    if folder and os.path.exists(folder):
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


class ElidedLabel(QLabel):
    def __init__(self, text="", style="", parent=None):
        super().__init__(parent)
        self._full = text
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(40)
        if style:
            self.setStyleSheet(style)
        self._refresh()

    def set_full_text(self, text):
        self._full = text
        self._refresh()

    def full_text(self):
        return self._full

    def set_color_style(self, style):
        self.setStyleSheet(style)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self):
        fm = QFontMetrics(self.font())
        self.setText(
            fm.elidedText(self._full, Qt.ElideRight, max(40, self.width()))
        )


class DownloadItem(QFrame):
    removed = Signal(object)
    changed = Signal(object)
    pauseRequested = Signal(object)
    resumeRequested = Signal(object)
    cancelRequested = Signal(object)

    def __init__(self, url, kind, parent=None):
        super().__init__(parent)
        self.setObjectName("itemCard")
        self.url = url
        self.kind = kind
        self.title = url
        self.task_id = None
        self.start_params = None
        self.file_path = ""
        self.pending_restart = False
        self.meta = {}
        self.state = "retrieving"
        self.paused = False
        self._title_full = url
        self._status_full = i18n.tr("status_retrieving")
        self._apply_card_style()
        self.setMinimumHeight(64)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 8, 8, 8)
        lay.setSpacing(14)

        self.thumb = QLabel()
        self.thumb.setFixedSize(40, 40)
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setStyleSheet(
            f"background:{theme.colors()['thumb']}; border:none; border-radius:2px;"
        )
        lay.addWidget(self.thumb)

        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(3)

        self.url_label = ElidedLabel(
            self.title,
            f"color:{theme.colors()['text']}; font-size:14px; border:none;",
        )
        col.addWidget(self.url_label)

        self.status_label = ElidedLabel(
            self._status_full,
            f"color:{theme.colors()['muted']}; font-size:13px; border:none;",
        )
        col.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 1000)
        self.progress.setStyleSheet(
            "QProgressBar { background:transparent; border:none; }"
            "QProgressBar::chunk { background:#55B900; border-radius:2px; }"
        )
        self.progress.setVisible(False)
        col.addWidget(self.progress)
        lay.addLayout(col)

        self.folder_btn = QPushButton()
        self.folder_btn.setObjectName("ghostBtn")
        self.folder_btn.setFixedSize(32, 32)
        self.folder_btn.setCursor(Qt.PointingHandCursor)
        self.folder_btn.setIcon(folder_icon(18))
        self.folder_btn.setIconSize(QSize(18, 18))
        self.folder_btn.setToolTip("Open in folder")
        self.folder_btn.clicked.connect(lambda: open_item_folder(self))
        lay.addWidget(self.folder_btn)

        self.more_btn = QPushButton()
        self.more_btn.setObjectName("ghostBtn")
        self.more_btn.setFixedSize(32, 32)
        self.more_btn.setCursor(Qt.PointingHandCursor)
        self.more_btn.setIcon(dots_icon(18))
        self.more_btn.setIconSize(QSize(18, 18))
        lay.addWidget(self.more_btn)

    def set_title(self, title):
        self.title = title
        self.url_label.set_full_text(title)
        self.changed.emit(self)

    def set_thumb(self, data):
        if not data:
            return
        pix = QPixmap()
        if pix.loadFromData(data):
            self.thumb.setPixmap(
                pix.scaled(
                    40, 40, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
                )
            )

    def set_state(self, state, message=""):
        self.state = state
        self.paused = state == "paused"
        text = i18n.tr("status_" + state)
        if state == "error" and message:
            text = f"{i18n.tr('status_error')}: {message[:80]}"
        if state == "completed":
            text = self._completed_text()
        self.status_label.set_full_text(text)
        if state == "downloading":
            self.progress.setVisible(True)
        else:
            self.progress.setVisible(False)
            if state == "completed":
                self.progress.setValue(1000)
        self.changed.emit(self)

    def set_meta(self, meta):
        self.meta = meta or {}
        if self.state == "completed":
            self.status_label.set_full_text(self._completed_text())

    def _completed_text(self):
        parts = []
        duration = self.meta.get("duration")
        if duration:
            parts.append(fmt_duration(duration))
        size = self.meta.get("size")
        if size:
            parts.append(fmt_size(size))
        ext = self.meta.get("ext")
        if ext:
            parts.append(ext.upper())
        if self.meta.get("height"):
            parts.append(f"{int(self.meta['height'])}p")
        if self.meta.get("fps"):
            parts.append(f"{int(self.meta['fps'])}fps")
        return " • ".join(parts) if parts else "completed"

    def set_progress(self, pct, speed_bps, eta_s, total):
        self.progress.setValue(int(pct * 10))
        parts = []
        if speed_bps:
            parts.append(fmt_speed(speed_bps))
        if eta_s is not None and eta_s >= 0:
            parts.append(f"ETA {fmt_eta(eta_s)}")
        if total:
            parts.append(fmt_size(total))
        if parts:
            self.status_label.set_full_text(" • ".join(parts))
        self.changed.emit(self)

    def retheme(self):
        self._apply_card_style()
        self.url_label.set_color_style(
            f"color:{theme.colors()['text']}; font-size:14px; border:none;"
        )
        self.status_label.set_color_style(
            f"color:{theme.colors()['muted']}; font-size:13px; border:none;"
        )
        self.thumb.setStyleSheet(
            f"background:{theme.colors()['thumb']}; border:none; border-radius:2px;"
        )
        self.more_btn.setIcon(dots_icon(18))

    def _apply_card_style(self):
        c = theme.colors()
        self.setStyleSheet(
            "QFrame#itemCard {"
            f" background:{c['panel']}; border:1px solid {c['card_border']};"
            " border-radius:4px; }"
            "QFrame#itemCard:hover {"
            f" border:1px solid {c['card_border_hover']}; }}"
        )

    def toggle_pause(self):
        if self.state == "downloading":
            self.pauseRequested.emit(self)
        elif self.state == "paused":
            self.resumeRequested.emit(self)
