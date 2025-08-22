import sys
import os
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow

class HelpWindow(QMainWindow):
    def __init__(self):
        super(HelpWindow, self).__init__()
        BASE_DIR = os.path.dirname(__file__)
        uic.loadUi(os.path.join(BASE_DIR, "help.ui"), self)
        self.setWindowTitle("YTDM-Help?")

        # Set window title and icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'Assets', 'YTDM.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HelpWindow()
    window.show()

    sys.exit(app.exec_())
