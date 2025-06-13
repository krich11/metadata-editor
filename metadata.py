# PNG Metadata Editor - Metadata Handler
# Date: June 13, 2025
# Time: 09:51 AM CDT
# Version: 2.0.7
# Description: Handles metadata loading, editing, and saving for PNG files with dynamic row heights

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, PngImagePlugin
import os
import json
from utils import limit_text_lines, calculate_row_height, THEME


class MetadataHandler:
    def __init__(self, ui):
        self.ui = ui
        self.current_file = None
        self.current_image = None
        self.metadata_entries = {}
        self.is_modified = False
        self.dialogs = []  # Track open dialogs for theme updates

    def handle_drop(self, event):
        # Handle dropped files
        try:
            print("Drop event triggered")  # Debug log
            files = self.ui.root.tk.splitlist(event.data)
            print(f"Files received: {files}")  # Debug log
            if files:
                file_path = files[0].strip()
                print(f"Processing file: {file_path}")  # Debug log
                if file_path.lower().endswith('.png'):
                    self.load_png_file(file_path)
                else:
                    messagebox.showerror("Error", "Please drop a PNG file.")
            else:
                messagebox.showerror("Error", "No file dropped.")
        except Exception as e:
            print(f"Drag and drop error: {str(e)}")  # Debug log
            messagebox.showerror("Error", f"Drag and drop failed: {str(e)}")

    def open_file(self):
        # Open file dialog for PNG selection
        file_path = filedialog.askopenfilename(
            title="Select PNG File",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.load_png_file(file_path)

    def load_png_file(self, file_path):
        # Load PNG file and its metadata
        try:
            self.current_file = file_path
            self.current_image = Image.open(file_path)

            # Update UI
            self.ui.file_label.config(text=os.path.basename(file_path))
            self.ui.drop_label.place_forget()
            self.ui.image_preview.update_preview(self.current_image)

            # Clear existing metadata
            for item in self.ui.metadata_tree.get_children():
                self.ui.metadata_tree.delete(item)
            self.metadata_entries.clear()

            # Load metadata
            self.load_metadata()
            self.is_modified = False
            self.ui.update_status(f"Loaded: {os.path.basename(file_path)}")
            self.ui.adjust_row_heights()  # Refresh row heights

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PNG file:\n{str(e)}")

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
            item_id = self.ui.metadata_tree.insert('', 'end', values=(key, value))
            row_height = calculate_row_height(self.ui.root, f"{key}\n{value}")
            self.metadata_entries[item_id] = {
                'key': key,
                'value': value,
                'editable': False,
                'row_height': row_height
            }
            self.ui.metadata_tree.item(item_id, tags=('basic',))

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
                display_value = limit_text_lines(display_value, max_lines=12)
                item_id = self.ui.metadata_tree.insert('', 'end', values=(key, display_value))
                row_height = calculate_row_height(self.ui.root, f"{key}\n{display_value}")
                self.metadata_entries[item_id] = {
                    'key': key,
                    'value': display_value,
                    'editable': True,
                    'full_value': str(value),
                    'row_height': row_height
                }
                self.ui.metadata_tree.item(item_id, tags=('row',))

        # Show message if no metadata
        if not png_info:
            item_id = self.ui.metadata_tree.insert('', 'end', values=('No PNG metadata', 'found in this file'))
            row_height = calculate_row_height(self.ui.root, "No PNG metadata\nfound in this file")
            self.metadata_entries[item_id] = {
                'key': 'No PNG metadata',
                'value': 'found in this file',
                'editable': False,
                'row_height': row_height
            }
            self.ui.metadata_tree.item(item_id, tags=('basic',))

        self.ui.adjust_row_heights()  # Apply heights after loading

    def edit_metadata_item(self, event):
        # Handle double-click to edit metadata
        selection = self.ui.metadata_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id not in self.metadata_entries:
            return

        entry_data = self.metadata_entries[item_id]
        if not entry_data['editable']:
            messagebox.showinfo("Info", "This field is not editable (basic image information).")
            return

        self.create_edit_dialog(item_id, entry_data)

    def create_edit_dialog(self, item_id, entry_data):
        # Create dialog for metadata editing
        dialog = tk.Toplevel(self.ui.root)
        dialog.title("Edit Metadata")
        dialog.geometry("600x500")
        dialog.transient(self.ui.root)
        dialog.grab_set()
        self.dialogs.append(dialog)

        # Center dialog
        x = self.ui.root.winfo_rootx() + 50
        y = self.ui.root.winfo_rooty() + 50
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Key field
        ttk.Label(main_frame, text="Key:").pack(anchor=tk.W)
        key_var = tk.StringVar(value=entry_data['key'])
        key_entry = ttk.Entry(main_frame, textvariable=key_var, width=60)
        key_entry.pack(fill=tk.X, pady=(0, 10))

        # Value field
        ttk.Label(main_frame, text="Value:").pack(anchor=tk.W)
        value_text = scrolledtext.ScrolledText(main_frame, height=20, width=60)
        value_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        value_text.insert('1.0', entry_data.get('full_value', entry_data['value']))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def save_changes():
            new_key = key_var.get().strip()
            new_value = value_text.get('1.0', tk.END).strip()

            if not new_key:
                messagebox.showerror("Error", "Key cannot be empty.")
                return

            display_value = limit_text_lines(new_value, max_lines=12)
            row_height = calculate_row_height(self.ui.root, f"{new_key}\n{display_value}")
            self.ui.metadata_tree.item(item_id, values=(new_key, display_value))
            self.metadata_entries[item_id] = {
                'key': new_key,
                'value': display_value,
                'full_value': new_value,
                'editable': True,
                'row_height': row_height
            }
            self.ui.metadata_tree.item(item_id, tags=('row',))
            self.is_modified = True
            self.ui.update_status("Metadata modified")
            self.ui.adjust_row_heights()
            self.dialogs.remove(dialog)
            dialog.destroy()

        def on_close():
            self.dialogs.remove(dialog)
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=on_close).pack(side=tk.RIGHT)

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        value_text.focus_set()

        # Apply theme
        self.apply_dialog_theme(dialog)

    def add_metadata_field(self):
        # Add new metadata field
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load a PNG file first.")
            return

        dialog = tk.Toplevel(self.ui.root)
        dialog.title("Add Metadata Field")
        dialog.geometry("400x300")
        dialog.transient(self.ui.root)
        dialog.grab_set()
        self.dialogs.append(dialog)

        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Key:").pack(anchor=tk.W)
        key_var = tk.StringVar()
        key_entry = ttk.Entry(main_frame, textvariable=key_var, width=40)
        key_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Value:").pack(anchor=tk.W)
        value_text = scrolledtext.ScrolledText(main_frame, height=10, width=50)
        value_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def add_field():
            key = key_var.get().strip()
            value = value_text.get('1.0', tk.END).strip()

            if not key:
                messagebox.showerror("Error", "Key cannot be empty.")
                return

            display_value = limit_text_lines(value, max_lines=12)
            row_height = calculate_row_height(self.ui.root, f"{key}\n{display_value}")
            item_id = self.ui.metadata_tree.insert('', 'end', values=(key, display_value))
            self.metadata_entries[item_id] = {
                'key': key,
                'value': display_value,
                'full_value': value,
                'editable': True,
                'row_height': row_height
            }
            self.ui.metadata_tree.item(item_id, tags=('row',))
            self.is_modified = True
            self.ui.update_status("New metadata field added")
            self.ui.adjust_row_heights()
            self.dialogs.remove(dialog)
            dialog.destroy()

        def on_close():
            self.dialogs.remove(dialog)
            dialog.destroy()

        ttk.Button(button_frame, text="Add", command=add_field).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=on_close).pack(side=tk.RIGHT)

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        key_entry.focus_set()

        # Apply theme
        self.apply_dialog_theme(dialog)

    def remove_metadata_field(self):
        # Remove selected metadata field
        selection = self.ui.metadata_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a metadata field to remove.")
            return

        item_id = selection[0]
        entry_data = self.metadata_entries.get(item_id, {})

        if not entry_data.get('editable', True):
            messagebox.showinfo("Info", "Cannot remove basic image information fields.")
            return

        key = entry_data.get('key', 'Unknown')
        if messagebox.askyesno("Confirm", f"Remove metadata field '{key}'?"):
            self.ui.metadata_tree.delete(item_id)
            del self.metadata_entries[item_id]
            self.is_modified = True
            self.ui.update_status("Metadata field removed")
            self.ui.adjust_row_heights()

    def save_file(self):
        # Save metadata to current file
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded.")
            return

        self.save_metadata_to_file(self.current_file)

    def save_as_file(self):
        # Save metadata to new file
        if not self.current_image:
            messagebox.showwarning("Warning", "No file loaded.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save PNG File As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )

        if file_path:
            self.save_metadata_to_file(file_path)

    def save_metadata_to_file(self, file_path):
        # Save metadata to specified file
        try:
            png_info = PngImagePlugin.PngInfo()

            for item_id, entry_data in self.metadata_entries.items():
                if entry_data['editable'] and entry_data['key'] and entry_data.get('full_value', entry_data['value']):
                    if entry_data['key'] not in ['Image Width', 'Image Height', 'Image Mode', 'Image Format']:
                        png_info.add_text(entry_data['key'], entry_data.get('full_value', entry_data['value']))

            self.current_image.save(file_path, "PNG", pnginfo=png_info)

            if file_path == self.current_file:
                self.is_modified = False

            self.ui.update_status(f"Saved: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"File saved successfully:\n{os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def apply_dialog_theme(self, dialog):
        # Apply theme to dialog widgets
        dialog.configure(bg=THEME[self.ui.theme]["bg"])
        for widget in dialog.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(style="TFrame")
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        child.configure(background=THEME[self.ui.theme]["bg"], foreground=THEME[self.ui.theme]["fg"])
                    elif isinstance(child, ttk.Button):
                        child.configure(style="TButton")
                    elif isinstance(child, ttk.Entry):
                        child.configure(style="TEntry")
                    elif isinstance(child, scrolledtext.ScrolledText):
                        child.configure(bg=THEME[self.ui.theme]["highlight"], fg=THEME[self.ui.theme]["fg"])

    def update_dialog_theme(self, theme):
        # Update theme for all open dialogs
        for dialog in self.dialogs[:]:
            if dialog.winfo_exists():
                self.apply_dialog_theme(dialog)
            else:
                self.dialogs.remove(dialog)