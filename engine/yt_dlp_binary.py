import os
import subprocess
import sys
import urllib.request

from shutil import which

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _project_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _bin_dir():
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(sys.executable), "bin")
    return os.path.join(_project_dir(), "bin")


BUNDLED_PATH = os.path.join(_bin_dir(), "yt-dlp.exe")
DOWNLOAD_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"


def ytdlp_path():
    if os.path.exists(BUNDLED_PATH):
        return BUNDLED_PATH
    if getattr(sys, "frozen", False):
        candidate = os.path.join(os.path.dirname(sys.executable), "yt-dlp.exe")
        if os.path.exists(candidate):
            return candidate
    found = which("yt-dlp") or which("yt-dlp.exe")
    if found:
        return found
    return None


def ensure_ytdlp():
    if os.path.exists(BUNDLED_PATH):
        return BUNDLED_PATH
    try:
        _download()
    except Exception:
        pass
    if os.path.exists(BUNDLED_PATH):
        return BUNDLED_PATH
    return ytdlp_path()


def _download():
    os.makedirs(_bin_dir(), exist_ok=True)
    tmp = BUNDLED_PATH + ".part"
    req = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
        while True:
            chunk = resp.read(1 << 15)
            if not chunk:
                break
            f.write(chunk)
    os.replace(tmp, BUNDLED_PATH)


def get_version():
    path = ytdlp_path()
    if not path:
        return None
    try:
        r = subprocess.run(
            [path, "--version"], capture_output=True, text=True, timeout=30,
            creationflags=CREATE_NO_WINDOW,
        )
        return (r.stdout or "").strip()
    except Exception:
        return None


def update():
    path = ensure_ytdlp()
    if not path:
        return False, "Could not download the yt-dlp engine."
    try:
        r = subprocess.run(
            [path, "-U"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            creationflags=CREATE_NO_WINDOW,
        )
        out = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
        return r.returncode == 0, out
    except Exception as exc:
        return False, str(exc)
