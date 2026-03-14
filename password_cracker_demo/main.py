"""
Password Cracking Visualizer
Entry point — launches the PySide6 GUI application.

FOR EDUCATIONAL USE ONLY.
This tool only simulates attacks locally on user-supplied passwords.
It does not perform any real network or system attacks.
"""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


def main():
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Password Cracking Visualizer")
    app.setOrganizationName("CyberSecDemo")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
