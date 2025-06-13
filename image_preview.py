# PNG Metadata Editor - Image Preview Module
# Date: June 13, 2025
# Time: 08:45 AM CDT
# Version: 2.0.0
# Description: Handles optional image preview functionality

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils import THEME


class ImagePreview:
    def __init__(self, ui):
        self.ui = ui
        self.preview_visible = False
        self.preview_frame = None
        self.image_label = None
        self.photo = None

    def toggle_preview(self):
        # Toggle image preview visibility
        if self.preview_visible:
            self.hide_preview()
        else:
            self.show_preview()

    def show_preview(self):
        # Create and show image preview pane
        if self.preview_frame:
            return

        self.preview_frame = ttk.Frame(self.ui.main_paned, padding=10)
        self.ui.main_paned.add(self.preview_frame, weight=1)

        ttk.Label(self.preview_frame, text="Image Preview").pack(anchor=tk.N)
        self.image_label = ttk.Label(self.preview_frame, background=THEME[self.ui.theme]["bg"])
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.preview_visible = True
        if self.ui.metadata_handler.current_image:
            self.update_preview(self.ui.metadata_handler.current_image)

    def hide_preview(self):
        # Hide image preview pane
        if not self.preview_frame:
            return

        self.ui.main_paned.remove(self.preview_frame)
        self.preview_frame.destroy()
        self.preview_frame = None
        self.image_label = None
        self.photo = None
        self.preview_visible = False

    def update_preview(self, image):
        # Update preview with new image
        if not self.preview_visible or not image:
            return

        try:
            # Resize image to fit preview area
            max_size = (400, 400)
            img = image.copy()
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=self.photo)

        except Exception as e:
            self.image_label.configure(text=f"Preview error: {str(e)}")

    def update_theme(self, theme):
        # Update preview background for theme change
        if self.image_label:
            self.image_label.configure(background=THEME[theme]["bg"])