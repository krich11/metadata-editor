#!/usr/bin/env python3
"""
PNG Metadata Editor - A Windows GUI tool for viewing and editing PNG metadata
Supports drag-and-drop, dynamic metadata display, and save/save-as functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinterdnd2 as tkdnd
from PIL import Image, PngImagePlugin
import os
import json
from pathlib import Path


class PNGMetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Metadata Editor")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Current file info
        self.current_file = None
        self.current_image = None
        self.metadata_entries = {}
        self.is_modified = False

        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        """Create the main user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # File info section
        file_frame = ttk.LabelFrame(main_frame, text="File Information", padding="5")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_label = ttk.Label(file_frame, text="No file loaded", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        ttk.Button(button_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save As", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Add Field", command=self.add_metadata_field).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Field", command=self.remove_metadata_field).pack(side=tk.LEFT)

        # Metadata editing area
        metadata_frame = ttk.LabelFrame(main_frame, text="Metadata", padding="5")
        metadata_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        metadata_frame.columnconfigure(0, weight=1)
        metadata_frame.rowconfigure(0, weight=1)

        # Create treeview for metadata with scrollbars
        tree_frame = ttk.Frame(metadata_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Treeview with columns
        self.metadata_tree = ttk.Treeview(tree_frame, columns=('Key', 'Value'), show='headings', height=15)
        self.metadata_tree.heading('Key', text='Metadata Key')
        self.metadata_tree.heading('Value', text='Value')
        self.metadata_tree.column('Key', width=200, minwidth=150)
        self.metadata_tree.column('Value', width=400, minwidth=200)

        # Scrollbars for treeview
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.metadata_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.metadata_tree.xview)
        self.metadata_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.metadata_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Bind double-click for editing
        self.metadata_tree.bind('<Double-1>', self.edit_metadata_item)

        # Drop zone label (initially visible)
        self.drop_label = ttk.Label(metadata_frame,
                                    text="Drag and drop a PNG file here, or use 'Open File' button",
                                    font=('TkDefaultFont', 12),
                                    foreground='gray',
                                    anchor='center')
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - No file loaded")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        self.root.drop_target_register(tkdnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """Handle dropped files"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.png'):
                self.load_png_file(file_path)
            else:
                messagebox.showerror("Error", "Please drop a PNG file.")

    def open_file(self):
        """Open file dialog to select PNG file"""
        file_path = filedialog.askopenfilename(
            title="Select PNG File",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            self.load_png_file(file_path)

    def load_png_file(self, file_path):
        """Load and analyze PNG file metadata"""
        try:
            self.current_file = file_path
            self.current_image = Image.open(file_path)

            # Update UI
            self.file_label.config(text=os.path.basename(file_path))
            self.drop_label.place_forget()  # Hide drop label

            # Clear existing metadata
            for item in self.metadata_tree.get_children():
                self.metadata_tree.delete(item)
            self.metadata_entries.clear()

            # Load metadata
            self.load_metadata()
            self.is_modified = False
            self.update_status(f"Loaded: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PNG file:\n{str(e)}")

    def load_metadata(self):
        """Extract and display PNG metadata"""
        if not self.current_image:
            return

        # Get PNG info
        png_info = self.current_image.info

        # Add basic image information
        basic_info = {
            'Image Width': str(self.current_image.width),
            'Image Height': str(self.current_image.height),
            'Image Mode': self.current_image.mode,
            'Image Format': self.current_image.format or 'PNG'
        }

        # Add basic info to tree
        for key, value in basic_info.items():
            item_id = self.metadata_tree.insert('', 'end', values=(key, value))
            self.metadata_entries[item_id] = {'key': key, 'value': value, 'editable': False}

        # Add PNG-specific metadata
        if png_info:
            for key, value in png_info.items():
                # Handle different types of metadata values
                if isinstance(value, (list, tuple)):
                    display_value = ', '.join(str(v) for v in value)
                elif isinstance(value, dict):
                    display_value = json.dumps(value, indent=2)
                else:
                    display_value = str(value)

                item_id = self.metadata_tree.insert('', 'end', values=(key, display_value))
                self.metadata_entries[item_id] = {'key': key, 'value': display_value, 'editable': True}

        # If no metadata found, show message
        if not png_info:
            item_id = self.metadata_tree.insert('', 'end', values=('No PNG metadata', 'found in this file'))
            self.metadata_entries[item_id] = {'key': 'No PNG metadata', 'value': 'found in this file',
                                              'editable': False}

    def edit_metadata_item(self, event):
        """Handle double-click to edit metadata item"""
        selection = self.metadata_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        if item_id not in self.metadata_entries:
            return

        entry_data = self.metadata_entries[item_id]
        if not entry_data['editable']:
            messagebox.showinfo("Info", "This field is not editable (basic image information).")
            return

        # Create edit dialog
        self.create_edit_dialog(item_id, entry_data)

    def create_edit_dialog(self, item_id, entry_data):
        """Create dialog for editing metadata"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Metadata")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Key field
        ttk.Label(main_frame, text="Key:").pack(anchor=tk.W)
        key_var = tk.StringVar(value=entry_data['key'])
        key_entry = ttk.Entry(main_frame, textvariable=key_var, width=50)
        key_entry.pack(fill=tk.X, pady=(0, 10))

        # Value field (multiline for long values)
        ttk.Label(main_frame, text="Value:").pack(anchor=tk.W)
        value_text = scrolledtext.ScrolledText(main_frame, height=15, width=50)
        value_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        value_text.insert('1.0', entry_data['value'])

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def save_changes():
            new_key = key_var.get().strip()
            new_value = value_text.get('1.0', tk.END).strip()

            if not new_key:
                messagebox.showerror("Error", "Key cannot be empty.")
                return

            # Update the treeview
            self.metadata_tree.item(item_id, values=(new_key, new_value))
            self.metadata_entries[item_id] = {'key': new_key, 'value': new_value, 'editable': True}
            self.is_modified = True
            self.update_status("Metadata modified")
            dialog.destroy()

        def cancel_changes():
            dialog.destroy()

        ttk.Button(button_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=cancel_changes).pack(side=tk.RIGHT)

        # Focus on value field
        value_text.focus_set()

    def add_metadata_field(self):
        """Add new metadata field"""
        if not self.current_image:
            messagebox.showwarning("Warning", "Please load a PNG file first.")
            return

        # Create dialog for new field
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Metadata Field")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Key:").pack(anchor=tk.W)
        key_var = tk.StringVar()
        key_entry = ttk.Entry(main_frame, textvariable=key_var, width=40)
        key_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="Value:").pack(anchor=tk.W)
        value_var = tk.StringVar()
        value_entry = ttk.Entry(main_frame, textvariable=value_var, width=40)
        value_entry.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def add_field():
            key = key_var.get().strip()
            value = value_var.get().strip()

            if not key:
                messagebox.showerror("Error", "Key cannot be empty.")
                return

            item_id = self.metadata_tree.insert('', 'end', values=(key, value))
            self.metadata_entries[item_id] = {'key': key, 'value': value, 'editable': True}
            self.is_modified = True
            self.update_status("New metadata field added")
            dialog.destroy()

        ttk.Button(button_frame, text="Add", command=add_field).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

        key_entry.focus_set()

    def remove_metadata_field(self):
        """Remove selected metadata field"""
        selection = self.metadata_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a metadata field to remove.")
            return

        item_id = selection[0]
        entry_data = self.metadata_entries.get(item_id, {})

        if not entry_data.get('editable', True):
            messagebox.showinfo("Info", "Cannot remove basic image information fields.")
            return

        # Confirm deletion
        key = entry_data.get('key', 'Unknown')
        if messagebox.askyesno("Confirm", f"Remove metadata field '{key}'?"):
            self.metadata_tree.delete(item_id)
            del self.metadata_entries[item_id]
            self.is_modified = True
            self.update_status("Metadata field removed")

    def save_file(self):
        """Save metadata to current file"""
        if not self.current_file:
            messagebox.showwarning("Warning", "No file loaded.")
            return

        self.save_metadata_to_file(self.current_file)

    def save_as_file(self):
        """Save metadata to new file"""
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
        """Save metadata to specified file"""
        try:
            # Collect editable metadata
            png_info = PngImagePlugin.PngInfo()

            for item_id, entry_data in self.metadata_entries.items():
                if entry_data['editable'] and entry_data['key'] and entry_data['value']:
                    # Skip empty values and basic image info
                    if entry_data['key'] not in ['Image Width', 'Image Height', 'Image Mode', 'Image Format']:
                        png_info.add_text(entry_data['key'], entry_data['value'])

            # Save image with metadata
            self.current_image.save(file_path, "PNG", pnginfo=png_info)

            # Update current file if saved to same location
            if file_path == self.current_file:
                self.is_modified = False

            self.update_status(f"Saved: {os.path.basename(file_path)}")
            messagebox.showinfo("Success", f"File saved successfully:\n{os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def update_status(self, message):
        """Update status bar"""
        status = message
        if self.is_modified:
            status += " (Modified)"
        self.status_var.set(status)


def main():
    """Main application entry point"""
    try:
        # Create main window with drag-drop support
        root = tkdnd.TkinterDnD.Tk()
        app = PNGMetadataEditor(root)

        # Set window icon (if available)
        try:
            root.iconbitmap(default='python.ico')  # Optional: add an icon file
        except:
            pass  # Ignore if icon not found

        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')

        # Start the application
        root.mainloop()

    except ImportError as e:
        print("Required packages not installed. Please install:")
        print("pip install pillow tkinterdnd2")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    main()