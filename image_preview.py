# PNG Metadata Editor - Image Preview Module (PyQt5)
# Date: June 13, 2025
# Time: 09:15 AM CDT (Updated for PyQt5)
# Version: 2.0.5
# Description: Handles optional image preview functionality with fixed rendering using PyQt5

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
from PIL import Image, ImageQt # ImageQt is crucial for PIL to PyQt conversion
from utils import get_theme_colors # Assuming get_theme_colors is added to utils for PyQt5 styling


class ImagePreview:
    def __init__(self, ui):
        self.ui = ui
        self.preview_visible = False
        self.preview_widget = None # QWidget for the preview pane
        self.image_label = None
        self.current_image = None # PIL Image object

    def toggle_preview(self):
        # Toggle image preview visibility
        if self.preview_visible:
            self.hide_preview()
        else:
            self.show_preview()

    def show_preview(self):
        # Create and show image preview pane
        if self.preview_widget:
            return

        self.preview_widget = QFrame()
        self.preview_widget.setFrameShape(QFrame.StyledPanel)
        self.preview_widget.setFrameShadow(QFrame.Raised)
        self.preview_widget.setLayout(QVBoxLayout())
        self.preview_widget.layout().setContentsMargins(10, 10, 10, 10) # Padding

        title_label = QLabel("Image Preview")
        title_label.setAlignment(Qt.AlignHCenter)
        self.preview_widget.layout().addWidget(title_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet(f"background-color: {get_theme_colors(self.ui.theme)['bg']};") # Initial background
        self.preview_widget.layout().addWidget(self.image_label)

        self.ui.main_splitter.addWidget(self.preview_widget) # Add to the splitter
        self.preview_visible = True

        # Update theme for the newly created widgets
        self.update_theme(self.ui.theme)

        if self.current_image:
            self.update_preview(self.current_image)

    def hide_preview(self):
        # Hide image preview pane
        if not self.preview_widget:
            return

        # Remove from splitter and delete
        self.ui.main_splitter.takeWidget(self.ui.main_splitter.indexOf(self.preview_widget))
        self.preview_widget.deleteLater() # Schedule for deletion
        self.preview_widget = None
        self.image_label = None
        self.preview_visible = False

    def update_preview(self, pil_image):
        # Update preview with new image (PIL Image object)
        self.current_image = pil_image
        if not self.preview_visible or not pil_image or not self.image_label:
            return

        try:
            # Resize image to fit preview area
            max_size = QSize(400, 400) # Use QSize for consistency
            img = pil_image.copy() # Work on a copy

            # Calculate new size maintaining aspect ratio
            img.thumbnail((max_size.width(), max_size.height()), Image.LANCZOS)

            # Convert PIL Image to QImage, then to QPixmap
            q_image = ImageQt.ImageQt(img) # Convert PIL image to QImage
            pixmap = QPixmap.fromImage(q_image)

            self.image_label.setPixmap(pixmap)
            self.image_label.setText("") # Clear any error text

        except Exception as e:
            self.image_label.setPixmap(QPixmap()) # Clear pixmap
            self.image_label.setText(f"Preview error: {str(e)}")
            self.image_label.setStyleSheet(f"color: red; background-color: {get_theme_colors(self.ui.theme)['bg']};") # Show error in red

    def update_theme(self, theme):
        # Update preview background for theme change
        if self.image_label:
            self.image_label.setStyleSheet(f"background-color: {get_theme_colors(theme)['bg']};")
        if self.preview_widget: # Also update the frame itself
            self.preview_widget.setStyleSheet(f"background-color: {get_theme_colors(theme)['bg']};")
            # Update title label color
            for widget in self.preview_widget.findChildren(QLabel):
                if widget.text() == "Image Preview":
                    widget.setStyleSheet(f"color: {get_theme_colors(theme)['fg']};")
                    break