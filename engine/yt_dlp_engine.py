import json
import os
import sys
import re
import shutil
import subprocess
import threading
import urllib.request

from PySide6.QtCore import QObject, Signal


from engine.yt_dlp_binary import CREATE_NO_WINDOW


class AbortDownload(Exception):
    pass


_STAT_PART = re.compile(
    r"^[\d.,]+[KMB]?\s+(reactions|shares|views|comments|likes)$", re.I
)


def _is_stats_segment(segment):
    subs = [s.strip() for s in segment.split("·") if s.strip()]
    return bool(subs) and all(_STAT_PART.match(s) for s in subs)


def clean_title(title, uploader=""):
    if not title:
        return title
    parts = [p.strip() for p in title.split(" | ")]
    while len(parts) > 1 and _is_stats_segment(parts[0]):
        parts.pop(0)
    if uploader and len(parts) > 1 and parts[-1].strip().lower() == uploader.strip().lower():
        parts.pop()
    cleaned = " | ".join(parts).strip()
    return cleaned or title


def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    name = name.rstrip(". ")
    return name[:100].strip()


_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]|\[[\d;]*m")


def strip_ansi(text):
    return _ANSI_RE.sub("", text or "")


def find_ffmpeg_dir():
    if getattr(sys, "frozen", False):
        local = os.path.join(os.path.dirname(sys.executable), "ffmpeg")
        if os.path.exists(os.path.join(local, "ffmpeg.exe")):
            return local
    try:
        from static_ffmpeg import run as static_run
        ffmpeg_exe, _ = static_run.get_or_fetch_platform_executables_else_raise()
        return os.path.dirname(ffmpeg_exe)
    except Exception:
        pass
    exe = shutil.which("ffmpeg")
    if exe:
        return os.path.dirname(exe)
    try:
        import imageio_ffmpeg
        return os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return None


def _fetch_bytes(url, timeout=10):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return b""


def fmt_size(num):
    if not num:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


def fmt_speed(bps):
    if not bps:
        return ""
    return f"{fmt_size(bps)}/s"


def fmt_eta(seconds):
    if seconds is None or seconds < 0:
        return ""
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"
    return f"{seconds // 60}:{seconds % 60:02d}"


def fmt_duration(seconds):
    if not seconds or seconds < 0:
        return ""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


_VIDEO_HEIGHT = {
    "Best": None,
    "UHD 8K": 4320,
    "HD 4K": 2160,
    "HQ 2K": 1440,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
    "240p": 240,
    "144p": 144,
}

_VIDEO_CODEC_PREFIX = {
    "Any": None,
    "H264": "avc1",
    "H265": "hvc1",
    "AV1": "av01",
    "VP9": "vp9",
}


def _video_format(quality, fps, codec):
    height = _VIDEO_HEIGHT.get(quality)
    if height is None and quality not in ("Best",):
        height = 720
    fps_cap = None
    if fps and fps != "Highest":
        digits = "".join(ch for ch in fps if ch.isdigit())
        fps_cap = int(digits) if digits else None
    codec_prefix = _VIDEO_CODEC_PREFIX.get(codec)

    def conditions(use_codec=True, use_fps=True):
        out = []
        if height:
            out.append(f"height<={height}")
        if fps_cap and use_fps:
            out.append(f"fps<={fps_cap}")
        if codec_prefix and use_codec:
            out.append(f"vcodec^={codec_prefix}")
        return out

    def fmt(conds):
        selector = "bestvideo[" + "][".join(conds) + "]" if conds else "bestvideo"
        return selector + "+bestaudio[acodec^=mp4a]"

    chain = [fmt(conditions())]
    if codec_prefix:
        chain.append(fmt(conditions(use_codec=False)))
    if fps_cap:
        chain.append(fmt(conditions(use_fps=False)))
    chain.append("bestvideo+bestaudio")
    if height:
        chain.append(f"best[height<={height}]")
    chain.append("best")
    return chain


def _mode_tag_and_args(mode, quality, fps, codec):
    if mode == "audio":
        if quality == "Highest":
            tag = "highest" if codec == "Auto" else f"highest-{codec.lower()}"
            return tag, []
        bitrate = "".join(ch for ch in quality if ch.isdigit()) or "320"
        if codec == "Auto":
            return f"{bitrate}kbps", [
                "-x", "--audio-format", "mp3", "--audio-quality", f"{bitrate}K",
            ]
        return f"{bitrate}kbps-{codec.lower()}", [
            "-x", "--audio-format", codec.lower(), "--audio-quality", f"{bitrate}K",
        ]
    res_tag = "best"
    if quality in _VIDEO_HEIGHT and quality != "Best":
        res_tag = quality
    tag = res_tag
    if fps and fps != "Highest":
        tag += f"-{fps}"
    if codec and codec != "Any":
        tag += f"-{codec.lower()}"
    return tag, [
        "-f", "/".join(_video_format(quality, fps, codec)),
        "--merge-output-format", "mp4",
    ]


def _audio_postprocessors(quality, codec):
    if quality == "Highest":
        return None
    bitrate = "".join(ch for ch in quality if ch.isdigit()) or "320"
    if codec == "Auto":
        fmt_codec = "mp3"
    else:
        fmt_codec = codec.lower()
    return [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": fmt_codec,
        "preferredquality": bitrate,
    }]


class YtDlpEngine(QObject):
    metadataResolved = Signal(str, str, bytes)
    metadataFailed = Signal(str, str)
    progressChanged = Signal(str, float, float, object, object)
    stateChanged = Signal(str, str, str)
    completedInfo = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._abort = set()
        self._pause_requested = set()
        self._cancel_requested = set()
        self._procs = {}
        self._meta_store = {}
        self.cookies_browser = None
        self.speed_limit = None
        self.proxy = None
        self._ffmpeg_dir = find_ffmpeg_dir()

    def _base_args(self):
        args = [
            "--newline", "--progress", "--no-warnings", "--color", "never",
            "--encoding", "utf-8", "--retries", "3",
            "--concurrent-fragments", "4",
            "--windows-filenames", "--trim-filenames", "180",
        ]
        if self.cookies_browser and self.cookies_browser != "None":
            args += ["--cookies-from-browser", self.cookies_browser.lower()]
        if self.speed_limit and self.speed_limit != "Unlimited":
            args += ["--limit-rate", self.speed_limit]
        if self.proxy:
            args += ["--proxy", self.proxy]
        if self._ffmpeg_dir:
            args += ["--ffmpeg-location", self._ffmpeg_dir]
        return args

    @staticmethod
    def _strip_cookies(args):
        out = []
        skip = False
        for a in args:
            if skip:
                skip = False
                continue
            if a.lower() == "--cookies-from-browser":
                skip = True
                continue
            out.append(a)
        return out

    def _arg_variants(self, args):
        variants = [list(args)]
        has_cookies = any(a.lower() == "--cookies-from-browser" for a in args)
        if has_cookies:
            variants.append(self._strip_cookies(args))
        fallback = self._strip_cookies(args)
        fallback += ["--extractor-args", "youtube:player_client=android_vr"]
        variants.append(fallback)
        return variants

    @staticmethod
    def _should_retry(error):
        msg = strip_ansi(str(error)).lower()
        return (
            "sign in to confirm" in msg
            or "not a bot" in msg
            or "dpapi" in msg
            or "failed to decrypt" in msg
            or "cookies" in msg
            or "429" in msg
            or "too many requests" in msg
            or "impersonat" in msg
        )

    @staticmethod
    def _needs_python_fallback(error):
        return "impersonat" in strip_ansi(str(error)).lower()

    def resolve_metadata(self, task_id, url):
        def run():
            from engine.yt_dlp_binary import ensure_ytdlp
            try:
                exe = ensure_ytdlp()
            except Exception as exc:
                exe = None
                exe_err = str(exc)
            if not exe:
                if self._pyapi_available():
                    self._pyapi_metadata(task_id, url)
                else:
                    self.metadataFailed.emit(
                        task_id, f"yt-dlp engine not found and could not be downloaded. {exe_err}"
                    )
                return
            base = self._base_args() + ["--skip-download", "--flat-playlist"]
            last_err = None
            data = None
            for vargs in self._arg_variants(base):
                cmd = [exe] + vargs + ["--dump-single-json", url]
                try:
                    r = subprocess.run(
                        cmd, capture_output=True, text=True,
                        encoding="utf-8", errors="replace", timeout=240,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                except subprocess.TimeoutExpired:
                    last_err = "Timeout while retrieving information"
                    continue
                if r.returncode == 0 and r.stdout.strip():
                    try:
                        data = json.loads(r.stdout)
                        break
                    except json.JSONDecodeError as exc:
                        last_err = exc
                        continue
                last_err = RuntimeError(r.stderr.strip() or "Cannot parse data")
                if not self._should_retry(last_err):
                    break
            if data is None:
                if self._needs_python_fallback(last_err) and self._pyapi_available():
                    self._pyapi_metadata(task_id, url)
                else:
                    self.metadataFailed.emit(task_id, strip_ansi(str(last_err)))
                return
            meta = {
                "duration": data.get("duration"),
                "uploader": data.get("uploader") or data.get("channel") or "",
                "height": data.get("height"),
                "fps": data.get("fps"),
            }
            self._meta_store[task_id] = meta
            title = clean_title(data.get("title") or url, meta["uploader"])
            thumb_url = ""
            for t in reversed(data.get("thumbnails") or []):
                if t.get("url"):
                    thumb_url = t["url"]
                    break
            thumb_bytes = _fetch_bytes(thumb_url) if thumb_url else b""
            self.metadataResolved.emit(task_id, title, thumb_bytes)

        threading.Thread(target=run, daemon=True).start()

    def start(self, task_id, url, mode, quality, outdir, is_playlist=False,
              fps="Highest", codec="Any", title=None):
        self._abort.discard(task_id)
        self._pause_requested.discard(task_id)
        self._cancel_requested.discard(task_id)
        threading.Thread(
            target=self._run_download,
            args=(task_id, url, mode, quality, outdir, is_playlist, fps, codec, title),
            daemon=True,
        ).start()

    def pause(self, task_id):
        self._pause_requested.add(task_id)
        self._abort.add(task_id)
        self._kill(task_id)

    def cancel(self, task_id):
        self._cancel_requested.add(task_id)
        self._abort.add(task_id)
        self._kill(task_id)

    def _kill(self, task_id):
        proc = self._procs.pop(task_id, None)
        if proc and proc.poll() is None:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    creationflags=CREATE_NO_WINDOW,
                )
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def _run_download(self, task_id, url, mode, quality, outdir, is_playlist,
                      fps="Highest", codec="Any", title=None):
        from engine.yt_dlp_binary import ensure_ytdlp
        try:
            exe = ensure_ytdlp()
        except Exception as exc:
            exe = None
            exe_err = str(exc)
        if exe:
            ok = self._subprocess_download(
                task_id, exe, url, mode, quality, outdir, is_playlist, fps, codec, title
            )
            if ok:
                return
            if not self._pyapi_available():
                return
        else:
            if not self._pyapi_available():
                self.stateChanged.emit(
                    task_id, "error",
                    f"yt-dlp engine not found and could not be downloaded. {exe_err}",
                )
                return
        self._pyapi_run_download(
            task_id, url, mode, quality, outdir, is_playlist, fps, codec, title
        )

    def _subprocess_download(self, task_id, exe, url, mode, quality, outdir,
                             is_playlist, fps, codec, title):
        tag, mode_args = _mode_tag_and_args(mode, quality, fps, codec)
        if not is_playlist and title:
            name_base = f"{sanitize_filename(title)} [%(id)s]"
        else:
            name_base = "%(title).100B [%(id)s]"
        outtmpl = os.path.join(outdir, f"{name_base} [{tag}].%(ext)s")

        base = self._base_args() + mode_args + [
            "-o", outtmpl,
            "--progress-template",
            "download:PROG|%(progress.downloaded_bytes)s|%(progress.total_bytes)s|"
            "%(progress.total_bytes_estimate)s|%(progress.speed)s|%(progress.eta)s",
            "--print", "after_move:filepath",
        ]
        if is_playlist:
            base.append("--yes-playlist")
        else:
            base.append("--no-playlist")

        os.makedirs(outdir, exist_ok=True)
        try:
            self.stateChanged.emit(task_id, "downloading", "")
            info_path = None
            last_err = None
            for vargs in self._arg_variants(base):
                cmd = [exe] + vargs + [url]
                try:
                    proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, encoding="utf-8", errors="replace",
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                except OSError as exc:
                    last_err = exc
                    continue
                self._procs[task_id] = proc
                out_path = None
                err_tail = []
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("PROG|"):
                        self._parse_progress(task_id, line)
                        continue
                    if re.match(r"^[A-Za-z]:[\\/]", line):
                        out_path = line
                        continue
                    if line.startswith("[") or "error" in line.lower():
                        err_tail.append(line)
                proc.wait()
                self._procs.pop(task_id, None)
                if task_id in self._abort:
                    raise AbortDownload()
                if proc.returncode == 0 and out_path:
                    self.completedInfo.emit(
                        task_id,
                        self._collect_meta(task_id, out_path, quality, fps, mode=mode),
                    )
                    self.stateChanged.emit(task_id, "completed", out_path)
                    return True
                last_err = RuntimeError(
                    " | ".join(err_tail[-2:]) or f"yt-dlp exited with code {proc.returncode}"
                )
                if not self._should_retry(last_err):
                    break
            if self._needs_python_fallback(last_err) and self._pyapi_available():
                return False
            raise last_err if last_err is not None else Exception("Download failed")
        except AbortDownload:
            self._procs.pop(task_id, None)
            if task_id in self._cancel_requested:
                self.stateChanged.emit(task_id, "cancelled", "")
            else:
                self.stateChanged.emit(task_id, "paused", "")
            return True
        except Exception as e:
            self.stateChanged.emit(task_id, "error", strip_ansi(str(e)))
            return True

    def _parse_progress(self, task_id, line):
        parts = line.split("|")
        parts += [""] * 6

        def to_f(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        done = to_f(parts[1])
        total = to_f(parts[2]) or to_f(parts[3])
        speed = to_f(parts[4])
        eta = to_f(parts[5])
        pct = (done / total * 100.0) if done is not None and total else 0.0
        self.progressChanged.emit(
            task_id, pct, speed or 0.0, eta, total
        )

    def _collect_meta(self, task_id, path, quality=None, fps=None, mode=None):
        entry = self._meta_store.get(task_id, {})
        meta = {}
        meta["duration"] = entry.get("duration")
        size = None
        if path and os.path.exists(path):
            size = os.path.getsize(path)
        meta["size"] = size
        meta["ext"] = os.path.splitext(path)[1].lstrip(".").lower() if path else ""
        if mode == "audio":
            meta["height"] = None
            meta["fps"] = None
        else:
            req_height = (
                _VIDEO_HEIGHT.get(quality) if quality and quality != "Best" else None
            )
            src_height = entry.get("height")
            if req_height and src_height:
                meta["height"] = min(req_height, src_height)
            else:
                meta["height"] = req_height or src_height
            req_fps = None
            if fps and fps != "Highest":
                digits = "".join(ch for ch in fps if ch.isdigit())
                req_fps = int(digits) if digits else None
            src_fps = entry.get("fps")
            if req_fps and src_fps:
                meta["fps"] = min(req_fps, src_fps)
            else:
                meta["fps"] = req_fps or src_fps
        meta["uploader"] = entry.get("uploader") or ""
        self._meta_store.pop(task_id, None)
        return meta

    @staticmethod
    def _pyapi_available():
        try:
            import yt_dlp  # noqa: F401
            return True
        except ImportError:
            return False

    def _pyapi_base_opts(self):
        opts = {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "color": "never",
            "retries": 3,
            "concurrent_fragment_downloads": 4,
        }
        if self.cookies_browser and self.cookies_browser != "None":
            opts["cookiesfrombrowser"] = (self.cookies_browser.lower(),)
        if self.speed_limit and self.speed_limit != "Unlimited":
            opts["ratelimit"] = self.speed_limit
        if self.proxy:
            opts["proxy"] = self.proxy
        if self._ffmpeg_dir:
            opts["ffmpeg_location"] = self._ffmpeg_dir
        return opts

    def _pyapi_metadata(self, task_id, url):
        def run():
            import yt_dlp
            try:
                opts = self._pyapi_base_opts()
                opts["skip_download"] = True
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                meta = {
                    "duration": info.get("duration"),
                    "uploader": info.get("uploader") or info.get("channel") or "",
                    "height": info.get("height"),
                    "fps": info.get("fps"),
                }
                self._meta_store[task_id] = meta
                title = clean_title(info.get("title") or url, meta["uploader"])
                thumb_url = ""
                for t in reversed(info.get("thumbnails") or []):
                    if t.get("url"):
                        thumb_url = t["url"]
                        break
                thumb_bytes = _fetch_bytes(thumb_url) if thumb_url else b""
                self.metadataResolved.emit(task_id, title, thumb_bytes)
            except Exception as e:
                self.metadataFailed.emit(task_id, strip_ansi(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _pyapi_run_download(self, task_id, url, mode, quality, outdir, is_playlist,
                            fps="Highest", codec="Any", title=None):
        def run():
            import yt_dlp

            def hook(d):
                if task_id in self._abort:
                    raise AbortDownload()
                if d["status"] == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    done = d.get("downloaded_bytes") or 0
                    pct = (done / total * 100.0) if total else 0.0
                    self.progressChanged.emit(
                        task_id, pct, d.get("speed") or 0.0, d.get("eta"), total or None
                    )

            tag, _ = _mode_tag_and_args(mode, quality, fps, codec)
            if not is_playlist and title:
                name_base = f"{sanitize_filename(title)} [%(id)s]"
            else:
                name_base = "%(title).100B [%(id)s]"
            outtmpl = os.path.join(outdir, f"{name_base} [{tag}].%(ext)s")

            opts = self._pyapi_base_opts()
            opts.update({
                "outtmpl": outtmpl,
                "progress_hooks": [hook],
                "noplaylist": not is_playlist,
            })
            if mode == "audio":
                opts["format"] = "bestaudio/best"
                post = _audio_postprocessors(quality, codec)
                if post:
                    opts["postprocessors"] = post
            else:
                opts["format"] = "/".join(_video_format(quality, fps, codec))
                opts["merge_output_format"] = "mp4"

            os.makedirs(outdir, exist_ok=True)
            try:
                self.stateChanged.emit(task_id, "downloading", "")
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    path = ""
                    req = info.get("requested_downloads") or []
                    if req and req[0].get("filepath"):
                        path = req[0]["filepath"]
                    if not path:
                        path = ydl.prepare_filename(info)
                self.completedInfo.emit(
                    task_id,
                    self._collect_meta(task_id, path, quality, fps, mode=mode),
                )
                self.stateChanged.emit(task_id, "completed", path)
            except AbortDownload:
                if task_id in self._cancel_requested:
                    self.stateChanged.emit(task_id, "cancelled", "")
                else:
                    self.stateChanged.emit(task_id, "paused", "")
            except Exception as e:
                self.stateChanged.emit(task_id, "error", strip_ansi(str(e)))

        threading.Thread(target=run, daemon=True).start()
