# PNG Metadata Editor - Main Application (PyQt5)
# Date: June 13, 2025
# Time: 09:15 AM CDT (Updated for PyQt5)
# Version: 2.0.5
# Description: Entry point for the PNG Metadata Editor with enhanced UI and image preview using PyQt5

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui import PNGMetadataEditorUI
# No direct equivalent for 'utils.center_window' needed as PyQt handles geometry similarly
# No direct equivalent for 'os' environment variable setting for DND, PyQt handles DND natively.


def main():
    app = QApplication(sys.argv)
    try:
        main_window = PNGMetadataEditorUI()
        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText("Application Error")
        msg_box.setInformativeText(f"An unexpected error occurred: {e}")
        msg_box.setWindowTitle("Error")
        msg_box.exec_()
        sys.exit(1)


if __name__ == "__main__":
    main()