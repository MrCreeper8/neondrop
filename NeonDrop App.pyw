import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk


DOWNLOAD_DIR = Path.home() / "Downloads" / "NeonDrop"
PAPER = "#f8ff00"
INK = "#080808"
HOT = "#ff2bc2"
CYAN = "#00f5ff"
GREEN = "#35ff62"
WHITE = "#fff7f0"


def has_ffmpeg():
    return shutil.which("ffmpeg") is not None


def ytdlp_command():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    return [sys.executable, "-m", "yt_dlp"]


def has_ytdlp():
    if shutil.which("yt-dlp"):
        return True
    probe = subprocess.run(
        [sys.executable, "-c", "import yt_dlp"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return probe.returncode == 0


def build_command(url, mode):
    output = str(DOWNLOAD_DIR / "%(title).180s [%(id)s].%(ext)s")
    cmd = ytdlp_command()

    if mode == "MP3":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    elif mode == "Lean":
        fmt = "bv*[height<=720]+ba/b[height<=720]/best[height<=720]/best" if has_ffmpeg() else "b[height<=720]/best[height<=720]/best"
        cmd += ["-f", fmt]
    else:
        fmt = "bv*+ba/best" if has_ffmpeg() else "best"
        cmd += ["-f", fmt]

    if mode != "MP3" and has_ffmpeg():
        cmd += ["--merge-output-format", "mp4", "--remux-video", "mp4"]

    cmd += ["--newline", "--restrict-filenames", "--no-playlist", "-o", output, url]
    return cmd


class NeonDrop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NeonDrop")
        self.geometry("980x700")
        self.minsize(760, 560)
        self.configure(bg=PAPER)
        self.log_queue = queue.Queue()
        self.downloading = False

        self.mode = tk.StringVar(value="Max")
        self.url = tk.StringVar()
        self.status = tk.StringVar(value="READY")
        self.folder = tk.StringVar(value=f"Downloads: {DOWNLOAD_DIR}")
        self.progress = tk.DoubleVar(value=0)

        self.build_ui()
        self.after(120, self.flush_log)

    def build_ui(self):
        outer = tk.Frame(self, bg=PAPER)
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        panel = tk.Frame(outer, bg=WHITE, highlightthickness=5, highlightbackground=INK)
        panel.pack(fill="both", expand=True)

        ticker = tk.Label(
            panel,
            text="PASTE LINK    DOWNLOAD    MP4 VIDEO    NEONDROP",
            bg=INK,
            fg=GREEN,
            anchor="w",
            font=("Impact", 23),
            padx=14,
            pady=6,
        )
        ticker.pack(fill="x")

        hero = tk.Frame(panel, bg=WHITE)
        hero.pack(fill="x", padx=34, pady=(28, 10))

        title = tk.Label(
            hero,
            text="NEONDROP",
            bg=WHITE,
            fg=INK,
            font=("Impact", 96),
            anchor="w",
        )
        title.pack(side="left", fill="x", expand=True)

        drop = tk.Label(
            hero,
            text="DROP",
            bg=HOT,
            fg=INK,
            font=("Impact", 54),
            padx=18,
            pady=6,
            highlightthickness=5,
            highlightbackground=INK,
        )
        drop.pack(side="right", padx=(18, 0))

        entry_label = tk.Label(panel, text="Link", bg=WHITE, fg=INK, font=("Impact", 24), anchor="w")
        entry_label.pack(fill="x", padx=38, pady=(12, 4))

        entry = tk.Entry(
            panel,
            textvariable=self.url,
            bg="#fff7f0",
            fg=INK,
            insertbackground=INK,
            font=("Arial", 22, "bold"),
            relief="solid",
            bd=5,
        )
        entry.pack(fill="x", padx=38, ipady=13)
        entry.focus_set()

        row = tk.Frame(panel, bg=WHITE)
        row.pack(fill="x", padx=38, pady=18)

        for mode in ("Max", "Lean", "MP3"):
            rb = tk.Radiobutton(
                row,
                text=mode,
                variable=self.mode,
                value=mode,
                indicatoron=False,
                selectcolor=GREEN,
                bg=WHITE,
                fg=INK,
                activebackground=CYAN,
                font=("Impact", 25),
                width=7,
                relief="solid",
                bd=4,
                command=self.pulse,
            )
            rb.pack(side="left", padx=(0, 12), ipady=6)

        button = tk.Button(
            row,
            text="DOWNLOAD  ▶",
            bg=HOT,
            fg=INK,
            activebackground=GREEN,
            activeforeground=INK,
            font=("Impact", 34),
            relief="solid",
            bd=5,
            command=self.start_download,
            cursor="hand2",
        )
        button.pack(side="right", fill="x", expand=True, ipady=7)
        self.download_button = button

        meter = ttk.Style(self)
        meter.theme_use("clam")
        meter.configure("Neon.Horizontal.TProgressbar", troughcolor=WHITE, background=GREEN, bordercolor=INK, lightcolor=CYAN, darkcolor=HOT)

        progress = ttk.Progressbar(panel, variable=self.progress, maximum=100, style="Neon.Horizontal.TProgressbar")
        progress.pack(fill="x", padx=38, pady=(4, 0), ipady=8)

        status_row = tk.Frame(panel, bg=INK, highlightthickness=5, highlightbackground=INK)
        status_row.pack(fill="x", padx=38, pady=(18, 0))
        tk.Label(status_row, textvariable=self.status, bg=INK, fg=GREEN, font=("Arial", 13, "bold"), anchor="w").pack(side="left", padx=12, pady=8)
        tk.Label(status_row, textvariable=self.folder, bg=INK, fg=WHITE, font=("Arial", 10, "bold"), anchor="e").pack(side="right", padx=12, pady=8)

        self.log = tk.Text(
            panel,
            height=9,
            bg=INK,
            fg=WHITE,
            insertbackground=WHITE,
            font=("Consolas", 10),
            relief="solid",
            bd=5,
            wrap="word",
        )
        self.log.pack(fill="both", expand=True, padx=38, pady=(0, 34))
        self.write_line("Paste a link you own or have permission to download.")
        self.write_line("Video modes output MP4 when FFmpeg is available.")

    def pulse(self):
        self.configure(bg=CYAN if self["bg"] == PAPER else PAPER)
        self.after(110, lambda: self.configure(bg=PAPER))

    def write_line(self, text):
        self.log.insert("end", text + "\n")
        self.log.see("end")

    def start_download(self):
        if self.downloading:
            return
        url = self.url.get().strip()
        if not url.startswith(("http://", "https://")):
            self.write_line("Drop in a full http:// or https:// link.")
            self.status.set("NEEDS LINK")
            return
        self.downloading = True
        self.download_button.configure(state="disabled", text="WORKING...")
        self.progress.set(2)
        self.status.set("LAUNCHING")
        threading.Thread(target=self.download_worker, args=(url, self.mode.get()), daemon=True).start()

    def download_worker(self, url, mode):
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.log_queue.put(("line", "Ignition started."))

        if not has_ytdlp():
            self.log_queue.put(("line", "yt-dlp is not installed for this Python. Run: python -m pip install -U yt-dlp"))
            self.log_queue.put(("done", "ERROR"))
            return
        if mode == "MP3" and not has_ffmpeg():
            self.log_queue.put(("line", "MP3 conversion needs FFmpeg. Use Max/Lean or install FFmpeg."))
            self.log_queue.put(("done", "ERROR"))
            return

        if mode != "MP3":
            self.log_queue.put(("line", "Video output is set to MP4." if has_ffmpeg() else "FFmpeg not found, so MP4 conversion is unavailable."))

        try:
            process = subprocess.Popen(
                build_command(url, mode),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(DOWNLOAD_DIR),
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            for line in process.stdout:
                clean = line.strip()
                if not clean:
                    continue
                self.log_queue.put(("line", clean))
                percent = re.search(r"(\d+(?:\.\d+)?)%", clean)
                if percent:
                    self.log_queue.put(("progress", float(percent.group(1))))
            code = process.wait()
            self.log_queue.put(("progress", 100 if code == 0 else self.progress.get()))
            self.log_queue.put(("line", f"Done. Saved in {DOWNLOAD_DIR}" if code == 0 else f"Download stopped with code {code}."))
            self.log_queue.put(("done", "FINISHED" if code == 0 else "ERROR"))
        except Exception as exc:
            self.log_queue.put(("line", str(exc)))
            self.log_queue.put(("done", "ERROR"))

    def flush_log(self):
        try:
            while True:
                kind, value = self.log_queue.get_nowait()
                if kind == "line":
                    self.write_line(value)
                    self.status.set("RUNNING")
                elif kind == "progress":
                    self.progress.set(value)
                elif kind == "done":
                    self.status.set(value)
                    self.downloading = False
                    self.download_button.configure(state="normal", text="DOWNLOAD  ▶")
        except queue.Empty:
            pass
        self.after(120, self.flush_log)


if __name__ == "__main__":
    app = NeonDrop()
    app.mainloop()
