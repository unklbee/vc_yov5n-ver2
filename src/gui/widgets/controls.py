## 3. Control Widget (`src/gui/widgets/controls.py`)

"""Simplified control widget"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QPushButton,
    QComboBox, QSpinBox, QSlider, QHBoxLayout, QFileDialog,
    QLineEdit, QRadioButton, QButtonGroup, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from typing import Dict


class ControlWidget(QWidget):
    """Main control panel widget"""

    # Signals
    start_detection = Signal()
    source_changed = Signal(dict)
    device_changed = Signal(str)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.is_running = False

        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup UI components"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setFrameShadow(QFrame.Plain)

        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Control Panel")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(title)

        # Video source group
        layout.addWidget(self.create_source_group())

        # Device group
        layout.addWidget(self.create_device_group())

        # Detection control group
        layout.addWidget(self.create_detection_group())

        # Performance group
        layout.addWidget(self.create_performance_group())

        layout.addStretch()

        # Set content to scroll area
        scroll.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_source_group(self) -> QGroupBox:
        """Create video source group"""
        group = QGroupBox("Video Source")
        group.setStyleSheet(self.get_group_style())

        layout = QVBoxLayout(group)

        # Source type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))

        self.source_combo = QComboBox()
        self.source_combo.addItems(["File", "Webcam", "RTSP"])
        type_layout.addWidget(self.source_combo)
        layout.addLayout(type_layout)

        # File selection
        file_layout = QHBoxLayout()
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Select video file...")

        self.browse_button = QPushButton("Browse")
        self.browse_button.setMaximumWidth(80)
        self.browse_button.clicked.connect(self.browse_file)

        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        # Load button
        self.load_button = QPushButton("Load Source")
        self.load_button.setStyleSheet(self.get_button_style("primary"))
        self.load_button.clicked.connect(self.load_source)
        layout.addWidget(self.load_button)

        return group

    def create_device_group(self) -> QGroupBox:
        """Create device selection group"""
        group = QGroupBox("Processing Device")
        group.setStyleSheet(self.get_group_style())

        layout = QVBoxLayout(group)

        # Device selection
        device_layout = QHBoxLayout()

        self.device_group = QButtonGroup()
        self.cpu_radio = QRadioButton("CPU")
        self.gpu_radio = QRadioButton("GPU")

        self.cpu_radio.setChecked(True)
        self.device_group.addButton(self.cpu_radio, 0)
        self.device_group.addButton(self.gpu_radio, 1)

        device_layout.addWidget(self.cpu_radio)
        device_layout.addWidget(self.gpu_radio)
        device_layout.addStretch()

        layout.addLayout(device_layout)

        # Connect signal
        self.device_group.buttonToggled.connect(self.on_device_changed)

        return group

    def create_detection_group(self) -> QGroupBox:
        """Create detection control group"""
        group = QGroupBox("Detection Control")
        group.setStyleSheet(self.get_group_style())

        layout = QVBoxLayout(group)

        # Start/Stop button
        self.start_button = QPushButton("Start Detection")
        self.start_button.setStyleSheet(self.get_button_style("success"))
        self.start_button.clicked.connect(self.start_detection.emit)
        layout.addWidget(self.start_button)

        # Status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("padding: 5px; color: #9E9E9E;")
        layout.addWidget(self.status_label)

        return group

    def create_performance_group(self) -> QGroupBox:
        """Create performance settings group"""
        group = QGroupBox("Performance")
        group.setStyleSheet(self.get_group_style())

        layout = QVBoxLayout(group)

        # Frame skip
        skip_layout = QHBoxLayout()
        skip_layout.addWidget(QLabel("Frame Skip:"))

        self.frame_skip_slider = QSlider(Qt.Horizontal)
        self.frame_skip_slider.setRange(1, 10)
        self.frame_skip_slider.setValue(2)

        self.skip_label = QLabel("2")
        self.skip_label.setMinimumWidth(20)
        self.skip_label.setAlignment(Qt.AlignCenter)

        skip_layout.addWidget(self.frame_skip_slider)
        skip_layout.addWidget(self.skip_label)
        layout.addLayout(skip_layout)

        # Connect signal
        self.frame_skip_slider.valueChanged.connect(self.on_frame_skip_changed)

        return group

    def get_group_style(self) -> str:
        """Get group box stylesheet"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #FFC66D;
                background-color: #2B2B2B;
            }
        """

    def get_button_style(self, button_type: str = "default") -> str:
        """Get button stylesheet"""
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
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 13px;
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
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover { background-color: #D64545; }
                QPushButton:pressed { background-color: #B94A47; }
            """
        }
        return styles.get(button_type, styles["primary"])

    def browse_file(self):
        """Browse for video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv);;All Files (*)"
        )

        if file_path:
            self.file_edit.setText(file_path)

    def load_source(self):
        """Load selected video source"""
        source_type = self.source_combo.currentText().lower()

        if source_type == "file":
            file_path = self.file_edit.text().strip()
            if file_path:
                config = {
                    'type': 'file',
                    'file_path': file_path
                }
                self.source_changed.emit(config)

        elif source_type == "webcam":
            config = {
                'type': 'webcam',
                'camera_id': 0
            }
            self.source_changed.emit(config)

    def on_device_changed(self, button, checked):
        """Handle device change"""
        if checked:
            device = "CPU" if button == self.cpu_radio else "GPU"
            self.device_changed.emit(device)

    def on_frame_skip_changed(self, value: int):
        """Handle frame skip change"""
        self.skip_label.setText(str(value))
        self.config_manager.update_detection(frame_skip=value)

    def set_detection_state(self, running: bool):
        """Set detection state"""
        self.is_running = running

        if running:
            self.start_button.setText("Stop Detection")
            self.start_button.setStyleSheet(self.get_button_style("danger"))
            self.status_label.setText("Status: Running")
            self.status_label.setStyleSheet("padding: 5px; color: #51cf66;")
        else:
            self.start_button.setText("Start Detection")
            self.start_button.setStyleSheet(self.get_button_style("success"))
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("padding: 5px; color: #9E9E9E;")

    def load_config(self):
        """Load configuration"""
        config = self.config_manager.config

        # Set device
        if config.detection.device == "GPU":
            self.gpu_radio.setChecked(True)
        else:
            self.cpu_radio.setChecked(True)

        # Set frame skip
        self.frame_skip_slider.setValue(config.detection.frame_skip)
        self.skip_label.setText(str(config.detection.frame_skip))