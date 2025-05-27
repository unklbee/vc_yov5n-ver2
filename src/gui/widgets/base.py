# Vehicle Detection System - Optimized Structure


### 1. **Base Components** (`src/gui/widgets/base.py`)

"""Base widget components to reduce code duplication"""
from PySide6.QtWidgets import QWidget, QGroupBox, QPushButton
from PySide6.QtCore import Signal
from typing import Dict, Any

class BaseWidget(QWidget):
    """Base widget with common functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Override in subclasses"""
        pass

    def connect_signals(self):
        """Override in subclasses"""
        pass

class StyledGroupBox(QGroupBox):
    """Reusable styled group box"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #FFC66D;
                background-color: #2B2B2B;
            }
        """)

class StyledButton(QPushButton):
    """Reusable styled button"""

    def __init__(self, text: str, style_type: str = "default", parent=None):
        super().__init__(text, parent)
        self.apply_style(style_type)

    def apply_style(self, style_type: str):
        styles = {
            "primary": """
                QPushButton {
                    background-color: #365880;
                    color: white;
                    border: 1px solid #365880;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #4A7BA7; }
                QPushButton:pressed { background-color: #214283; }
            """,
            "success": """
                QPushButton {
                    background-color: #59A869;
                    color: white;
                    border: 1px solid #59A869;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #6BB77A; }
                QPushButton:pressed { background-color: #4A8A56; }
            """,
            "danger": """
                QPushButton {
                    background-color: #C75450;
                    color: white;
                    border: 1px solid #C75450;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #D64545; }
                QPushButton:pressed { background-color: #B94A47; }
            """
        }
        self.setStyleSheet(styles.get(style_type, styles["primary"]))