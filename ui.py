# PNG Metadata Editor - UI Module
# Date: June 13, 2025
# Time: 08:57 AM CDT
# Version: 2.0.2
# Description: Main UI components and layout for the PNG Metadata Editor with enhanced theme support

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import tkinterdnd2 as tkdnd
from metadata import MetadataHandler
from image_preview import ImagePreview
from utils import THEME, apply_theme


class PNGMetadataEditorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Metadata Editor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)
        self.theme = "dark"  # Default theme
        self.metadata_handler = MetadataHandler(self)
        self.image_preview = ImagePreview(self)

        self.setup_ui()
        self.setup_menu()
        self.setup_drag_drop()
        apply_theme(self.root, self.theme)

    def setup_ui(self):
        # Main container with paned window for resizable preview
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left pane for metadata controls
        self.main_frame = ttk.Frame(self.main_paned, padding=10)
        self.main_paned.add(self.main_frame, weight=1)

        # File info section
        file_frame = ttk.LabelFrame(self.main_frame, text="File Information", padding=5)
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.file_label = ttk.Label(file_frame, text="No file loaded", foreground=THEME[self.theme]["fg_muted"])
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Control buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(0, 10))

        buttons = [
            ("Open File", self.metadata_handler.open_file),
            ("Save", self.metadata_handler.save_file),
            ("Save As", self.metadata_handler.save_as_file),
            ("Add Field", self.metadata_handler.add_metadata_field),
            ("Remove Field", self.metadata_handler.remove_metadata_field)
        ]
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=(0, 5))

        # Theme toggle button
        self.theme_button = ttk.Button(button_frame, text="Toggle Light Mode", command=self.toggle_theme)
        self.theme_button.pack(side=tk.LEFT, padx=(10, 5))

        # Metadata table
        metadata_frame = ttk.LabelFrame(self.main_frame, text="Metadata", padding=5)
        metadata_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        metadata_frame.columnconfigure(0, weight=1)
        metadata_frame.rowconfigure(0, weight=1)

        tree_frame = ttk.Frame(metadata_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Enhanced treeview with multi-line support
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25)
        self.metadata_tree = ttk.Treeview(tree_frame, columns=('Key', 'Value'), show='headings', height=20,
                                          style="Custom.Treeview")
        self.metadata_tree.heading('Key', text='Metadata Key')
        self.metadata_tree.heading('Value', text='Value')
        self.metadata_tree.column('Key', width=250, minwidth=150)
        self.metadata_tree.column('Value', width=500, minwidth=300)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.metadata_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.metadata_tree.xview)
        self.metadata_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.metadata_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.metadata_tree.bind('<Double-1>', self.metadata_handler.edit_metadata_item)

        # Drop zone label
        self.drop_label = ttk.Label(metadata_frame,
                                    text="Drag and drop a PNG file here, or use 'Open File' button",
                                    font=('TkDefaultFont', 12),
                                    foreground=THEME[self.theme]["fg_muted"],
                                    anchor='center')
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')

        # Status bar
        self.status_var = tk.StringVar(value="Ready - No file loaded")
        status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))

    def setup_menu(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Image Preview", command=self.image_preview.toggle_preview)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.metadata_handler.open_file)
        file_menu.add_command(label="Save", command=self.metadata_handler.save_file)
        file_menu.add_command(label="Save As", command=self.metadata_handler.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def setup_drag_drop(self):
        # Enable drag and drop
        self.root.drop_target_register(tkdnd.DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.metadata_handler.handle_drop)

    def toggle_theme(self):
        # Toggle between light and dark themes
        self.theme = "light" if self.theme == "dark" else "dark"
        apply_theme(self.root, self.theme)
        self.file_label.configure(foreground=THEME[self.theme]["fg_muted"])
        self.drop_label.configure(foreground=THEME[self.theme]["fg_muted"])
        self.image_preview.update_theme(self.theme)
        self.theme_button.configure(text=f"Toggle {'Dark' if self.theme == 'light' else 'Light'} Mode")
        self.metadata_handler.update_dialog_theme(self.theme)

    def update_status(self, message):
        # Update status bar message
        status = message
        if self.metadata_handler.is_modified:
            status += " (Modified)"
        self.status_var.set(status)