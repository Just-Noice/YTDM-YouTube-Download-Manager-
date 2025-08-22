import sys
import os
import json
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QFileDialog, QMessageBox

# Path to data.json inside main/
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data.json')

class ChangePathApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Change-path.ui'), self)

        # Title & icon
        self.setWindowTitle("YTDM - Change Paths")
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'YTDM.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Connect buttons
        self.MusicBrowse.clicked.connect(self.browse_music)
        self.SaveMusic.clicked.connect(self.save_music_path)

        self.VideoBrowse.clicked.connect(self.browse_video)
        self.SaveVideo.clicked.connect(self.save_video_path)

        self.exit.clicked.connect(self.close)

        self.Default.clicked.connect(self.use_default_musicvideo)


        # Store paths
        self.music_path = ""
        self.video_path = ""

        # Load existing or default paths
        self.load_paths()

    # --- Load from JSON or defaults ---
    def load_paths(self):
        default = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    data = json.load(f)
                    self.music_path = data.get("music_path", default)
                    self.video_path = data.get("video_path", default)
            except (json.JSONDecodeError, ValueError):
                self.music_path = default
                self.video_path = default
        else:
            self.music_path = default
            self.video_path = default

        # Update UI fields
        self.MusicURL.setText(self.music_path)
        self.VideoURL.setText(self.video_path)

    # --- Save JSON helper ---
    def save_paths_to_json(self):
        data = {
            "music_path": self.music_path,
            "video_path": self.video_path
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # --- MUSIC ---
    def browse_music(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Music Download Folder")
        if folder:
            self.music_path = folder
            self.MusicURL.setText(folder)

    def save_music_path(self):
        if self.music_path:
            self.save_paths_to_json()
            QMessageBox.information(self, "Saved", f"Music path saved:\nPlease re-open the app to apply changes.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a folder first!")

    # --- VIDEO ---
    def browse_video(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Video Download Folder")
        if folder:
            self.video_path = folder
            self.VideoURL.setText(folder)

    def save_video_path(self):
        if self.video_path:
            self.save_paths_to_json()
            QMessageBox.information(self, "Saved", f"Video path saved:\nPlease re-open the app to apply changes.")
        else:
            QMessageBox.warning(self, "Warning", "Please select a folder first!")

    # --- Reset Both ---
    def use_default_musicvideo(self):
        default_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.music_path = default_path
        self.video_path = default_path
        self.MusicURL.setText(default_path)
        self.VideoURL.setText(default_path)
        self.save_paths_to_json()
        QMessageBox.information(self, "Reset", f"Both paths reset to:\n{default_path}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ChangePathApp()
    window.show()
    sys.exit(app.exec_())
