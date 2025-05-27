"""
src/gui/widgets/control_panel.py - FIXED untuk PySide6
Mengganti implementasi tkinter dengan PySide6 untuk konsistensi
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QSpinBox, QSlider, QRadioButton,
    QButtonGroup, QLineEdit, QFileDialog, QFrame, QSizePolicy,
    QSpacerItem, QScrollArea, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
from typing import Dict, Any, Optional
import os


class SourceSelectionGroup(QGroupBox):
    """Video source selection group"""

    source_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__("Video Source", parent)

        # Setup group box style
        self.setStyleSheet("""
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
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Source type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))

        self.source_combo = QComboBox()
        self.source_combo.addItems(["File", "Webcam", "RTSP"])
        self.source_combo.setCurrentText("File")
        self.source_combo.setStyleSheet("""
            QComboBox {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
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
        type_layout.addWidget(self.source_combo)

        layout.addLayout(type_layout)

        # File source controls
        self.file_frame = QFrame()
        file_layout = QVBoxLayout(self.file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)

        file_input_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select video file...")
        self.file_path_edit.setStyleSheet("""
            QLineEdit {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QLineEdit:focus {
                border-color: #4A88C7;
            }
        """)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setMaximumWidth(80)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #365880;
                color: white;
                border: 1px solid #365880;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4A7BA7;
            }
            QPushButton:pressed {
                background-color: #214283;
            }
        """)

        file_input_layout.addWidget(self.file_path_edit)
        file_input_layout.addWidget(self.browse_button)
        file_layout.addLayout(file_input_layout)

        # Webcam source controls
        self.webcam_frame = QFrame()
        webcam_layout = QHBoxLayout(self.webcam_frame)
        webcam_layout.setContentsMargins(0, 0, 0, 0)

        webcam_layout.addWidget(QLabel("Camera ID:"))
        self.camera_spinbox = QSpinBox()
        self.camera_spinbox.setRange(0, 10)
        self.camera_spinbox.setValue(0)
        self.camera_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QSpinBox:hover {
                border-color: #4A88C7;
            }
        """)
        webcam_layout.addWidget(self.camera_spinbox)
        webcam_layout.addStretch()

        # RTSP source controls
        self.rtsp_frame = QFrame()
        rtsp_layout = QVBoxLayout(self.rtsp_frame)
        rtsp_layout.setContentsMargins(0, 0, 0, 0)

        self.rtsp_url_edit = QLineEdit()
        self.rtsp_url_edit.setPlaceholderText("rtsp://username:password@ip:port/stream")
        self.rtsp_url_edit.setStyleSheet("""
            QLineEdit {
                background-color: #45494A;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QLineEdit:focus {
                border-color: #4A88C7;
            }
        """)
        rtsp_layout.addWidget(QLabel("RTSP URL:"))
        rtsp_layout.addWidget(self.rtsp_url_edit)

        # Add frames to main layout
        layout.addWidget(self.file_frame)
        layout.addWidget(self.webcam_frame)
        layout.addWidget(self.rtsp_frame)

        # Load button
        self.load_button = QPushButton("Load Source")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #365880;
                color: white;
                border: 1px solid #365880;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #4A7BA7;
            }
            QPushButton:pressed {
                background-color: #214283;
            }
        """)
        layout.addWidget(self.load_button)

        # Connect signals
        self.source_combo.currentTextChanged.connect(self._on_source_type_changed)
        self.browse_button.clicked.connect(self._browse_file)
        self.load_button.clicked.connect(self._load_source)

        # Show initial frame
        self._on_source_type_changed("File")

    def _on_source_type_changed(self, source_type: str):
        """Handle source type change"""
        # Hide all frames
        self.file_frame.hide()
        self.webcam_frame.hide()
        self.rtsp_frame.hide()

        # Show appropriate frame
        if source_type == "File":
            self.file_frame.show()
        elif source_type == "Webcam":
            self.webcam_frame.show()
        elif source_type == "RTSP":
            self.rtsp_frame.show()

    def _browse_file(self):
        """Browse for video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv);;All Files (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)

    def _load_source(self):
        """Load selected source"""
        source_type = self.source_combo.currentText().lower()

        try:
            if source_type == "file":
                file_path = self.file_path_edit.text().strip()
                if not file_path:
                    QMessageBox.warning(self, "Error", "Please select a video file")
                    return
                if not os.path.exists(file_path):
                    QMessageBox.warning(self, "Error", "Selected file does not exist")
                    return

                config = {
                    'type': 'file',
                    'file_path': file_path,
                    'loop': True
                }

            elif source_type == "webcam":
                config = {
                    'type': 'webcam',
                    'camera_id': self.camera_spinbox.value()
                }

            elif source_type == "rtsp":
                rtsp_url = self.rtsp_url_edit.text().strip()
                if not rtsp_url:
                    QMessageBox.warning(self, "Error", "Please enter RTSP URL")
                    return

                config = {
                    'type': 'rtsp',
                    'rtsp_url': rtsp_url
                }

            else:
                return

            print(f"✅ Loading video source: {config}")
            self.source_changed.emit(config)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load source: {str(e)}")


class DeviceSelectionGroup(QGroupBox):
    """Processing device selection group"""

    device_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__("Processing Device", parent)

        self.setStyleSheet("""
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
        """)

        layout = QVBoxLayout(self)

        # Device selection radio buttons
        self.device_group = QButtonGroup(self)

        radio_layout = QHBoxLayout()

        self.cpu_radio = QRadioButton("CPU")
        self.cpu_radio.setChecked(True)
        self.cpu_radio.setStyleSheet("""
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
        """)

        self.gpu_radio = QRadioButton("GPU")
        self.gpu_radio.setStyleSheet(self.cpu_radio.styleSheet())

        self.device_group.addButton(self.cpu_radio, 0)
        self.device_group.addButton(self.gpu_radio, 1)

        radio_layout.addWidget(self.cpu_radio)
        radio_layout.addWidget(self.gpu_radio)
        radio_layout.addStretch()

        layout.addLayout(radio_layout)

        # Device info label
        self.device_info_label = QLabel("CPU: Intel OpenVINO Runtime")
        self.device_info_label.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(self.device_info_label)

        # Connect signals
        self.device_group.buttonToggled.connect(self._on_device_changed)

    def _on_device_changed(self, button, checked):
        """Handle device change"""
        if checked:
            device = "CPU" if button == self.cpu_radio else "GPU"
            self.device_changed.emit(device)

            # Update info label
            if device == "CPU":
                self.device_info_label.setText("CPU: Intel OpenVINO Runtime")
            else:
                self.device_info_label.setText("GPU: Intel integrated graphics")

    def set_device(self, device: str):
        """Set selected device"""
        if device.upper() == "CPU":
            self.cpu_radio.setChecked(True)
        else:
            self.gpu_radio.setChecked(True)


class PerformanceGroup(QGroupBox):
    """Performance settings group"""

    frame_skip_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__("Performance", parent)

        self.setStyleSheet("""
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
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Frame skip setting
        skip_layout = QHBoxLayout()
        skip_layout.addWidget(QLabel("Frame Skip:"))

        self.frame_skip_slider = QSlider(Qt.Horizontal)
        self.frame_skip_slider.setRange(1, 10)
        self.frame_skip_slider.setValue(2)
        self.frame_skip_slider.setTickPosition(QSlider.TicksBelow)
        self.frame_skip_slider.setTickInterval(1)
        self.frame_skip_slider.setStyleSheet("""
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
                background-color: #5C9BD1;
            }
            QSlider::sub-page:horizontal {
                background-color: #4A88C7;
                border-radius: 3px;
            }
        """)

        self.frame_skip_label = QLabel("2")
        self.frame_skip_label.setMinimumWidth(20)
        self.frame_skip_label.setAlignment(Qt.AlignCenter)
        self.frame_skip_label.setStyleSheet("""
            QLabel {
                background-color: #4C5052;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 2px 6px;
                font-weight: bold;
                color: #BBBBBB;
            }
        """)

        skip_layout.addWidget(self.frame_skip_slider)
        skip_layout.addWidget(self.frame_skip_label)
        layout.addLayout(skip_layout)

        # Performance info
        info_label = QLabel("Higher values = better performance, lower accuracy")
        info_label.setStyleSheet("color: #9E9E9E; font-size: 11px;")
        layout.addWidget(info_label)

        # Connect signals
        self.frame_skip_slider.valueChanged.connect(self._on_frame_skip_changed)

    def _on_frame_skip_changed(self, value: int):
        """Handle frame skip change"""
        self.frame_skip_label.setText(str(value))
        self.frame_skip_changed.emit(value)

    def set_frame_skip(self, value: int):
        """Set frame skip value"""
        self.frame_skip_slider.setValue(value)


class DetectionControlGroup(QGroupBox):
    """Detection control group"""

    detection_toggled = Signal()

    def __init__(self, parent=None):
        super().__init__("Detection Control", parent)

        self.setStyleSheet("""
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
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Start/Stop button
        self.start_stop_button = QPushButton("Start Detection")
        self.start_stop_button.setStyleSheet("""
            QPushButton {
                background-color: #59A869;
                color: white;
                border: 1px solid #59A869;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #6BB77A;
            }
            QPushButton:pressed {
                background-color: #4A8A56;
            }
        """)

        # Status indicator
        self.status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #ff6b6b; font-size: 16px;")
        self.status_text = QLabel("Stopped")
        self.status_text.setStyleSheet("color: #9E9E9E; font-weight: 500;")

        self.status_layout.addWidget(QLabel("Status:"))
        self.status_layout.addWidget(self.status_indicator)
        self.status_layout.addWidget(self.status_text)
        self.status_layout.addStretch()

        layout.addWidget(self.start_stop_button)
        layout.addLayout(self.status_layout)

        # Connect signals
        self.start_stop_button.clicked.connect(self.detection_toggled.emit)

        # State tracking
        self.is_running = False

    def set_detection_state(self, running: bool):
        """Set detection running state"""
        self.is_running = running

        if running:
            self.start_stop_button.setText("Stop Detection")
            self.start_stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #C75450;
                    color: white;
                    border: 1px solid #C75450;
                    border-radius: 6px;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #D64545;
                }
                QPushButton:pressed {
                    background-color: #B94A47;
                }
            """)
            self.status_indicator.setStyleSheet("color: #51cf66; font-size: 16px;")
            self.status_text.setText("Running")
            self.status_text.setStyleSheet("color: #51cf66; font-weight: 500;")
        else:
            self.start_stop_button.setText("Start Detection")
            self.start_stop_button.setStyleSheet("""
                QPushButton {
                    background-color: #59A869;
                    color: white;
                    border: 1px solid #59A869;
                    border-radius: 6px;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #6BB77A;
                }
                QPushButton:pressed {
                    background-color: #4A8A56;
                }
            """)
            self.status_indicator.setStyleSheet("color: #ff6b6b; font-size: 16px;")
            self.status_text.setText("Stopped")
            self.status_text.setStyleSheet("color: #9E9E9E; font-weight: 500;")


class StatisticsDisplayGroup(QGroupBox):
    """TAMBAHAN: Display basic statistics di control panel"""

    def __init__(self, parent=None):
        super().__init__("Quick Stats", parent)

        self.setStyleSheet("""
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
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # FPS display
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_label = QLabel("0.0")
        self.fps_label.setStyleSheet("font-weight: bold; color: #4A88C7;")
        fps_layout.addWidget(self.fps_label)
        fps_layout.addStretch()
        layout.addLayout(fps_layout)

        # ROI status
        roi_layout = QHBoxLayout()
        roi_layout.addWidget(QLabel("ROI:"))
        self.roi_status_label = QLabel("OFF")
        self.roi_status_label.setStyleSheet("font-weight: bold; color: #ff6b6b;")
        roi_layout.addWidget(self.roi_status_label)
        roi_layout.addStretch()
        layout.addLayout(roi_layout)

        # Total vehicles
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total:"))
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("font-weight: bold; color: #51cf66;")
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        layout.addLayout(total_layout)

    def update_stats(self, stats: Dict[str, Any], vehicle_counts: Dict[str, Dict[str, int]]):
        """Update quick stats display"""
        try:
            # Update FPS
            fps = stats.get('fps', 0.0)
            self.fps_label.setText(f"{fps:.1f}")

            # Update ROI status
            roi_enabled = stats.get('roi_enabled', False)
            if roi_enabled:
                self.roi_status_label.setText("ON")
                self.roi_status_label.setStyleSheet("font-weight: bold; color: #51cf66;")
            else:
                self.roi_status_label.setText("OFF")
                self.roi_status_label.setStyleSheet("font-weight: bold; color: #ff6b6b;")

            # Update total vehicles
            total = sum(sum(counts.values()) for counts in vehicle_counts.values())
            self.total_label.setText(str(total))

        except Exception as e:
            print(f"Quick stats update error: {e}")


class ControlPanelWidget(QWidget):
    """Main control panel widget - FIXED untuk PySide6"""

    # Signals
    source_changed = Signal(dict)
    device_changed = Signal(str)
    detection_toggled = Signal()
    frame_skip_changed = Signal(int)

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager

        # Setup widget
        self.setFixedWidth(320)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        # Create scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #4C5052;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4A88C7;
            }
        """)

        # Main content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Control Panel")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #BBBBBB;
                padding: 10px 0;
                border-bottom: 2px solid #4A88C7;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)

        # Add control groups
        self.source_group = SourceSelectionGroup()
        self.device_group = DeviceSelectionGroup()
        self.performance_group = PerformanceGroup()
        self.control_group = DetectionControlGroup()
        self.stats_group = StatisticsDisplayGroup()  # TAMBAHAN

        layout.addWidget(self.source_group)
        layout.addWidget(self.device_group)
        layout.addWidget(self.performance_group)
        layout.addWidget(self.control_group)
        layout.addWidget(self.stats_group)  # TAMBAHAN

        # Add stretch to push everything to the top
        layout.addStretch()

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Connect signals
        self.source_group.source_changed.connect(self._on_source_changed)
        self.device_group.device_changed.connect(self.device_changed.emit)
        self.performance_group.frame_skip_changed.connect(self.frame_skip_changed.emit)
        self.control_group.detection_toggled.connect(self.detection_toggled.emit)

        # Load initial configuration
        self._load_config()

        print("✅ Control Panel (PySide6) initialized")

    def _load_config(self):
        """Load configuration into controls"""
        try:
            config = self.config_manager.config

            # Set device
            self.device_group.set_device(config.detection.device)

            # Set frame skip
            self.performance_group.set_frame_skip(config.detection.frame_skip)

            print(f"✅ Control panel config loaded: device={config.detection.device}, skip={config.detection.frame_skip}")

        except Exception as e:
            print(f"⚠️ Error loading control panel config: {e}")

    def _on_source_changed(self, source_config: dict):
        """Handle source change with validation"""
        try:
            print(f"📹 Source changed: {source_config}")
            self.source_changed.emit(source_config)
        except Exception as e:
            print(f"❌ Error handling source change: {e}")

    def set_detection_state(self, running: bool):
        """Set detection state"""
        try:
            self.control_group.set_detection_state(running)
            print(f"🎮 Detection state changed: {'Running' if running else 'Stopped'}")
        except Exception as e:
            print(f"❌ Error setting detection state: {e}")

    def update_statistics(self, stats: Dict[str, Any], vehicle_counts: Dict[str, Dict[str, int]]):
        """TAMBAHAN: Update quick statistics display"""
        try:
            self.stats_group.update_stats(stats, vehicle_counts)
        except Exception as e:
            print(f"❌ Error updating control panel stats: {e}")

    def get_current_frame_skip(self) -> int:
        """Get current frame skip value"""
        try:
            return self.performance_group.frame_skip_slider.value()
        except Exception as e:
            print(f"❌ Error getting frame skip: {e}")
            return 2