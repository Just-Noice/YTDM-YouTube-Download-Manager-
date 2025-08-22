import os
import sys
import re
import json
import subprocess
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

# Use user's Downloads folder for both audio and video
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data.json")

def load_paths():
    default_music = os.path.join(os.path.expanduser("~"), "Downloads")
    default_video = os.path.join(os.path.expanduser("~"), "Downloads")

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                music = data.get("music_path", default_music)
                video = data.get("video_path", default_video)
                return music, video
        except Exception:
            pass  # fallback if json invalid
    return default_music, default_video

MUSIC_DOWNLOAD_DIR, VIDEO_DOWNLOAD_DIR = load_paths()

bin_path = os.path.join(os.path.dirname(__file__), '..', 'bin', 'yt-dlp.exe')
help_path = os.path.join(os.path.dirname(__file__), '..', 'help', 'help.py')
change_path_path = os.path.join(os.path.dirname(__file__), '..', 'change-path', 'Change-path.py')

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    output = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, url: str, mode: str, parent=None):
        super().__init__(parent)
        self.url = url
        self.mode = mode

    def run(self):
        try:
            if self.mode == 'audio':
                out_dir = MUSIC_DOWNLOAD_DIR
                cmd = [
                    'yt-dlp', '-f', 'bestaudio/best',
                    '-x', '--audio-format', 'mp3',
                    '--embed-thumbnail', '--add-metadata',
                    '--no-overwrites',
                    '-o', os.path.join(out_dir, '%(title)s.%(ext)s'),
                    self.url
                ]
            else:
                out_dir = VIDEO_DOWNLOAD_DIR
                cmd = [
                    'yt-dlp', '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '--embed-thumbnail', '--add-metadata',
                    '--merge-output-format', 'mp4',
                    '--no-overwrites',
                    '-o', os.path.join(out_dir, '%(title)s.%(ext)s'),
                    self.url
                ]

            os.makedirs(out_dir, exist_ok=True)

            startupinfo = None
            if sys.platform.startswith('win'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                startupinfo=startupinfo
            )

            exists = False

            for line in process.stdout:
                QtWidgets.QApplication.processEvents()
                text = line.rstrip()
                self.output.emit(text)
                if 'has already been downloaded' in text or 'Skipping download' in text:
                    exists = True
                m = re.search(r"(\d{1,3}\.\d)%", text)
                if m:
                    percent = int(float(m.group(1)))
                    self.progress.emit(percent)

            process.wait()
            if exists:
                self.finished.emit('exists')
            elif process.returncode != 0:
                self.finished.emit(f'error: Return code {process.returncode}')
            else:
                self.finished.emit('success')

        except Exception as e:
            self.finished.emit(f'error: {e}')

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'YTDM.ui'), self)

        # Set window title and icon
        self.setWindowTitle("YTDM")
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'YTDM.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Connect buttons
        self.Audio.clicked.connect(lambda: self.start_download('audio'))
        self.Video.clicked.connect(lambda: self.start_download('video'))
        self.Clear.clicked.connect(self.clear_ui)
        self.Update.clicked.connect(self.run_update)
        self.Help.clicked.connect(self.run_help)
        self.Exit.clicked.connect(self.close)
        self.changePath.clicked.connect(self.run_change_path)


        # Initial clear
        self.Clear.setEnabled(True)
        self.ProgressBox.clear()

    def extract_video_id(self, url: str) -> str:
        match = re.search(r'(?:v=|youtu\.be/|/embed/|/v/)([A-Za-z0-9_-]{11})', url)
        return match.group(1) if match else ''

    def start_download(self, mode: str):
        raw_url = self.URL.toPlainText().strip()
        if not raw_url:
            QMessageBox.warning(self, 'Input Error', 'Please enter a YouTube URL.')
            return
        vid_id = self.extract_video_id(raw_url)
        if not vid_id:
            QMessageBox.warning(self, 'Input Error', 'Invalid YouTube URL.')
            return
        url = f'https://www.youtube.com/watch?v={vid_id}'

        # Disable buttons during download
        for btn in [self.Audio, self.Video, self.Clear, self.Update, self.Help, self.changePath]:
            btn.setEnabled(False)
        self.ProgressBox.clear()

        # Launch download thread
        self.thread = DownloadThread(url, mode)
        self.thread.output.connect(self.append_output)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def append_output(self, text: str):
        self.ProgressBox.append(text)

    def on_finished(self, status: str):
        # Re-enable buttons
        for btn in [self.Audio, self.Video, self.Clear, self.Update, self.Help, self.changePath]:
            btn.setEnabled(True)

        if status == 'exists':
            QMessageBox.information(self, 'Info', 'Looks like you have already got this file — skipping download')
        elif status == 'success':
            QMessageBox.information(self, 'Success', 'All set — your file is ready to go')
        elif status.startswith('error'):
            err = status.split(':', 1)[1]
            QMessageBox.critical(self, 'Error', f'Oops, something interrupted the download: {err}')

    def clear_ui(self):
        self.URL.clear()
        self.ProgressBox.clear()

    def run_update(self):
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(['cmd', '/c', f'"{bin_path}" -U'], shell=True)
            else:
                subprocess.Popen(['sh', '-c', f'"{bin_path}" -U'])
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not run update: {e}')

    def run_help(self):
        try:
            # Launch help.py without showing terminal
            subprocess.Popen([sys.executable, help_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open help: {e}')

    def run_change_path(self):
        try:
            # Launch help.py without showing terminal
            subprocess.Popen([sys.executable, change_path_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not open change path: {e}')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
