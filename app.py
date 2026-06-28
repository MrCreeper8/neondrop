import json
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


APP_PORT = 5177
APP_ROOT = Path(__file__).resolve().parent
DOWNLOAD_DIR = Path.home() / "Downloads" / "NeonDrop"
jobs = {}


def has_ytdlp():
    return shutil.which("yt-dlp") is not None or _python_module_exists("yt_dlp")


def has_ffmpeg():
    return shutil.which("ffmpeg") is not None


def app_url():
    return f"http://127.0.0.1:{APP_PORT}"


def server_already_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex(("127.0.0.1", APP_PORT)) == 0


def _python_module_exists(name):
    probe = subprocess.run(
        [sys.executable, "-c", f"import {name}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return probe.returncode == 0


def command_for(url, quality):
    output = str(DOWNLOAD_DIR / "%(title).180s [%(id)s].%(ext)s")
    if shutil.which("yt-dlp"):
        cmd = ["yt-dlp"]
    else:
        cmd = [sys.executable, "-m", "yt_dlp"]

    if quality == "audio":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    elif quality == "small":
        fmt = "bv*[height<=720]+ba/b[height<=720]/best[height<=720]/best" if has_ffmpeg() else "b[height<=720]/best[height<=720]/best"
        cmd += ["-f", fmt]
    else:
        fmt = "bv*+ba/best" if has_ffmpeg() else "best"
        cmd += ["-f", fmt]

    if quality != "audio" and has_ffmpeg():
        cmd += ["--merge-output-format", "mp4", "--remux-video", "mp4"]

    cmd += [
        "--newline",
        "--restrict-filenames",
        "--no-playlist",
        "-o",
        output,
        url,
    ]
    return cmd


def run_job(job_id, url, quality):
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    jobs[job_id]["status"] = "running"
    jobs[job_id]["lines"].append("Ignition started.")

    if not has_ytdlp():
        jobs[job_id]["status"] = "error"
        jobs[job_id]["lines"].append(
            "yt-dlp is not installed. Install it with: py -m pip install -U yt-dlp"
        )
        return
    if quality == "audio" and not has_ffmpeg():
        jobs[job_id]["status"] = "error"
        jobs[job_id]["lines"].append(
            "MP3 conversion needs FFmpeg. Install FFmpeg, or use Max/Lean for video."
        )
        return
    if quality != "audio":
        jobs[job_id]["lines"].append(
            "Video output is set to MP4." if has_ffmpeg() else "FFmpeg not found, so MP4 conversion is unavailable."
        )

    try:
        process = subprocess.Popen(
            command_for(url, quality),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(DOWNLOAD_DIR),
        )
        for line in process.stdout:
            clean = line.strip()
            if clean:
                jobs[job_id]["lines"].append(clean)
                percent = re.search(r"(\d+(?:\.\d+)?)%", clean)
                if percent:
                    jobs[job_id]["progress"] = float(percent.group(1))
        code = process.wait()
        if code == 0:
            jobs[job_id]["progress"] = 100
            jobs[job_id]["status"] = "done"
            jobs[job_id]["lines"].append(f"Done. Saved in {DOWNLOAD_DIR}")
        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["lines"].append(f"Download stopped with code {code}.")
    except Exception as exc:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["lines"].append(str(exc))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_file(APP_ROOT / "index.html", "text/html; charset=utf-8")
        elif parsed.path == "/style.css":
            self.send_file(APP_ROOT / "style.css", "text/css; charset=utf-8")
        elif parsed.path == "/app.js":
            self.send_file(APP_ROOT / "app.js", "application/javascript; charset=utf-8")
        elif parsed.path.startswith("/api/job/"):
            job_id = parsed.path.rsplit("/", 1)[-1]
            self.send_json(jobs.get(job_id, {"status": "missing", "lines": []}))
        elif parsed.path == "/api/status":
            self.send_json(
                {
                    "ready": has_ytdlp(),
                    "downloadDir": str(DOWNLOAD_DIR),
                    "python": sys.executable,
                }
            )
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/download":
            self.send_error(404)
            return

        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body or "{}")
        url = (data.get("url") or "").strip()
        quality = data.get("quality") or "best"

        if not url.startswith(("http://", "https://")):
            self.send_json({"error": "Drop in a full http:// or https:// link."}, 400)
            return

        job_id = str(int(time.time() * 1000))
        jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "lines": [],
            "downloadDir": str(DOWNLOAD_DIR),
        }
        threading.Thread(target=run_job, args=(job_id, url, quality), daemon=True).start()
        self.send_json({"jobId": job_id})

    def send_file(self, path, content_type):
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload, status=200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if server_already_running():
        webbrowser.open(app_url())
        sys.exit(0)

    server = ThreadingHTTPServer(("127.0.0.1", APP_PORT), Handler)
    url = app_url()
    print(f"NeonDrop is live at {url}")
    print(f"Downloads save to {DOWNLOAD_DIR}")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    server.serve_forever()
