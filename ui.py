# PNG Metadata Editor - UI Module (PyQt5)
# Date: June 13, 2025
# Time: 09:51 AM CDT (Updated for PyQt5)
# Version: 2.0.7
# Description: Main UI components and layout for the PNG Metadata Editor with dynamic row heights and robust drag-drop using PyQt5

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QMessageBox, QSplitter, QFrame, QSizePolicy, QAction, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFontMetrics, QDragEnterEvent, QDropEvent

from metadata import MetadataHandler
from image_preview import ImagePreview
from utils import apply_theme, get_theme_colors # Assuming get_theme_colors is added to utils for PyQt5 styling


class PNGMetadataEditorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PNG Metadata Editor")
        self.base_width = 1000
        self.base_height = 700
        self.setGeometry(100, 100, self.base_width, self.base_height)
        self.setMinimumSize(800, 500)
        self.theme = "dark"  # Default theme

        self.metadata_handler = MetadataHandler(self)
        self.image_preview = ImagePreview(self)

        self.setup_ui()
        self.setup_menu()
        self.apply_initial_theme() # Apply theme after UI setup

        # Enable drag and drop for the main window
        self.setAcceptDrops(True)

    def setup_ui(self):
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Main splitter for resizable preview
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Left pane for metadata controls
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        self.main_splitter.addWidget(left_frame)

        # File info section
        file_info_frame = QFrame()
        file_info_layout = QHBoxLayout(file_info_frame)
        file_info_frame.setContentsMargins(0,0,0,0) # Adjust margins if needed for a cleaner look
        left_layout.addWidget(file_info_frame)

        file_info_layout.addWidget(QLabel("File:"))
        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet(f"color: {get_theme_colors(self.theme)['fg_muted']};") # Initial muted color
        file_info_layout.addWidget(self.file_label)
        file_info_layout.addStretch(1) # Pushes file label to left

        # Control buttons
        button_layout = QHBoxLayout()
        left_layout.addLayout(button_layout)

        buttons_data = [
            ("Open File", self.metadata_handler.open_file),
            ("Save", self.metadata_handler.save_file),
            ("Save As", self.metadata_handler.save_as_file),
            ("Add Field", self.metadata_handler.add_metadata_field),
            ("Remove Field", self.metadata_handler.remove_metadata_field),
            ("Toggle Preview", self.toggle_preview)
        ]
        for text, command in buttons_data:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            button_layout.addWidget(btn)

        # Theme toggle button
        self.theme_button = QPushButton("Toggle Light Mode")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)
        button_layout.addStretch(1) # Pushes buttons to left

        # Metadata table (QTreeWidget)
        metadata_frame = QFrame()
        metadata_layout = QVBoxLayout(metadata_frame)
        left_layout.addWidget(metadata_frame)
        metadata_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.metadata_tree = QTreeWidget()
        self.metadata_tree.setHeaderLabels(['Metadata Key', 'Value'])
        self.metadata_tree.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.metadata_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.metadata_tree.setColumnCount(2)
        self.metadata_tree.setIndentation(0) # Remove indentation for cleaner look

        self.metadata_tree.itemDoubleClicked.connect(self.metadata_handler.edit_metadata_item)
        self.metadata_tree.setAlternatingRowColors(True) # For better readability
        metadata_layout.addWidget(self.metadata_tree)

        # Drop zone label
        self.drop_label = QLabel("Drag and drop a PNG file here, or use 'Open File' button")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet(f"color: {get_theme_colors(self.theme)['fg_muted']};")
        self.drop_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.drop_label.setWordWrap(True) # Allow text to wrap
        metadata_layout.addWidget(self.drop_label) # Initially add to layout, will hide on file load

        # Status bar
        self.status_bar = self.statusBar()
        self.update_status("Ready - No file loaded")

        # Initial splitter sizes (left pane takes most space)
        self.main_splitter.setSizes([self.width(), 0]) # Image preview starts hidden

    def setup_menu(self):
        # File menu
        file_menu = self.menuBar().addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.metadata_handler.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.metadata_handler.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.metadata_handler.save_as_file)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def apply_initial_theme(self):
        # Apply the initial theme after UI components are created
        apply_theme(self, self.theme)

    def toggle_theme(self):
        # Toggle between light and dark themes
        self.theme = "light" if self.theme == "dark" else "dark"
        apply_theme(self, self.theme)

        # Update specific widget colors that don't get styled by apply_theme directly
        theme_colors = get_theme_colors(self.theme)
        self.file_label.setStyleSheet(f"color: {theme_colors['fg_muted']};")
        self.drop_label.setStyleSheet(f"color: {theme_colors['fg_muted']};")
        self.image_preview.update_theme(self.theme)
        self.theme_button.setText(f"Toggle {'Dark' if self.theme == 'light' else 'Light'} Mode")
        self.metadata_handler.update_dialog_theme(self.theme)

    def toggle_preview(self):
        # Toggle image preview visibility
        if self.image_preview.preview_visible:
            self.image_preview.hide_preview()
            # Restore left pane to full width
            self.main_splitter.setSizes([self.width(), 0])
        else:
            self.image_preview.show_preview()
            # Adjust splitter to show preview (approx 70/30 split initially)
            self.main_splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])
            if self.metadata_handler.current_image:
                self.image_preview.update_preview(self.metadata_handler.current_image)

    def adjust_row_heights(self):
        # In PyQt5, row heights are usually handled by the `sizeHint` of a custom delegate
        # or by setting a fixed height. For dynamic content, a custom delegate is preferred.
        # For a simpler approach, we can manually adjust as done in Tkinter, but it's less direct.
        # PyQt's QTreeWidget usually handles this more gracefully.
        # If content requires more space, you might consider `setWordWrap(True)` on the item's QLabel.
        # For specific item heights, a custom delegate would be needed.
        # For now, we'll ensure items are properly displayed.
        for item_id, entry_data in self.metadata_handler.metadata_entries.items():
            item = self.metadata_handler.qt_item_map.get(item_id) # Get the QTreeWidgetItem
            if item:
                # Re-set text to ensure word wrap calculation if needed
                item.setText(0, entry_data['key'])
                item.setText(1, entry_data['value'])
                # If you need dynamic height, this is where a custom delegate is useful.
                # For basic wrapping, QTreeWidget often handles it if text is long and column is narrow.
                # Here, we'll just ensure the text is properly set.

        # Trigger a layout update if necessary
        self.metadata_tree.resizeColumnToContents(0)
        self.metadata_tree.resizeColumnToContents(1)


    def update_status(self, message):
        # Update status bar message
        status = message
        if self.metadata_handler.is_modified:
            status += " (Modified)"
        self.status_bar.showMessage(status)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Accept drag if it contains URLs (files)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Handle dropped files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.metadata_handler.handle_drop(files[0]) # Pass the first file
        event.acceptProposedAction()

    def resizeEvent(self, event):
        # When main window is resized, ensure splitter adjusts its sizes.
        # This will distribute space proportionally unless fixed.
        if self.image_preview.preview_visible:
            # Re-apply sizes to maintain proportion if preview is visible
            current_sizes = self.main_splitter.sizes()
            total_width = sum(current_sizes)
            if total_width > 0:
                ratio_left = current_sizes[0] / total_width
                ratio_right = current_sizes[1] / total_width
                new_total_width = self.width() # Use the new width of the QMainWindow
                self.main_splitter.setSizes([int(new_total_width * ratio_left), int(new_total_width * ratio_right)])
        super().resizeEvent(event)
