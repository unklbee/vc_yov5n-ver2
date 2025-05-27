# """
# src/gui/styles/jetbrains_theme.py
# JetBrains-inspired theme for the application
# """
#
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QPalette, QColor
#
#
# class JetBrainsTheme:
#     """JetBrains-inspired dark theme with modern design elements"""
#
#     def __init__(self):
#         # Color palette based on JetBrains IDEs
#         self.colors = {
#             # Background colors
#             'bg_primary': '#2B2B2B',      # Main background
#             'bg_secondary': '#3C3F41',    # Secondary background
#             'bg_tertiary': '#4C5052',     # Tertiary background
#             'bg_input': '#45494A',        # Input fields
#             'bg_hover': '#4B6EAF',        # Hover states
#             'bg_selected': '#214283',     # Selected items
#             'bg_header': '#3C3F41',       # Header background
#
#             # Text colors
#             'text_primary': '#BBBBBB',    # Primary text
#             'text_secondary': '#9E9E9E',  # Secondary text
#             'text_disabled': '#6C6C6C',   # Disabled text
#             'text_accent': '#FFC66D',     # Accent text
#             'text_success': '#6A8759',    # Success text
#             'text_error': '#BC3F3C',      # Error text
#             'text_warning': '#BBB529',    # Warning text
#
#             # Border colors
#             'border_primary': '#555555',  # Primary borders
#             'border_secondary': '#404040', # Secondary borders
#             'border_focus': '#4A88C7',    # Focus borders
#
#             # Button colors
#             'btn_primary': '#365880',     # Primary buttons
#             'btn_primary_hover': '#4A7BA7', # Primary button hover
#             'btn_secondary': '#4C5052',   # Secondary buttons
#             'btn_secondary_hover': '#5C6365', # Secondary button hover
#             'btn_success': '#59A869',     # Success buttons
#             'btn_error': '#C75450',       # Error buttons
#
#             # Accent colors
#             'accent_blue': '#4A88C7',     # Blue accent
#             'accent_green': '#499C54',    # Green accent
#             'accent_orange': '#F28C28',   # Orange accent
#             'accent_red': '#F26522',      # Red accent
#             'accent_purple': '#9876AA',   # Purple accent
#         }
#
#     def get_main_stylesheet(self):
#         """Get the main application stylesheet"""
#         return f"""
#         /* Main Application Styling */
#         QMainWindow {{
#             background-color: {self.colors['bg_primary']};
#             color: {self.colors['text_primary']};
#         }}
#
#         /* Menu Bar */
#         QMenuBar {{
#             background-color: {self.colors['bg_secondary']};
#             color: {self.colors['text_primary']};
#             border-bottom: 1px solid {self.colors['border_primary']};
#             padding: 2px;
#         }}
#
#         QMenuBar::item {{
#             background-color: transparent;
#             padding: 6px 12px;
#             margin: 1px;
#             border-radius: 3px;
#         }}
#
#         QMenuBar::item:selected {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         QMenuBar::item:pressed {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         /* Menu */
#         QMenu {{
#             background-color: {self.colors['bg_secondary']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 6px;
#             padding: 4px;
#         }}
#
#         QMenu::item {{
#             padding: 8px 24px 8px 8px;
#             border-radius: 4px;
#             margin: 1px;
#         }}
#
#         QMenu::item:selected {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         QMenu::separator {{
#             height: 1px;
#             background-color: {self.colors['border_primary']};
#             margin: 4px 8px;
#         }}
#
#         /* Tool Bar */
#         QToolBar {{
#             background-color: {self.colors['bg_secondary']};
#             border: none;
#             padding: 4px;
#             spacing: 2px;
#         }}
#
#         QToolBar::separator {{
#             width: 1px;
#             background-color: {self.colors['border_primary']};
#             margin: 4px 8px;
#         }}
#
#         /* Status Bar */
#         QStatusBar {{
#             background-color: {self.colors['bg_secondary']};
#             color: {self.colors['text_primary']};
#             border-top: 1px solid {self.colors['border_primary']};
#             padding: 2px;
#         }}
#
#         QStatusBar QLabel {{
#             color: {self.colors['text_secondary']};
#             padding: 2px 8px;
#         }}
#
#         /* Dock Widgets */
#         QDockWidget {{
#             color: {self.colors['text_primary']};
#             titlebar-close-icon: url(:/icons/close.png);
#             titlebar-normal-icon: url(:/icons/undock.png);
#         }}
#
#         QDockWidget::title {{
#             background-color: {self.colors['bg_header']};
#             color: {self.colors['text_primary']};
#             padding: 8px;
#             border-bottom: 1px solid {self.colors['border_primary']};
#             font-weight: bold;
#         }}
#
#         QDockWidget::close-button, QDockWidget::float-button {{
#             background-color: transparent;
#             border: none;
#             padding: 2px;
#             margin: 2px;
#             border-radius: 2px;
#         }}
#
#         QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         /* Splitter */
#         QSplitter::handle {{
#             background-color: {self.colors['border_primary']};
#         }}
#
#         QSplitter::handle:horizontal {{
#             width: 2px;
#         }}
#
#         QSplitter::handle:vertical {{
#             height: 2px;
#         }}
#
#         QSplitter::handle:hover {{
#             background-color: {self.colors['accent_blue']};
#         }}
#
#         /* Buttons */
#         QPushButton {{
#             background-color: {self.colors['btn_secondary']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 6px;
#             padding: 8px 16px;
#             font-weight: 500;
#             min-width: 80px;
#         }}
#
#         QPushButton:hover {{
#             background-color: {self.colors['btn_secondary_hover']};
#             border-color: {self.colors['border_focus']};
#         }}
#
#         QPushButton:pressed {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         QPushButton:disabled {{
#             background-color: {self.colors['bg_tertiary']};
#             color: {self.colors['text_disabled']};
#             border-color: {self.colors['border_secondary']};
#         }}
#
#         QPushButton.primary {{
#             background-color: {self.colors['btn_primary']};
#             color: white;
#             border-color: {self.colors['btn_primary']};
#         }}
#
#         QPushButton.primary:hover {{
#             background-color: {self.colors['btn_primary_hover']};
#         }}
#
#         QPushButton.success {{
#             background-color: {self.colors['btn_success']};
#             color: white;
#             border-color: {self.colors['btn_success']};
#         }}
#
#         QPushButton.error {{
#             background-color: {self.colors['btn_error']};
#             color: white;
#             border-color: {self.colors['btn_error']};
#         }}
#
#         /* Tool Buttons */
#         QToolButton {{
#             background-color: transparent;
#             color: {self.colors['text_primary']};
#             border: 1px solid transparent;
#             border-radius: 4px;
#             padding: 6px;
#             margin: 1px;
#         }}
#
#         QToolButton:hover {{
#             background-color: {self.colors['bg_hover']};
#             border-color: {self.colors['border_focus']};
#         }}
#
#         QToolButton:pressed {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         QToolButton:checked {{
#             background-color: {self.colors['bg_selected']};
#             border-color: {self.colors['accent_blue']};
#         }}
#
#         /* Input Fields */
#         QLineEdit, QTextEdit, QPlainTextEdit {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             padding: 6px 8px;
#             selection-background-color: {self.colors['bg_selected']};
#         }}
#
#         QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
#             border-color: {self.colors['border_focus']};
#             background-color: {self.colors['bg_secondary']};
#         }}
#
#         QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
#             background-color: {self.colors['bg_tertiary']};
#             color: {self.colors['text_disabled']};
#         }}
#
#         /* Combo Box */
#         QComboBox {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             padding: 6px 8px;
#             min-width: 100px;
#         }}
#
#         QComboBox:hover {{
#             border-color: {self.colors['border_focus']};
#         }}
#
#         QComboBox:focus {{
#             border-color: {self.colors['accent_blue']};
#         }}
#
#         QComboBox::drop-down {{
#             subcontrol-origin: padding;
#             subcontrol-position: top right;
#             width: 20px;
#             border: none;
#         }}
#
#         QComboBox::down-arrow {{
#             image: url(:/icons/arrow_down.png);
#             width: 12px;
#             height: 12px;
#         }}
#
#         QComboBox QAbstractItemView {{
#             background-color: {self.colors['bg_secondary']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             selection-background-color: {self.colors['bg_hover']};
#             outline: none;
#         }}
#
#         /* Spin Box */
#         QSpinBox, QDoubleSpinBox {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             padding: 4px 8px;
#         }}
#
#         QSpinBox:focus, QDoubleSpinBox:focus {{
#             border-color: {self.colors['border_focus']};
#         }}
#
#         /* Sliders */
#         QSlider::groove:horizontal {{
#             background-color: {self.colors['bg_tertiary']};
#             height: 6px;
#             border-radius: 3px;
#         }}
#
#         QSlider::handle:horizontal {{
#             background-color: {self.colors['accent_blue']};
#             width: 16px;
#             height: 16px;
#             border-radius: 8px;
#             margin: -5px 0;
#         }}
#
#         QSlider::handle:horizontal:hover {{
#             background-color: {self.colors['btn_primary_hover']};
#         }}
#
#         QSlider::sub-page:horizontal {{
#             background-color: {self.colors['accent_blue']};
#             border-radius: 3px;
#         }}
#
#         /* Progress Bar */
#         QProgressBar {{
#             background-color: {self.colors['bg_tertiary']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             text-align: center;
#             font-weight: bold;
#         }}
#
#         QProgressBar::chunk {{
#             background-color: {self.colors['accent_blue']};
#             border-radius: 3px;
#         }}
#
#         /* Check Box */
#         QCheckBox {{
#             color: {self.colors['text_primary']};
#             spacing: 8px;
#         }}
#
#         QCheckBox::indicator {{
#             width: 16px;
#             height: 16px;
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 3px;
#             background-color: {self.colors['bg_input']};
#         }}
#
#         QCheckBox::indicator:hover {{
#             border-color: {self.colors['border_focus']};
#         }}
#
#         QCheckBox::indicator:checked {{
#             background-color: {self.colors['accent_blue']};
#             border-color: {self.colors['accent_blue']};
#         }}
#
#         /* Radio Button */
#         QRadioButton {{
#             color: {self.colors['text_primary']};
#             spacing: 8px;
#         }}
#
#         QRadioButton::indicator {{
#             width: 16px;
#             height: 16px;
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 8px;
#             background-color: {self.colors['bg_input']};
#         }}
#
#         QRadioButton::indicator:hover {{
#             border-color: {self.colors['border_focus']};
#         }}
#
#         QRadioButton::indicator:checked {{
#             background-color: {self.colors['accent_blue']};
#             border-color: {self.colors['accent_blue']};
#         }}
#
#         /* List Widget */
#         QListWidget {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             outline: none;
#         }}
#
#         QListWidget::item {{
#             padding: 8px;
#             border-bottom: 1px solid {self.colors['border_secondary']};
#         }}
#
#         QListWidget::item:selected {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         QListWidget::item:hover {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         /* Tree Widget */
#         QTreeWidget {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             outline: none;
#             alternate-background-color: {self.colors['bg_secondary']};
#         }}
#
#         QTreeWidget::item {{
#             padding: 4px;
#             border-bottom: 1px solid {self.colors['border_secondary']};
#         }}
#
#         QTreeWidget::item:selected {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         QTreeWidget::item:hover {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         QTreeWidget::branch:closed:has-children {{
#             image: url(:/icons/branch_closed.png);
#         }}
#
#         QTreeWidget::branch:open:has-children {{
#             image: url(:/icons/branch_open.png);
#         }}
#
#         /* Table Widget */
#         QTableWidget {{
#             background-color: {self.colors['bg_input']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             gridline-color: {self.colors['border_secondary']};
#             outline: none;
#         }}
#
#         QTableWidget::item {{
#             padding: 8px;
#             border-bottom: 1px solid {self.colors['border_secondary']};
#         }}
#
#         QTableWidget::item:selected {{
#             background-color: {self.colors['bg_selected']};
#         }}
#
#         QHeaderView::section {{
#             background-color: {self.colors['bg_header']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             padding: 8px;
#             font-weight: bold;
#         }}
#
#         /* Tab Widget */
#         QTabWidget::pane {{
#             background-color: {self.colors['bg_secondary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#         }}
#
#         QTabBar::tab {{
#             background-color: {self.colors['bg_tertiary']};
#             color: {self.colors['text_secondary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-bottom: none;
#             padding: 8px 16px;
#             margin-right: 2px;
#             border-top-left-radius: 4px;
#             border-top-right-radius: 4px;
#         }}
#
#         QTabBar::tab:selected {{
#             background-color: {self.colors['bg_secondary']};
#             color: {self.colors['text_primary']};
#             border-color: {self.colors['accent_blue']};
#         }}
#
#         QTabBar::tab:hover:!selected {{
#             background-color: {self.colors['bg_hover']};
#         }}
#
#         /* Group Box */
#         QGroupBox {{
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 6px;
#             margin-top: 10px;
#             padding-top: 10px;
#             font-weight: bold;
#         }}
#
#         QGroupBox::title {{
#             subcontrol-origin: margin;
#             left: 10px;
#             padding: 0 8px 0 8px;
#             background-color: {self.colors['bg_primary']};
#         }}
#
#         /* Frame */
#         QFrame {{
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             background-color: {self.colors['bg_secondary']};
#         }}
#
#         QFrame[frameShape="6"] {{ /* StyledPanel */
#             border: 1px solid {self.colors['border_primary']};
#             background-color: {self.colors['bg_secondary']};
#         }}
#
#         /* Scroll Bar */
#         QScrollBar:vertical {{
#             background-color: {self.colors['bg_tertiary']};
#             width: 12px;
#             border-radius: 6px;
#         }}
#
#         QScrollBar::handle:vertical {{
#             background-color: {self.colors['border_primary']};
#             border-radius: 6px;
#             min-height: 20px;
#         }}
#
#         QScrollBar::handle:vertical:hover {{
#             background-color: {self.colors['accent_blue']};
#         }}
#
#         QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
#             height: 0px;
#         }}
#
#         QScrollBar:horizontal {{
#             background-color: {self.colors['bg_tertiary']};
#             height: 12px;
#             border-radius: 6px;
#         }}
#
#         QScrollBar::handle:horizontal {{
#             background-color: {self.colors['border_primary']};
#             border-radius: 6px;
#             min-width: 20px;
#         }}
#
#         QScrollBar::handle:horizontal:hover {{
#             background-color: {self.colors['accent_blue']};
#         }}
#
#         QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
#             width: 0px;
#         }}
#
#         /* Labels */
#         QLabel {{
#             color: {self.colors['text_primary']};
#             background-color: transparent;
#         }}
#
#         QLabel.heading {{
#             font-size: 14px;
#             font-weight: bold;
#             color: {self.colors['text_accent']};
#         }}
#
#         QLabel.subheading {{
#             font-size: 12px;
#             font-weight: 600;
#             color: {self.colors['text_secondary']};
#         }}
#
#         QLabel.success {{
#             color: {self.colors['text_success']};
#         }}
#
#         QLabel.error {{
#             color: {self.colors['text_error']};
#         }}
#
#         QLabel.warning {{
#             color: {self.colors['text_warning']};
#         }}
#
#         /* Dialog */
#         QDialog {{
#             background-color: {self.colors['bg_primary']};
#             color: {self.colors['text_primary']};
#         }}
#
#         /* Message Box */
#         QMessageBox {{
#             background-color: {self.colors['bg_primary']};
#             color: {self.colors['text_primary']};
#         }}
#
#         QMessageBox QPushButton {{
#             min-width: 80px;
#             padding: 6px 20px;
#         }}
#
#         /* File Dialog */
#         QFileDialog {{
#             background-color: {self.colors['bg_primary']};
#             color: {self.colors['text_primary']};
#         }}
#
#         /* Tool Tip */
#         QToolTip {{
#             background-color: {self.colors['bg_header']};
#             color: {self.colors['text_primary']};
#             border: 1px solid {self.colors['border_primary']};
#             border-radius: 4px;
#             padding: 4px 8px;
#         }}
#         """
#
#     def get_button_stylesheet(self, button_type: str = "default"):
#         """Get specific button stylesheet"""
#         if button_type == "primary":
#             return f"""
#             QPushButton {{
#                 background-color: {self.colors['btn_primary']};
#                 color: white;
#                 border: 1px solid {self.colors['btn_primary']};
#                 border-radius: 6px;
#                 padding: 8px 16px;
#                 font-weight: 600;
#             }}
#             QPushButton:hover {{
#                 background-color: {self.colors['btn_primary_hover']};
#             }}
#             QPushButton:pressed {{
#                 background-color: {self.colors['bg_selected']};
#             }}
#             """
#         elif button_type == "success":
#             return f"""
#             QPushButton {{
#                 background-color: {self.colors['btn_success']};
#                 color: white;
#                 border: 1px solid {self.colors['btn_success']};
#                 border-radius: 6px;
#                 padding: 8px 16px;
#                 font-weight: 600;
#             }}
#             QPushButton:hover {{
#                 background-color: {self.colors['accent_green']};
#             }}
#             """
#         elif button_type == "error":
#             return f"""
#             QPushButton {{
#                 background-color: {self.colors['btn_error']};
#                 color: white;
#                 border: 1px solid {self.colors['btn_error']};
#                 border-radius: 6px;
#                 padding: 8px 16px;
#                 font-weight: 600;
#             }}
#             QPushButton:hover {{
#                 background-color: {self.colors['accent_red']};
#             }}
#             """
#         else:
#             return ""
#
#     def apply_palette(self, app):
#         """Apply color palette to application"""
#         palette = QPalette()
#
#         # Window colors
#         palette.setColor(QPalette.Window, QColor(self.colors['bg_primary']))
#         palette.setColor(QPalette.WindowText, QColor(self.colors['text_primary']))
#
#         # Base colors
#         palette.setColor(QPalette.Base, QColor(self.colors['bg_input']))
#         palette.setColor(QPalette.AlternateBase, QColor(self.colors['bg_secondary']))
#
#         # Text colors
#         palette.setColor(QPalette.Text, QColor(self.colors['text_primary']))
#         palette.setColor(QPalette.BrightText, QColor(self.colors['text_accent']))
#
#         # Button colors
#         palette.setColor(QPalette.Button, QColor(self.colors['btn_secondary']))
#         palette.setColor(QPalette.ButtonText, QColor(self.colors['text_primary']))
#
#         # Highlight colors
#         palette.setColor(QPalette.Highlight, QColor(self.colors['bg_selected']))
#         palette.setColor(QPalette.HighlightedText, QColor(self.colors['text_primary']))
#
#         app.setPalette(palette)

# Create these minimal files if PySide6 components are missing:

# src/gui/styles/jetbrains_theme.py (minimal version)
"""
Minimal JetBrains theme for fallback
"""

class JetBrainsTheme:
    """Minimal JetBrains theme implementation"""

    def __init__(self):
        self.colors = {
            'bg_primary': '#2B2B2B',
            'text_primary': '#BBBBBB',
        }

    def get_main_stylesheet(self):
        """Get basic stylesheet"""
        return f"""
        QMainWindow {{
            background-color: {self.colors['bg_primary']};
            color: {self.colors['text_primary']};
        }}
        """

    def apply_palette(self, app):
        """Apply basic palette"""
        pass

# src/gui/widgets/video_widget.py (minimal version)
"""
Minimal video widget for fallback
"""

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PySide6.QtCore import Signal

    class VideoDisplayWidget(QWidget):
        """Minimal video display widget"""

        roi_drawn = Signal(list)
        line_drawn = Signal(tuple, tuple)
        annotations_cleared = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMinimumSize(640, 480)
            self.setStyleSheet("""
                background-color: #1E1E1E; 
                border: 2px solid #555555; 
                color: white;
                border-radius: 8px;
            """)

            layout = QVBoxLayout(self)
            self.label = QLabel("Video Display\n\nLoad a video source to begin detection")
            self.label.setStyleSheet("""
                color: #BBBBBB;
                font-size: 16px;
                padding: 20px;
                text-align: center;
            """)
            layout.addWidget(self.label)

        def update_frame(self, frame):
            """Update frame display"""
            self.label.setText("Video Playing...\n\nDetection Active")

        def draw_detections(self, frame, detections, detector):
            """Draw detections on frame"""
            return frame

        def clear_display(self):
            """Clear display"""
            self.label.setText("Video Display\n\nLoad a video source to begin detection")

except ImportError:
    # Fallback for when PySide6 is not available
    class VideoDisplayWidget:
        def __init__(self, *args, **kwargs): pass
        def update_frame(self, frame): pass
        def draw_detections(self, frame, detections, detector): return frame
        def clear_display(self): pass

# src/gui/widgets/control_panel.py (minimal version)
"""
Minimal control panel for fallback
"""

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
    from PySide6.QtCore import Signal

    class ControlPanelWidget(QWidget):
        """Minimal control panel widget"""

        source_changed = Signal(dict)
        device_changed = Signal(str)
        detection_toggled = Signal()
        frame_skip_changed = Signal(int)

        def __init__(self, config_manager, parent=None):
            super().__init__(parent)
            self.config_manager = config_manager
            self.setFixedWidth(320)
            self.setStyleSheet("""
                QWidget {
                    background-color: #2B2B2B;
                    color: #BBBBBB;
                    border: 1px solid #555555;
                }
            """)

            layout = QVBoxLayout(self)

            # Title
            title = QLabel("Control Panel")
            title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title)

            # Basic controls
            self.start_button = QPushButton("Start Detection")
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: #59A869;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #6BB77A;
                }
            """)
            self.start_button.clicked.connect(self.detection_toggled.emit)
            layout.addWidget(self.start_button)

            # Status
            self.status_label = QLabel("Ready")
            self.status_label.setStyleSheet("padding: 10px; color: #9E9E9E;")
            layout.addWidget(self.status_label)

            layout.addStretch()

        def set_detection_state(self, running):
            """Set detection state"""
            if running:
                self.start_button.setText("Stop Detection")
                self.start_button.setStyleSheet("""
                    QPushButton {
                        background-color: #C75450;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #D64545;
                    }
                """)
                self.status_label.setText("Detection Running")
            else:
                self.start_button.setText("Start Detection")
                self.start_button.setStyleSheet("""
                    QPushButton {
                        background-color: #59A869;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #6BB77A;
                    }
                """)
                self.status_label.setText("Ready")

except ImportError:
    class ControlPanelWidget:
        def __init__(self, *args, **kwargs): pass
        def set_detection_state(self, running): pass

# src/gui/widgets/statistics_panel.py (minimal version)
"""
Minimal statistics panel for fallback
"""

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

    class StatisticsPanelWidget(QWidget):
        """Minimal statistics panel widget"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedWidth(350)
            self.setStyleSheet("""
                QWidget {
                    background-color: #2B2B2B;
                    color: #BBBBBB;
                    border: 1px solid #555555;
                }
            """)

            layout = QVBoxLayout(self)

            # Title
            title = QLabel("Statistics")
            title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
            layout.addWidget(title)

            # Stats display
            self.stats_label = QLabel("No data yet")
            self.stats_label.setStyleSheet("padding: 10px; color: #9E9E9E;")
            layout.addWidget(self.stats_label)

            layout.addStretch()

        def update_statistics(self, stats, vehicle_counts):
            """Update statistics display"""
            fps = stats.get('fps', 0)
            total_vehicles = sum(sum(counts.values()) for counts in vehicle_counts.values())

            stats_text = f"FPS: {fps:.1f}\n"
            stats_text += f"Total Vehicles: {total_vehicles}\n"

            for vehicle_type, counts in vehicle_counts.items():
                up_count = counts.get('up', 0)
                down_count = counts.get('down', 0)
                stats_text += f"{vehicle_type.capitalize()}: ↑{up_count} ↓{down_count}\n"

            self.stats_label.setText(stats_text)

        def clear_statistics(self):
            """Clear statistics"""
            self.stats_label.setText("No data yet")

except ImportError:
    class StatisticsPanelWidget:
        def __init__(self, *args, **kwargs): pass
        def update_statistics(self, stats, vehicle_counts): pass
        def clear_statistics(self): pass

# src/gui/widgets/toolbar.py (minimal version)
"""
Minimal toolbar for fallback
"""

try:
    from PySide6.QtWidgets import QToolBar, QLabel
    from PySide6.QtCore import Signal

    class MainToolBar(QToolBar):
        """Minimal toolbar widget"""

        play_pause_clicked = Signal()
        stop_clicked = Signal()
        settings_clicked = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.addWidget(QLabel("Toolbar Active"))

        def set_detection_state(self, running):
            """Set detection state"""
            pass

except ImportError:
    class MainToolBar:
        def __init__(self, *args, **kwargs): pass
        def set_detection_state(self, running): pass

# src/gui/dialogs/settings_dialog.py (minimal version)
"""
Minimal settings dialog for fallback
"""

try:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

    class SettingsDialog(QDialog):
        """Minimal settings dialog"""

        def __init__(self, config_manager, data_manager, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Settings")
            self.resize(400, 300)

            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Settings dialog not fully available"))

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.accept)
            layout.addWidget(ok_button)

except ImportError:
    class SettingsDialog:
        def __init__(self, *args, **kwargs): pass
        def exec(self): return False

# src/gui/dialogs/source_dialog.py (minimal version)
"""
Minimal source dialog for fallback
"""

try:
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

    class VideoSourceDialog(QDialog):
        """Minimal video source dialog"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Video Source")
            self.resize(400, 200)

            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Video source dialog not fully available"))

            ok_button = QPushButton("OK")
            ok_button.clicked.connect(self.accept)
            layout.addWidget(ok_button)

        def get_source_config(self):
            """Get source configuration"""
            return {'type': 'webcam', 'camera_id': 0}

except ImportError:
    class VideoSourceDialog:
        def __init__(self, *args, **kwargs): pass
        def exec(self): return False
        def get_source_config(self): return {'type': 'webcam', 'camera_id': 0}