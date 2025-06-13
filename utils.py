# PNG Metadata Editor - Utilities
# Date: June 13, 2025
# Time: 09:51 AM CDT
# Version: 2.0.7
# Description: Utility functions and constants for the PNG Metadata Editor with enhanced theme support

import tkinter as tk
from tkinter import font, ttk

# Theme definitions
THEME = {
    "light": {
        "bg": "#ffffff",
        "fg": "#333333",
        "fg_muted": "#666666",
        "highlight": "#e0e0e0",
        "accent": "#0078d4"
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "fg_muted": "#888888",
        "highlight": "#2d2d2d",
        "accent": "#0a84ff"
    }
}

def center_window(root, width, height):
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

def apply_theme(root, theme):
    # Apply theme colors to application
    style = ttk.Style()
    style.theme_use('clam')  # Use clam theme for better control
    style.configure(".", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"])
    style.configure("TLabel", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"])
    style.configure("TButton", background=THEME[theme]["highlight"], foreground=THEME[theme]["fg"], bordercolor=THEME[theme]["accent"])
    style.configure("TFrame", background=THEME[theme]["bg"])
    style.configure("TEntry", fieldbackground=THEME[theme]["highlight"], foreground=THEME[theme]["fg"])
    style.configure("TScrollbar", background=THEME[theme]["highlight"], troughcolor=THEME[theme]["bg"], arrowcolor=THEME[theme]["fg"])
    style.configure("Custom.Treeview", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"], fieldbackground=THEME[theme]["bg"])
    style.map("Custom.Treeview",
              background=[('selected', THEME[theme]["accent"])],
              foreground=[('selected', THEME['light' if theme == 'dark' else 'dark']['fg'])])
    style.map("TButton",
              background=[('active', THEME[theme]["accent"])],
              foreground=[('active', THEME['light' if theme == 'dark' else 'dark']['fg'])])
    style.map("TScrollbar",
              background=[('active', THEME[theme]["accent"])])
    root.configure(bg=THEME[theme]["bg"])

def limit_text_lines(text, max_lines=12):
    # Limit text to specified number of lines for display
    lines = text.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + '\n[...]'
    return text

def calculate_row_height(root, text):
    # Calculate row height based on text content
    font_obj = font.Font(family="TkDefaultFont", size=10)
    lines = text.split('\n')
    num_lines = min(len(lines), 12)  # Cap at 12 lines
    line_height = font_obj.metrics('linespace')
    return max(line_height * num_lines + 4, 25)  # Add padding, ensure minimum height