# PNG Metadata Editor - Utilities
# Date: June 13, 2025
# Time: 08:49 AM CDT
# Version: 2.0.1
# Description: Utility functions and constants for the PNG Metadata Editor

import tkinter as tk

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
    style = tk.ttk.Style()
    style.configure(".", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"])
    style.configure("TLabel", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"])
    style.configure("TButton", background=THEME[theme]["highlight"])
    style.configure("TFrame", background=THEME[theme]["bg"])
    style.configure("Custom.Treeview", background=THEME[theme]["bg"], foreground=THEME[theme]["fg"], fieldbackground=THEME[theme]["bg"])
    style.map("Custom.Treeview",
              background=[('selected', THEME[theme]["accent"])],
              foreground=[('selected', THEME['light' if theme == 'dark' else 'dark']['fg'])])
    root.configure(bg=THEME[theme]["bg"])

def limit_text_lines(text, max_lines=12):
    # Limit text to specified number of lines for display
    lines = text.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + '\n[...]'
    return text