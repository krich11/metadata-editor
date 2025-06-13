# PNG Metadata Editor - Main Application
# Date: June 13, 2025
# Time: 08:45 AM CDT
# Version: 2.0.0
# Description: Entry point for the PNG Metadata Editor with enhanced UI and image preview

import sys
from tkinter import messagebox
import tkinterdnd2 as tkdnd
from ui import PNGMetadataEditorUI
from utils import center_window


def main():
    # Initialize main window with drag-drop support
    try:
        root = tkdnd.TkinterDnD.Tk()
        app = PNGMetadataEditorUI(root)

        # Set window icon if available
        try:
            root.iconbitmap(default='python.ico')
        except:
            pass

        # Center window
        center_window(root, 1000, 700)

        # Start application
        root.mainloop()

    except ImportError as e:
        messagebox.showerror("Error",
                             f"Required packages not installed.\nPlease install: pillow, tkinterdnd2\nError: {e}")
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("Error", f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()