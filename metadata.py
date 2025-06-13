# PNG Metadata Editor - Metadata Handler (PyQt5)
# Date: June 13, 2025
# Time: 09:51 AM CDT (Updated for PyQt5)
# Version: 2.0.7
# Description: Handles metadata loading, editing, and saving for PNG files with dynamic row heights using PyQt5

from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame, QApplication,
    QTreeWidget, QTreeWidgetItem,
    QWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontMetrics, QIcon
from PIL import Image, PngImagePlugin
import os
import json
from utils import limit_text_lines, get_theme_colors # Assuming get_theme_colors is added to utils for PyQt5 styling


class MetadataHandler:
    def __init__(self, ui):
        self.ui = ui
        self.current_file = None
        self.current_image = None
        self.metadata_entries = {} # Stores metadata as dicts with key, value, editable, full_value, etc.
        self.qt_item_map = {} # Maps unique internal item IDs to QTreeWidgetItem objects
        self.is_modified = False
        self.dialogs = []  # Track open dialogs for theme updates

    def handle_drop(self, file_path):
        # Handle dropped files (file_path is already processed by UI)
        if file_path:
            if file_path.lower().endswith('.png'):
                self.load_png_file(file_path)
            else:
                QMessageBox.showerror(self.ui, "Error", "Please drop a PNG file.")
        else:
            QMessageBox.showerror(self.ui, "Error", "No file dropped.")

    def open_file(self):
        # Open file dialog for PNG selection
        file_path, _ = QFileDialog.getOpenFileName(
            self.ui, "Select PNG File", "", "PNG files (*.png);;All files (*.*)"
        )
        if file_path:
            self.load_png_file(file_path)

    def load_png_file(self, file_path):
        # Load PNG file and its metadata
        try:
            self.current_file = file_path
            self.current_image = Image.open(file_path)
            self.current_image.load() # Load image data to close file handle after loading

            # Update UI
            self.ui.file_label.setText(os.path.basename(file_path))
            self.ui.drop_label.hide() # Hide the drop zone label
            self.ui.image_preview.update_preview(self.current_image)

            # Clear existing metadata in QTreeWidget
            self.ui.metadata_tree.clear()
            self.metadata_entries.clear()
            self.qt_item_map.clear()

            # Load metadata
            self.load_metadata()
            self.is_modified = False
            self.ui.update_status(f"Loaded: {os.path.basename(file_path)}")
            # No direct adjust_row_heights needed as QTreeWidget handles it better.
            # If dynamic heights are *critical* based on content, a custom delegate would be implemented.

        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to load PNG file:\n{str(e)}")

    def load_metadata(self):
        # Extract and display PNG metadata
        if not self.current_image:
            return

        png_info = self.current_image.info
        basic_info = {
            'Image Width': str(self.current_image.width),
            'Image Height': str(self.current_image.height),
            'Image Mode': self.current_image.mode,
            'Image Format': self.current_image.format or 'PNG'
        }

        # Add basic info
        for key, value in basic_info.items():
            item = QTreeWidgetItem(self.ui.metadata_tree, [key, value])
            item.setFlags(item.flags() & ~Qt.ItemIsEditable) # Make non-editable
            item_id = id(item) # Use unique ID for internal mapping
            self.metadata_entries[item_id] = {
                'key': key,
                'value': value,
                'editable': False,
                'full_value': value # Full value is same as display value for basic info
            }
            self.qt_item_map[item_id] = item

        # Add PNG metadata
        if png_info:
            for key, value in png_info.items():
                if isinstance(value, (list, tuple)):
                    display_value = ', '.join(str(v) for v in value)
                elif isinstance(value, dict):
                    display_value = json.dumps(value, indent=2)
                else:
                    display_value = str(value)

                # Limit display to 12 lines
                display_value_limited = limit_text_lines(display_value, max_lines=12)
                item = QTreeWidgetItem(self.ui.metadata_tree, [key, display_value_limited])
                item.setFlags(item.flags() | Qt.ItemIsEditable) # Make editable
                item_id = id(item)
                self.metadata_entries[item_id] = {
                    'key': key,
                    'value': display_value_limited,
                    'editable': True,
                    'full_value': str(value) # Store original full value
                }
                self.qt_item_map[item_id] = item

        # Show message if no metadata
        if not png_info and not basic_info: # Only if no basic info either
            item = QTreeWidgetItem(self.ui.metadata_tree, ['No PNG metadata', 'found in this file'])
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item_id = id(item)
            self.metadata_entries[item_id] = {
                'key': 'No PNG metadata',
                'value': 'found in this file',
                'editable': False,
                'full_value': 'found in this file'
            }
            self.qt_item_map[item_id] = item

        self.ui.metadata_tree.expandAll() # Expand all items to show content

    def edit_metadata_item(self, item, column):
        # Handle double-click to edit metadata
        # 'item' is a QTreeWidgetItem, 'column' is the index of the clicked column
        if not item:
            return

        # Find the internal ID for this QTreeWidgetItem
        item_id = None
        for iid, qitem in self.qt_item_map.items():
            if qitem == item:
                item_id = iid
                break

        if item_id is None or item_id not in self.metadata_entries:
            return

        entry_data = self.metadata_entries[item_id]
        if not entry_data['editable']:
            QMessageBox.information(self.ui, "Info", "This field is not editable (basic image information).")
            return

        self.create_edit_dialog(item_id, entry_data)

    def create_edit_dialog(self, item_id, entry_data):
        # Create dialog for metadata editing
        dialog = QDialog(self.ui)
        dialog.setWindowTitle("Edit Metadata")
        dialog.setFixedSize(600, 500) # Fixed size for dialog
        dialog.setWindowModality(Qt.ApplicationModal) # Makes it modal

        main_layout = QVBoxLayout(dialog)

        # Key field
        main_layout.addWidget(QLabel("Key:"))
        key_edit = QLineEdit(entry_data['key'])
        main_layout.addWidget(key_edit)

        # Value field
        main_layout.addWidget(QLabel("Value:"))
        value_text = QTextEdit()
        value_text.setText(entry_data.get('full_value', entry_data['value']))
        main_layout.addWidget(value_text)

        # Buttons
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_edit_dialog_changes(dialog, item_id, key_edit, value_text))
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject) # Reject closes the dialog
        button_layout.addWidget(cancel_button)

        self.dialogs.append(dialog)
        self.apply_dialog_theme(dialog) # Apply theme to the dialog
        dialog.exec_() # Show dialog modally

        if dialog in self.dialogs: # Clean up if still in list
            self.dialogs.remove(dialog)

    def save_edit_dialog_changes(self, dialog, item_id, key_edit, value_text):
        new_key = key_edit.text().strip()
        new_value = value_text.toPlainText().strip()

        if not new_key:
            QMessageBox.critical(dialog, "Error", "Key cannot be empty.")
            return

        display_value = limit_text_lines(new_value, max_lines=12)

        # Update the internal data structure
        self.metadata_entries[item_id]['key'] = new_key
        self.metadata_entries[item_id]['value'] = display_value
        self.metadata_entries[item_id]['full_value'] = new_value

        # Update the QTreeWidgetItem in the QTreeWidget
        item = self.qt_item_map[item_id]
        item.setText(0, new_key)
        item.setText(1, display_value)

        self.is_modified = True
        self.ui.update_status("Metadata modified")
        dialog.accept() # Accept closes the dialog

    def add_metadata_field(self):
        # Add new metadata field
        if not self.current_image:
            QMessageBox.warning(self.ui, "Warning", "Please load a PNG file first.")
            return

        dialog = QDialog(self.ui)
        dialog.setWindowTitle("Add Metadata Field")
        dialog.setFixedSize(400, 300)
        dialog.setWindowModality(Qt.ApplicationModal)

        main_layout = QVBoxLayout(dialog)

        main_layout.addWidget(QLabel("Key:"))
        key_edit = QLineEdit()
        main_layout.addWidget(key_edit)

        main_layout.addWidget(QLabel("Value:"))
        value_text = QTextEdit()
        main_layout.addWidget(value_text)

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_field_dialog_changes(dialog, key_edit, value_text))
        button_layout.addWidget(add_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)

        self.dialogs.append(dialog)
        self.apply_dialog_theme(dialog)
        dialog.exec_()

        if dialog in self.dialogs:
            self.dialogs.remove(dialog)

    def add_field_dialog_changes(self, dialog, key_edit, value_text):
        key = key_edit.text().strip()
        value = value_text.toPlainText().strip()

        if not key:
            QMessageBox.critical(dialog, "Error", "Key cannot be empty.")
            return

        display_value = limit_text_lines(value, max_lines=12)

        # Create new QTreeWidgetItem and internal mapping
        item = QTreeWidgetItem(self.ui.metadata_tree, [key, display_value])
        item.setFlags(item.flags() | Qt.ItemIsEditable) # Make editable
        item_id = id(item)
        self.metadata_entries[item_id] = {
            'key': key,
            'value': display_value,
            'full_value': value,
            'editable': True
        }
        self.qt_item_map[item_id] = item

        self.is_modified = True
        self.ui.update_status("New metadata field added")
        dialog.accept()

    def remove_metadata_field(self):
        # Remove selected metadata field
        selected_items = self.ui.metadata_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self.ui, "Warning", "Please select a metadata field to remove.")
            return

        item_to_remove = selected_items[0]
        # Find the internal ID for this QTreeWidgetItem
        item_id_to_remove = None
        for iid, qitem in self.qt_item_map.items():
            if qitem == item_to_remove:
                item_id_to_remove = iid
                break

        if item_id_to_remove is None or item_id_to_remove not in self.metadata_entries:
            return

        entry_data = self.metadata_entries[item_id_to_remove]

        if not entry_data.get('editable', True):
            QMessageBox.information(self.ui, "Info", "Cannot remove basic image information fields.")
            return

        key = entry_data.get('key', 'Unknown')
        reply = QMessageBox.question(self.ui, "Confirm", f"Remove metadata field '{key}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Remove from QTreeWidget
            root = self.ui.metadata_tree.invisibleRootItem()
            for i in range(root.childCount()):
                if root.child(i) == item_to_remove:
                    root.removeChild(item_to_remove)
                    break
            # Remove from internal dictionaries
            del self.metadata_entries[item_id_to_remove]
            del self.qt_item_map[item_id_to_remove]

            self.is_modified = True
            self.ui.update_status("Metadata field removed")

    def save_file(self):
        # Save metadata to current file
        if not self.current_file:
            QMessageBox.warning(self.ui, "Warning", "No file loaded.")
            return

        self.save_metadata_to_file(self.current_file)

    def save_as_file(self):
        # Save metadata to new file
        if not self.current_image:
            QMessageBox.warning(self.ui, "Warning", "No file loaded.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.ui, "Save PNG File As", os.path.basename(self.current_file) if self.current_file else "",
            "PNG files (*.png);;All files (*.*)"
        )

        if file_path:
            self.save_metadata_to_file(file_path)

    def save_metadata_to_file(self, file_path):
        # Save metadata to specified file
        try:
            # Create a new PngInfo object
            png_info = PngImagePlugin.PngInfo()

            for item_id, entry_data in self.metadata_entries.items():
                if entry_data['editable'] and entry_data['key'] and entry_data.get('full_value'):
                    # Basic image info fields are not actual PNG chunks, so don't add them.
                    # 'full_value' is the original, un-limited text.
                    if entry_data['key'] not in ['Image Width', 'Image Height', 'Image Mode', 'Image Format']:
                        png_info.add_text(entry_data['key'], entry_data['full_value'])

            # Create a new image object with the original image data to ensure we don't modify the opened one directly
            # which could lead to issues with file handles or unexpected behavior.
            temp_image = self.current_image.copy()

            # Save the image with the new PNG info
            temp_image.save(file_path, "PNG", pnginfo=png_info)

            # Update current file if saved to the same path
            if file_path == self.current_file:
                self.is_modified = False
                # Re-load the image to reflect saved changes, especially if metadata changed
                self.current_image = Image.open(file_path)
                self.current_image.load()


            self.ui.update_status(f"Saved: {os.path.basename(file_path)}")
            QMessageBox.information(self.ui, "Success", f"File saved successfully:\n{os.path.basename(file_path)}")

        except Exception as e:
            QMessageBox.critical(self.ui, "Error", f"Failed to save file:\n{str(e)}")

    def apply_dialog_theme(self, dialog):
        # Apply theme to dialog widgets
        theme_colors = get_theme_colors(self.ui.theme)
        dialog.setStyleSheet(f"background-color: {theme_colors['bg']}; color: {theme_colors['fg']};")

        # Recursively apply styles to children
        for widget in dialog.findChildren(QWidget):
            if isinstance(widget, QLabel):
                widget.setStyleSheet(f"color: {theme_colors['fg']};")
            elif isinstance(widget, QPushButton):
                widget.setStyleSheet(f"background-color: {theme_colors['highlight']}; color: {theme_colors['fg']}; border: 1px solid {theme_colors['accent']};")
                # Hover effect
                widget.setWhatsThis(f"QPushButton:hover {{ background-color: {theme_colors['accent']}; color: {get_theme_colors('light' if self.ui.theme == 'dark' else 'dark')['fg']}; }}")
                widget.setStyleSheet(widget.styleSheet() + widget.whatsThis())
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(f"background-color: {theme_colors['highlight']}; color: {theme_colors['fg']}; border: 1px solid {theme_colors['accent']};")
            elif isinstance(widget, QTextEdit):
                widget.setStyleSheet(f"background-color: {theme_colors['highlight']}; color: {theme_colors['fg']}; border: 1px solid {theme_colors['accent']};")
            # You might need to add more specific widget types if they don't inherit styles automatically

    def update_dialog_theme(self, theme):
        # Update theme for all open dialogs
        for dialog in self.dialogs[:]:
            if dialog.isVisible():
                self.apply_dialog_theme(dialog)
            else:
                self.dialogs.remove(dialog)