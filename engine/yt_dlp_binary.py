import json
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


def _fmt_bytes(num):
    if not num or num <= 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{int(num)} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num = num / 1024.0
    return f"{num:.1f} TB"


def fetch_latest_release():
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
        tag = data.get("tag_name") or ""
        for asset in data.get("assets", []):
            if asset.get("name") == "yt-dlp.exe":
                return tag, asset.get("browser_download_url") or DOWNLOAD_URL, asset.get("size")
    except Exception:
        pass
    return "", DOWNLOAD_URL, None


def download_update(progress_cb=None, force=False):
    current = get_version() or ""
    tag, url, size = fetch_latest_release()
    if not force and tag and current and tag.lstrip("v") == current:
        return True, f"yt-dlp is already up to date ({current})."

    def notify(pct, status):
        if progress_cb:
            try:
                progress_cb(pct, status)
            except Exception:
                pass

    try:
        os.makedirs(_bin_dir(), exist_ok=True)
        tmp = BUNDLED_PATH + ".part"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(tmp, "wb") as f:
            total = size or int(resp.headers.get("Content-Length") or 0)
            received = 0
            while True:
                chunk = resp.read(1 << 15)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                pct = int(received * 100 / total) if total else 0
                notify(pct, f"{_fmt_bytes(received)} / {_fmt_bytes(total)}")
        os.replace(tmp, BUNDLED_PATH)
    except Exception as exc:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass
        return False, f"Update failed: {exc}"
    new_version = get_version() or tag or "latest"
    return True, f"yt-dlp updated to {new_version}."
