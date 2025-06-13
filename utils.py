# PNG Metadata Editor - Utilities (PyQt5)
# Date: June 13, 2025
# Time: 09:51 AM CDT (Updated for PyQt5)
# Version: 2.0.7
# Description: Utility functions and constants for the PNG Metadata Editor with enhanced theme support using PyQt5

from PyQt5.QtWidgets import QApplication, QWidget, QStyleFactory
from PyQt5.QtGui import QPalette, QColor, QFontMetrics, QIcon
from PyQt5.QtCore import Qt, QSize

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

def get_theme_colors(theme_name):
    return THEME.get(theme_name, THEME["dark"]) # Default to dark if invalid theme name

def apply_theme(app_or_widget, theme_name):
    # Apply theme colors to the QApplication palette or a specific widget's palette
    theme_colors = get_theme_colors(theme_name)

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(theme_colors["bg"]))
    palette.setColor(QPalette.WindowText, QColor(theme_colors["fg"]))
    palette.setColor(QPalette.Base, QColor(theme_colors["highlight"]))
    palette.setColor(QPalette.AlternateBase, QColor(theme_colors["highlight"]))
    palette.setColor(QPalette.ToolTipBase, QColor(theme_colors["bg"]))
    palette.setColor(QPalette.ToolTipText, QColor(theme_colors["fg"]))
    palette.setColor(QPalette.Text, QColor(theme_colors["fg"]))
    palette.setColor(QPalette.Button, QColor(theme_colors["highlight"]))
    palette.setColor(QPalette.ButtonText, QColor(theme_colors["fg"]))
    palette.setColor(QPalette.BrightText, QColor(theme_colors["fg"]))
    palette.setColor(QPalette.Link, QColor(theme_colors["accent"]))
    palette.setColor(QPalette.Highlight, QColor(theme_colors["accent"]))
    palette.setColor(QPalette.HighlightedText, QColor(THEME['light' if theme_name == 'dark' else 'dark']['fg'])) # Text color on highlight

    # Apply to QApplication if available, otherwise to the widget
    if isinstance(app_or_widget, QApplication):
        app_or_widget.setPalette(palette)
        # Set a modern style if available
        if 'Fusion' in QStyleFactory.keys():
            app_or_widget.setStyle(QStyleFactory.create('Fusion'))
        elif 'Cleanlooks' in QStyleFactory.keys(): # Fallback for older systems
             app_or_widget.setStyle(QStyleFactory.create('Cleanlooks'))
    elif isinstance(app_or_widget, QWidget):
        app_or_widget.setPalette(palette)
        app_or_widget.setAutoFillBackground(True) # Ensure background is painted

    # Specific stylesheets for certain widgets for finer control (e.g., TreeView headers)
    # This might need to be set directly on the QTreeWidget in ui.py or here if passed the widget.
    # For a general approach, it's often done in the UI class after creating the widget.
    # Example for QTreeWidget in ui.py:
    # self.metadata_tree.setStyleSheet(f"""
    #     QTreeWidget {{
    #         background-color: {theme_colors["bg"]};
    #         color: {theme_colors["fg"]};
    #         alternate-background-color: {theme_colors["highlight"]};
    #     }}
    #     QTreeWidget::item:selected {{
    #         background-color: {theme_colors["accent"]};
    #         color: {THEME['light' if theme_name == 'dark' else 'dark']['fg']};
    #     }}
    #     QHeaderView::section {{
    #         background-color: {theme_colors["highlight"]};
    #         color: {theme_colors["fg"]};
    #         padding: 4px;
    #         border: 1px solid {theme_colors["bg"]};
    #     }}
    # """)


def limit_text_lines(text, max_lines=12):
    # Limit text to specified number of lines for display
    lines = text.split('\n')
    if len(lines) > max_lines:
        return '\n'.join(lines[:max_lines]) + '\n[...]'
    return text

# Note: calculate_row_height is generally not needed in PyQt5 for QTreeWidget
# as it manages row heights based on content and delegates.
# If custom dynamic height is essential, a custom QStyledItemDelegate is the way to go.