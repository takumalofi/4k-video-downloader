# 4K Video Downloader+

Desktop app to download videos/audio from YouTube, TikTok, Facebook and 1800+ sites.

Powered by **yt-dlp + FFmpeg**, built with **PySide6** (native Windows UI).

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## Features

- Paste Link — auto-grabs link from clipboard
- Video (Best → 144p, Frame Rate, Codec) & Audio (Highest/320/256/128/64 kbps)
- Playlists, quality per Video/Audio remembered between sessions
- Real progress: speed, ETA, size; Pause / Resume / Cancel
- Dark mode, English/Vietnamese, speed limit, proxy support
- Notification on finish, confirm-exit protection
- Update yt-dlp engine with 1 click (no repack needed)

## Run from source

```bash
pip install PySide6 yt-dlp curl_cffi static-ffmpeg
python main.py
```

## Build .exe

```bash
pip install pyinstaller
pyinstaller --noconfirm 4KVideoDownloader.spec
xcopy /E /I bin dist\4KVideoDownloader\bin
xcopy /E /I ffmpeg dist\4KVideoDownloader\ffmpeg
```

> `bin/yt-dlp.exe` and `ffmpeg/` are also **auto-downloaded** on first run if missing.

## Downloads

Prebuilt Windows app: see [Releases](../../releases).

## Update the engine

After YouTube changes something: **File → Settings → General → Update engine**. No repack needed.
