## Styles Module (`src/gui/styles.py`)

"""Centralized styling for the application"""
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

def apply_dark_theme(app_or_widget):
    """Apply dark theme to application or widget"""

    # Main application stylesheet
    stylesheet = """
    /* Main Application */
    QMainWindow {
        background-color: #2B2B2B;
        color: #BBBBBB;
    }
    
    /* Menu Bar */
    QMenuBar {
        background-color: #3C3F41;
        color: #BBBBBB;
        border-bottom: 1px solid #555555;
        padding: 2px;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 4px;
    }
    
    QMenuBar::item:selected {
        background-color: #4B6EAF;
    }
    
    QMenuBar::item:pressed {
        background-color: #214283;
    }
    
    /* Menu */
    QMenu {
        background-color: #3C3F41;
        color: #BBBBBB;
        border: 1px solid #555555;
        border-radius: 6px;
        padding: 4px;
    }
    
    QMenu::item {
        padding: 8px 16px;
        border-radius: 4px;
        margin: 1px;
    }
    
    QMenu::item:selected {
        background-color: #4B6EAF;
    }
    
    QMenu::separator {
        height: 1px;
        background-color: #555555;
        margin: 4px 8px;
    }
    
    /* Status Bar */
    QStatusBar {
        background-color: #3C3F41;
        color: #BBBBBB;
        border-top: 1px solid #555555;
        padding: 2px;
    }
    
    /* Splitter */
    QSplitter::handle {
        background-color: #555555;
        width: 2px;
        height: 2px;
    }
    
    QSplitter::handle:hover {
        background-color: #4A88C7;
    }
    
    /* Scroll Bar */
    QScrollBar:vertical {
        background-color: #3C3F41;
        width: 12px;
        border-radius: 6px;
        border: none;
    }
    
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #4A88C7;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    
    QScrollBar:horizontal {
        background-color: #3C3F41;
        height: 12px;
        border-radius: 6px;
        border: none;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #555555;
        border-radius: 6px;
        min-width: 20px;
        margin: 2px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #4A88C7;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
    
    /* Input Fields */
    QLineEdit, QTextEdit {
        background-color: #45494A;
        color: #BBBBBB;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px 8px;
    }
    
    QLineEdit:focus, QTextEdit:focus {
        border-color: #4A88C7;
    }
    
    /* Combo Box */
    QComboBox {
        background-color: #45494A;
        color: #BBBBBB;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px 8px;
        min-width: 100px;
    }
    
    QComboBox:hover {
        border-color: #4A88C7;
    }
    
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    
    QComboBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #BBBBBB;
    }
    
    QComboBox QAbstractItemView {
        background-color: #3C3F41;
        color: #BBBBBB;
        border: 1px solid #555555;
        selection-background-color: #4B6EAF;
        outline: none;
    }
    
    /* Spin Box */
    QSpinBox {
        background-color: #45494A;
        color: #BBBBBB;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
    }
    
    QSpinBox:focus {
        border-color: #4A88C7;
    }
    
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: transparent;
        border: none;
        width: 16px;
    }
    
    QSpinBox::up-arrow {
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid #BBBBBB;
    }
    
    QSpinBox::down-arrow {
        width: 0;
        height: 0;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #BBBBBB;
    }
    
    /* Sliders */
    QSlider::groove:horizontal {
        background-color: #4C5052;
        height: 6px;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background-color: #4A88C7;
        width: 16px;
        height: 16px;
        border-radius: 8px;
        margin: -5px 0;
    }
    
    QSlider::handle:horizontal:hover {
        background-color: #5A98D7;
    }
    
    QSlider::sub-page:horizontal {
        background-color: #4A88C7;
        border-radius: 3px;
    }
    
    /* Radio Button */
    QRadioButton {
        color: #BBBBBB;
        spacing: 8px;
    }
    
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        border-radius: 8px;
        background-color: #45494A;
    }
    
    QRadioButton::indicator:hover {
        border-color: #4A88C7;
    }
    
    QRadioButton::indicator:checked {
        background-color: #4A88C7;
        border-color: #4A88C7;
    }
    
    /* Tool Tips */
    QToolTip {
        background-color: #3C3F41;
        color: #BBBBBB;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px 8px;
    }
    """

    app_or_widget.setStyleSheet(stylesheet)

    # Apply palette for system colors
    if isinstance(app_or_widget, QApplication):
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.Window, QColor("#2B2B2B"))
        palette.setColor(QPalette.WindowText, QColor("#BBBBBB"))

        # Base colors
        palette.setColor(QPalette.Base, QColor("#45494A"))
        palette.setColor(QPalette.AlternateBase, QColor("#3C3F41"))

        # Text colors
        palette.setColor(QPalette.Text, QColor("#BBBBBB"))
        palette.setColor(QPalette.BrightText, QColor("#FFC66D"))

        # Button colors
        palette.setColor(QPalette.Button, QColor("#4C5052"))
        palette.setColor(QPalette.ButtonText, QColor("#BBBBBB"))

        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor("#214283"))
        palette.setColor(QPalette.HighlightedText, QColor("#BBBBBB"))

        app_or_widget.setPalette(palette)