from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMenu, QWidgetAction

from app.widgets.dropdown_button import DropdownButton
from app.widgets.menu_row import MenuRow
from app import i18n

VIDEO_QUALITIES = (
    "Best", "UHD 8K", "HD 4K", "HQ 2K",
    "1080p", "720p", "480p", "360p", "240p", "144p",
)
FPS_OPTIONS = ("Highest", "240fps", "120fps", "60fps", "50fps", "30fps", "25fps")
VIDEO_CODECS = ("Any", "H264", "H265", "AV1", "VP9")
AUDIO_QUALITIES = ("Highest", "320kbps", "256kbps", "128kbps", "64kbps")
AUDIO_CODECS = ("Auto", "AAC", "MP3", "Opus", "FLAC", "WAV")


def quality_display(q):
    if q == "Best":
        return i18n.tr("best")
    if q == "Best quality":
        return i18n.tr("best_quality")
    if q == "Highest":
        return i18n.tr("highest")
    return q


class QualityDropdown(DropdownButton):
    qualityChanged = Signal(str)
    fpsChanged = Signal(str)
    videoCodecChanged = Signal(str)
    audioCodecChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(i18n.tr("quality"), "720p", parent)
        self._mode = "video"
        self._video_quality = "720p"
        self._audio_quality = "Highest"
        self._fps = "Highest"
        self._video_codec = "H264"
        self._audio_codec = "Auto"
        self._quality_rows = {}
        self._fr_row = None
        self._codec_row = None
        self._build_menu()

    def _build_menu(self):
        old = self.menu()
        if old is not None:
            old.deleteLater()
        menu = QMenu(self)
        menu.setMinimumWidth(180)
        self._quality_rows = {}

        self._quality = self._audio_quality if self._mode == "audio" else self._video_quality
        qualities = AUDIO_QUALITIES if self._mode == "audio" else VIDEO_QUALITIES
        for q in qualities:
            row = MenuRow(quality_display(q), right="check", height=30)
            row.set_checked(q == self._quality)
            row.clicked.connect(self._make_quality_pick(q, menu))
            wa = QWidgetAction(menu)
            wa.setDefaultWidget(row)
            menu.addAction(wa)
            self._quality_rows[q] = row

        menu.addSeparator()

        if self._mode == "video":
            self._fr_row = MenuRow("Frame Rate", right="chevron", value=self._fps, height=30)
            fr_wa = QWidgetAction(menu)
            fr_wa.setDefaultWidget(self._fr_row)
            fr_wa.setMenu(
                self._select_menu(FPS_OPTIONS, self._fps, self._set_fps, menu)
            )
            menu.addAction(fr_wa)

            self._codec_row = MenuRow("Codec", right="chevron", value=self._video_codec, height=30)
            codec_wa = QWidgetAction(menu)
            codec_wa.setDefaultWidget(self._codec_row)
            codec_wa.setMenu(
                self._select_menu(VIDEO_CODECS, self._video_codec, self._set_video_codec, menu)
            )
            menu.addAction(codec_wa)
        else:
            self._codec_row = MenuRow("Codec", right="chevron", value=self._audio_codec, height=30)
            codec_wa = QWidgetAction(menu)
            codec_wa.setDefaultWidget(self._codec_row)
            codec_wa.setMenu(
                self._select_menu(AUDIO_CODECS, self._audio_codec, self._set_audio_codec, menu)
            )
            menu.addAction(codec_wa)

        self.setMenu(menu)

    def _make_quality_pick(self, q, menu):
        def do():
            self._quality = q
            if self._mode == "audio":
                self._audio_quality = q
            else:
                self._video_quality = q
            self.set_value(quality_display(q))
            for n, r in self._quality_rows.items():
                r.set_checked(n == q)
            menu.hide()
            self.qualityChanged.emit(q)
        return do

    def _select_menu(self, options, current, on_pick, parent_menu):
        menu = QMenu(self)
        rows = {}
        for name in options:
            row = MenuRow(name, right="check", height=30)
            row.set_checked(name == current)
            def make(name=name, row=row):
                def do():
                    for n, r in rows.items():
                        r.set_checked(n == name)
                    parent_menu.hide()
                    on_pick(name)
                return do
            row.clicked.connect(make())
            wa = QWidgetAction(menu)
            wa.setDefaultWidget(row)
            menu.addAction(wa)
            rows[name] = row
        return menu

    def set_mode(self, mode):
        if mode == self._mode:
            return
        self._mode = mode
        self._build_menu()
        self.set_value(quality_display(self._quality))

    def current_quality(self):
        return self._quality

    def _set_fps(self, name):
        self._fps = name
        self._fr_row.set_value(name)
        self.fpsChanged.emit(name)

    def _set_video_codec(self, name):
        self._video_codec = name
        self._codec_row.set_value(name)
        self.videoCodecChanged.emit(name)

    def _set_audio_codec(self, name):
        self._audio_codec = name
        self._codec_row.set_value(name)
        self.audioCodecChanged.emit(name)

    def video_quality(self):
        return self._video_quality

    def audio_quality(self):
        return self._audio_quality

    def _pick(self, name):
        if self._mode == "audio":
            self._audio_quality = name
        else:
            self._video_quality = name
        self.set_value(quality_display(name))
        self.qualityChanged.emit(name)

    def restore(self, mode, video_quality=None, audio_quality=None, fps=None):
        self._mode = mode
        if video_quality:
            self._video_quality = video_quality
        if audio_quality:
            self._audio_quality = audio_quality
        if fps:
            self._fps = fps
        self._build_menu()
        self.set_value(quality_display(self._quality))
