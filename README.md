# NeonDrop Downloader

NeonDrop is a small Windows desktop app for downloading videos through `yt-dlp`.

It provides a bright native UI where you paste a link, choose a mode, and download. Video modes try to save/remux as MP4 when FFmpeg is available. Audio mode downloads MP3.

## What It Uses

- Python and Tkinter for the desktop app
- yt-dlp for downloading supported video links
- FFmpeg for MP4 remuxing, merging, and MP3 conversion

## Run

Double-click:

```text
Start NeonDrop App.vbs
```

Or run directly:

```bat
python "NeonDrop App.pyw"
```

Downloads save to:

```text
%USERPROFILE%\Downloads\NeonDrop
```

## Optional Desktop Shortcut

Double-click this once:

```text
Create Desktop Shortcut.vbs
```

## Install Requirements

If `yt-dlp` is missing:

```bat
python -m pip install -U yt-dlp
```

FFmpeg is recommended for MP4 merging/remuxing and MP3 conversion.

## Notes

NeonDrop works with links supported by `yt-dlp`. Some sites may fail if they use DRM, require a login, block downloader tools, or change their website.

Only download videos you own, have permission to save, or are otherwise allowed to download.
