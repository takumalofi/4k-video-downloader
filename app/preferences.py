import os
import sys

from PySide6.QtCore import QSettings


def _prefs_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


_PATH = os.path.join(_prefs_dir(), "prefs.ini")

DEFAULTS = {
    "mode": "video",
    "video_quality": "720p",
    "audio_quality": "Highest",
    "fps": "Highest",
    "video_codec": "H264",
    "audio_codec": "Auto",
    "platform": "Windows",
    "save_location": "D:/",
    "theme_dark": False,
}


def load_prefs():
    settings = QSettings(_PATH, QSettings.IniFormat)
    prefs = dict(DEFAULTS)
    for key in DEFAULTS:
        value = settings.value(key)
        if value is None:
            continue
        if isinstance(DEFAULTS[key], bool):
            prefs[key] = value in (True, "true", "1", 1)
        else:
            prefs[key] = value
    return prefs


def save_prefs(prefs):
    settings = QSettings(_PATH, QSettings.IniFormat)
    for key, value in prefs.items():
        settings.setValue(key, value)
    settings.sync()
