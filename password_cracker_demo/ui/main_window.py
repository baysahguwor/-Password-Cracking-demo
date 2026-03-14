import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon

from ui.dashboard import Dashboard

BG_DARK = "#0D1117"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Cracking Visualizer — Cybersecurity Demo")
        self.setMinimumSize(1280, 780)

        # Dark palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(BG_DARK))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#E0EAF4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#060C12"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0D1520"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#E0EAF4"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#111820"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#E0EAF4"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#0A84FF"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        self.setPalette(palette)

        self.setCentralWidget(Dashboard())

    def showEvent(self, event):
        super().showEvent(event)
        self.showMaximized()
