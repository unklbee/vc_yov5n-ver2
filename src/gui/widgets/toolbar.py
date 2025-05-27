"""
src/gui/widgets/toolbar.py
Fixed main toolbar with JetBrains-style design
"""

from PySide6.QtWidgets import (
    QToolBar, QToolButton, QLabel, QFrame, QHBoxLayout,
    QWidget, QSizePolicy, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QAction, QFont


class ToolbarSeparator(QWidget):
    """Custom toolbar separator"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(1)
        self.setFixedHeight(24)
        self.setStyleSheet("""
            QWidget {
                background-color: #555555;
                margin: 2px 8px;
            }
        """)


class MainToolBar(QToolBar):
    """Main application toolbar"""

    # Signals
    play_pause_clicked = Signal()
    stop_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)

        # Configure toolbar
        self.setMovable(False)
        self.setFloatable(False)
        self.setIconSize(QSize(20, 20))
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.setStyleSheet("""
            QToolBar {
                background-color: #3C3F41;
                border: none;
                padding: 4px;
                spacing: 4px;
            }
            QToolButton {
                background-color: transparent;
                color: #BBBBBB;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 12px;
                margin: 1px;
                font-weight: 500;
            }
            QToolButton:hover {
                background-color: #4B6EAF;
                border-color: #4A88C7;
            }
            QToolButton:pressed {
                background-color: #214283;
            }
            QToolButton:checked {
                background-color: #365880;
                border-color: #4A88C7;
                color: white;
            }
            QToolButton:disabled {
                color: #6C6C6C;
                background-color: transparent;
            }
        """)

        self._create_actions()
        self._setup_toolbar()

        # State tracking
        self.is_detection_running = False

    def _create_actions(self):
        """Create toolbar actions"""
        # File actions
        self.new_action = QAction("New", self)
        self.new_action.setToolTip("Create new project (Ctrl+N)")
        self.new_action.setShortcut("Ctrl+N")

        self.open_action = QAction("Open", self)
        self.open_action.setToolTip("Open video source (Ctrl+O)")
        self.open_action.setShortcut("Ctrl+O")

        self.save_action = QAction("Save", self)
        self.save_action.setToolTip("Save configuration (Ctrl+S)")
        self.save_action.setShortcut("Ctrl+S")

        # Detection control actions
        self.play_pause_action = QAction("Start", self)
        self.play_pause_action.setToolTip("Start/Stop detection (F5)")
        self.play_pause_action.setShortcut("F5")
        self.play_pause_action.setCheckable(False)

        self.stop_action = QAction("Stop", self)
        self.stop_action.setToolTip("Stop detection")
        self.stop_action.setEnabled(False)

        # View actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.setToolTip("Open settings (Ctrl+Alt+S)")
        self.settings_action.setShortcut("Ctrl+Alt+S")

        # Connect signals
        self.play_pause_action.triggered.connect(self.play_pause_clicked.emit)
        self.stop_action.triggered.connect(self.stop_clicked.emit)
        self.settings_action.triggered.connect(self.settings_clicked.emit)

    def _setup_toolbar(self):
        """Setup toolbar layout"""
        # File group
        self.addAction(self.new_action)
        self.addAction(self.open_action)
        self.addAction(self.save_action)

        # Add separator
        self.addSeparator()

        # Detection control group
        self.addAction(self.play_pause_action)
        self.addAction(self.stop_action)

        # Add separator
        self.addSeparator()

        # Quick settings
        self._add_quick_settings()

        # Add separator
        self.addSeparator()

        # View and settings
        self.addAction(self.settings_action)

        # Add spacer to push remaining items to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.addWidget(spacer)

        # Status indicators
        self._add_status_indicators()

    def _add_quick_settings(self):
        """Add quick settings controls"""
        # Device selection
        device_label = QLabel("Device:")
        device_label.setStyleSheet("color: #BBBBBB; margin: 0 5px;")
        self.addWidget(device_label)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["CPU", "GPU"])
        self.device_combo.setMinimumWidth(80)
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                margin: 0 5px;
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
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3C3F41;
                color: #BBBBBB;
                border: 1px solid #555555;
                selection-background-color: #4B6EAF;
                outline: none;
            }
        """)
        self.addWidget(self.device_combo)

        # Frame skip
        skip_label = QLabel("Skip:")
        skip_label.setStyleSheet("color: #BBBBBB; margin: 0 5px;")
        self.addWidget(skip_label)

        self.frame_skip_spinbox = QSpinBox()
        self.frame_skip_spinbox.setRange(1, 10)
        self.frame_skip_spinbox.setValue(2)
        self.frame_skip_spinbox.setMinimumWidth(60)
        self.frame_skip_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
                margin: 0 5px;
            }
            QSpinBox:hover {
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
        """)
        self.addWidget(self.frame_skip_spinbox)

    def _add_status_indicators(self):
        """Add status indicators to the right side"""
        # Detection status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #9E9E9E;
                background-color: #4C5052;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 12px;
                margin: 0 5px;
                font-weight: 500;
            }
        """)
        self.addWidget(self.status_label)

        # Memory usage (placeholder)
        self.memory_label = QLabel("Mem: 0MB")
        self.memory_label.setStyleSheet("""
            QLabel {
                color: #9E9E9E;
                padding: 4px 8px;
                margin: 0 5px;
                font-size: 11px;
            }
        """)
        self.addWidget(self.memory_label)

    def set_detection_state(self, running: bool):
        """Update toolbar based on detection state"""
        self.is_detection_running = running

        if running:
            self.play_pause_action.setText("Pause")
            self.play_pause_action.setToolTip("Pause detection (F5)")
            self.stop_action.setEnabled(True)
            self.status_label.setText("Running")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background-color: #59A869;
                    border: 1px solid #59A869;
                    border-radius: 4px;
                    padding: 4px 12px;
                    margin: 0 5px;
                    font-weight: 500;
                }
            """)
        else:
            self.play_pause_action.setText("Start")
            self.play_pause_action.setToolTip("Start detection (F5)")
            self.stop_action.setEnabled(False)
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #9E9E9E;
                    background-color: #4C5052;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 4px 12px;
                    margin: 0 5px;
                    font-weight: 500;
                }
            """)

    def update_memory_usage(self, memory_mb: float):
        """Update memory usage display"""
        self.memory_label.setText(f"Mem: {memory_mb:.0f}MB")

        # Color code based on usage
        if memory_mb > 1000:  # > 1GB
            color = "#ff6b6b"  # Red
        elif memory_mb > 500:  # > 500MB
            color = "#FFC66D"  # Yellow
        else:
            color = "#9E9E9E"  # Gray

        self.memory_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                padding: 4px 8px;
                margin: 0 5px;
                font-size: 11px;
            }}
        """)

    def get_device_selection(self) -> str:
        """Get selected device"""
        return self.device_combo.currentText()

    def set_device_selection(self, device: str):
        """Set device selection"""
        index = self.device_combo.findText(device)
        if index >= 0:
            self.device_combo.setCurrentIndex(index)

    def get_frame_skip(self) -> int:
        """Get frame skip value"""
        return self.frame_skip_spinbox.value()

    def set_frame_skip(self, value: int):
        """Set frame skip value"""
        self.frame_skip_spinbox.setValue(value)