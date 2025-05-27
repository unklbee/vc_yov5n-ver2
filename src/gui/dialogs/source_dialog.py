"""
src/gui/dialogs/source_dialog.py
Video source selection dialog
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QSpinBox, QComboBox, QFileDialog,
    QDialogButtonBox, QFormLayout, QFrame, QMessageBox,
    QCheckBox, QTextEdit, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
import os


class FileSourceTab(QWidget):
    """File source configuration tab"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # File selection group
        file_group = QGroupBox("Video File Selection")
        file_group.setStyleSheet(self._get_group_style())
        file_layout = QFormLayout(file_group)

        # File path
        file_path_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select a video file...")

        self.browse_button = QPushButton("Browse")
        self.browse_button.setMaximumWidth(80)
        self.browse_button.setStyleSheet(self._get_button_style())
        self.browse_button.clicked.connect(self._browse_file)

        file_path_layout.addWidget(self.file_path_edit)
        file_path_layout.addWidget(self.browse_button)
        file_layout.addRow("File Path:", file_path_layout)

        # Playback options
        options_group = QGroupBox("Playback Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QFormLayout(options_group)

        # Loop video
        self.loop_checkbox = QCheckBox("Loop video when finished")
        self.loop_checkbox.setChecked(True)
        options_layout.addRow("Loop:", self.loop_checkbox)

        # Start position
        self.start_position_spinbox = QSpinBox()
        self.start_position_spinbox.setRange(0, 99999)
        self.start_position_spinbox.setValue(0)
        self.start_position_spinbox.setSuffix(" seconds")
        options_layout.addRow("Start Position:", self.start_position_spinbox)

        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addStretch()

        # File info area
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(80)
        self.info_text.setReadOnly(True)
        self.info_text.setPlainText("Select a video file to see information...")
        layout.addWidget(self.info_text)

        # Connect signals
        self.file_path_edit.textChanged.connect(self._update_file_info)

    def _get_group_style(self) -> str:
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

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
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
        """

    def _browse_file(self):
        """Browse for video file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.m4v);;All Files (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)

    def _update_file_info(self, file_path: str):
        """Update file information"""
        if not file_path or not os.path.exists(file_path):
            self.info_text.setPlainText("Select a valid video file to see information...")
            return

        try:
            # Get file info
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)

            info_text = f"File: {os.path.basename(file_path)}\n"
            info_text += f"Size: {file_size_mb:.1f} MB\n"
            info_text += f"Path: {file_path}"

            self.info_text.setPlainText(info_text)

        except Exception as e:
            self.info_text.setPlainText(f"Error reading file info: {str(e)}")

    def get_config(self) -> dict:
        """Get file source configuration"""
        return {
            'type': 'file',
            'file_path': self.file_path_edit.text().strip(),
            'loop': self.loop_checkbox.isChecked(),
            'start_position': self.start_position_spinbox.value()
        }

    def is_valid(self) -> tuple:
        """Check if configuration is valid"""
        file_path = self.file_path_edit.text().strip()

        if not file_path:
            return False, "Please select a video file"

        if not os.path.exists(file_path):
            return False, "Selected file does not exist"

        return True, ""


class WebcamSourceTab(QWidget):
    """Webcam source configuration tab"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Camera selection group
        camera_group = QGroupBox("Camera Selection")
        camera_group.setStyleSheet(self._get_group_style())
        camera_layout = QFormLayout(camera_group)

        # Camera ID
        self.camera_id_spinbox = QSpinBox()
        self.camera_id_spinbox.setRange(0, 10)
        self.camera_id_spinbox.setValue(0)
        camera_layout.addRow("Camera ID:", self.camera_id_spinbox)

        # Camera resolution
        resolution_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(320, 1920)
        self.width_spinbox.setValue(1280)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(240, 1080)
        self.height_spinbox.setValue(720)

        resolution_layout.addWidget(self.width_spinbox)
        resolution_layout.addWidget(QLabel("×"))
        resolution_layout.addWidget(self.height_spinbox)
        resolution_layout.addStretch()
        camera_layout.addRow("Resolution:", resolution_layout)

        # Frame rate
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(15, 60)
        self.fps_spinbox.setValue(30)
        camera_layout.addRow("Frame Rate:", self.fps_spinbox)

        layout.addWidget(camera_group)

        # Camera options
        options_group = QGroupBox("Camera Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QFormLayout(options_group)

        # Auto exposure
        self.auto_exposure_checkbox = QCheckBox("Enable auto exposure")
        self.auto_exposure_checkbox.setChecked(True)
        options_layout.addRow("Auto Exposure:", self.auto_exposure_checkbox)

        # Buffer size
        self.buffer_size_spinbox = QSpinBox()
        self.buffer_size_spinbox.setRange(1, 10)
        self.buffer_size_spinbox.setValue(1)
        options_layout.addRow("Buffer Size:", self.buffer_size_spinbox)

        layout.addWidget(options_group)
        layout.addStretch()

        # Test button
        self.test_button = QPushButton("Test Camera")
        self.test_button.setStyleSheet(self._get_button_style())
        self.test_button.clicked.connect(self._test_camera)
        layout.addWidget(self.test_button)

        # Test result
        self.test_result_text = QTextEdit()
        self.test_result_text.setMaximumHeight(60)
        self.test_result_text.setReadOnly(True)
        self.test_result_text.setPlainText("Click 'Test Camera' to verify camera access...")
        layout.addWidget(self.test_result_text)

    def _get_group_style(self) -> str:
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

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #365880;
                color: white;
                border: 1px solid #365880;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4A7BA7;
            }
            QPushButton:pressed {
                background-color: #214283;
            }
        """

    def _test_camera(self):
        """Test camera access"""
        import cv2

        camera_id = self.camera_id_spinbox.value()

        try:
            cap = cv2.VideoCapture(camera_id)

            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                if ret:
                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    actual_fps = cap.get(cv2.CAP_PROP_FPS)

                    result_text = (f"✅ Camera {camera_id} is working!\n"
                                   f"Resolution: {actual_width}×{actual_height}\n"
                                   f"FPS: {actual_fps:.1f}")
                    self.test_result_text.setPlainText(result_text)
                else:
                    self.test_result_text.setPlainText(f"❌ Camera {camera_id} failed to capture frame")

                cap.release()
            else:
                self.test_result_text.setPlainText(f"❌ Cannot access camera {camera_id}")

        except Exception as e:
            self.test_result_text.setPlainText(f"❌ Camera test error: {str(e)}")

    def get_config(self) -> dict:
        """Get webcam source configuration"""
        return {
            'type': 'webcam',
            'camera_id': self.camera_id_spinbox.value(),
            'width': self.width_spinbox.value(),
            'height': self.height_spinbox.value(),
            'fps': self.fps_spinbox.value(),
            'auto_exposure': self.auto_exposure_checkbox.isChecked(),
            'buffer_size': self.buffer_size_spinbox.value()
        }

    def is_valid(self) -> tuple:
        """Check if configuration is valid"""
        return True, ""


class RTSPSourceTab(QWidget):
    """RTSP source configuration tab"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # RTSP configuration group
        rtsp_group = QGroupBox("RTSP Stream Configuration")
        rtsp_group.setStyleSheet(self._get_group_style())
        rtsp_layout = QFormLayout(rtsp_group)

        # RTSP URL
        self.rtsp_url_edit = QLineEdit()
        self.rtsp_url_edit.setPlaceholderText("rtsp://username:password@ip:port/stream")
        rtsp_layout.addRow("RTSP URL:", self.rtsp_url_edit)

        # Username and password (optional)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username (optional)")
        rtsp_layout.addRow("Username:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password (optional)")
        rtsp_layout.addRow("Password:", self.password_edit)

        layout.addWidget(rtsp_group)

        # Connection options
        options_group = QGroupBox("Connection Options")
        options_group.setStyleSheet(self._get_group_style())
        options_layout = QFormLayout(options_group)

        # Connection timeout
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 60)
        self.timeout_spinbox.setValue(10)
        self.timeout_spinbox.setSuffix(" seconds")
        options_layout.addRow("Timeout:", self.timeout_spinbox)

        # Reconnect attempts
        self.reconnect_spinbox = QSpinBox()
        self.reconnect_spinbox.setRange(1, 10)
        self.reconnect_spinbox.setValue(3)
        options_layout.addRow("Reconnect Attempts:", self.reconnect_spinbox)

        # Buffer size
        self.buffer_size_spinbox = QSpinBox()
        self.buffer_size_spinbox.setRange(1, 10)
        self.buffer_size_spinbox.setValue(1)
        options_layout.addRow("Buffer Size:", self.buffer_size_spinbox)

        layout.addWidget(options_group)
        layout.addStretch()

        # Test connection button
        self.test_button = QPushButton("Test RTSP Connection")
        self.test_button.setStyleSheet(self._get_button_style())
        self.test_button.clicked.connect(self._test_rtsp_connection)
        layout.addWidget(self.test_button)

        # Test result
        self.test_result_text = QTextEdit()
        self.test_result_text.setMaximumHeight(80)
        self.test_result_text.setReadOnly(True)
        self.test_result_text.setPlainText("Click 'Test RTSP Connection' to verify stream access...")
        layout.addWidget(self.test_result_text)

    def _get_group_style(self) -> str:
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

    def _get_button_style(self) -> str:
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #365880;
                color: white;
                border: 1px solid #365880;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4A7BA7;
            }
            QPushButton:pressed {
                background-color: #214283;
            }
        """

    def _test_rtsp_connection(self):
        """Test RTSP connection"""
        import cv2

        rtsp_url = self.rtsp_url_edit.text().strip()

        if not rtsp_url:
            self.test_result_text.setPlainText("❌ Please enter an RTSP URL")
            return

        # Build complete URL with credentials if provided
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if username and password:
            # Insert credentials into URL
            if "://" in rtsp_url:
                protocol, rest = rtsp_url.split("://", 1)
                rtsp_url = f"{protocol}://{username}:{password}@{rest}"

        try:
            self.test_result_text.setPlainText("🔄 Testing RTSP connection...")

            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)

                    result_text = (f"✅ RTSP connection successful!\n"
                                   f"Resolution: {width}×{height}\n"
                                   f"FPS: {fps:.1f}")
                    self.test_result_text.setPlainText(result_text)
                else:
                    self.test_result_text.setPlainText("❌ Connected but failed to read frame")

                cap.release()
            else:
                self.test_result_text.setPlainText("❌ Cannot connect to RTSP stream")

        except Exception as e:
            self.test_result_text.setPlainText(f"❌ RTSP test error: {str(e)}")

    def get_config(self) -> dict:
        """Get RTSP source configuration"""
        config = {
            'type': 'rtsp',
            'rtsp_url': self.rtsp_url_edit.text().strip(),
            'timeout': self.timeout_spinbox.value(),
            'reconnect_attempts': self.reconnect_spinbox.value(),
            'buffer_size': self.buffer_size_spinbox.value()
        }

        # Add credentials if provided
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if username:
            config['username'] = username
        if password:
            config['password'] = password

        return config

    def is_valid(self) -> tuple:
        """Check if configuration is valid"""
        rtsp_url = self.rtsp_url_edit.text().strip()

        if not rtsp_url:
            return False, "Please enter an RTSP URL"

        if not rtsp_url.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://')):
            return False, "Invalid URL format. Use rtsp://, rtmp://, http://, or https://"

        return True, ""


class VideoSourceDialog(QDialog):
    """Video source selection dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Video Source")
        self.setModal(True)
        self.resize(500, 400)

        # Apply JetBrains style
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #4C5052;
                color: #9E9E9E;
                border: 1px solid #555555;
                border-bottom: none;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #2B2B2B;
                color: #BBBBBB;
                border-color: #4A88C7;
            }
            QTabBar::tab:hover:!selected {
                background-color: #5C6365;
            }
        """)

        # Create tabs
        self.file_tab = FileSourceTab()
        self.webcam_tab = WebcamSourceTab()
        self.rtsp_tab = RTSPSourceTab()

        self.tab_widget.addTab(self.file_tab, "📁 Video File")
        self.tab_widget.addTab(self.webcam_tab, "📷 Webcam")
        self.tab_widget.addTab(self.rtsp_tab, "🌐 RTSP Stream")

        layout.addWidget(self.tab_widget)

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background-color: #4C5052;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 500;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #5C6365;
                border-color: #4A88C7;
            }
            QDialogButtonBox QPushButton:default {
                background-color: #365880;
                color: white;
                border-color: #365880;
            }
            QDialogButtonBox QPushButton:default:hover {
                background-color: #4A7BA7;
            }
        """)

        layout.addWidget(self.button_box)

        # Connect signals
        self.button_box.accepted.connect(self._on_ok_clicked)
        self.button_box.rejected.connect(self.reject)

    def _on_ok_clicked(self):
        """Handle OK button click"""
        # Get current tab
        current_tab = self.tab_widget.currentWidget()

        # Validate configuration
        is_valid, error_message = current_tab.is_valid()

        if not is_valid:
            QMessageBox.warning(self, "Invalid Configuration", error_message)
            return

        self.accept()

    def get_source_config(self) -> dict:
        """Get selected source configuration"""
        current_tab = self.tab_widget.currentWidget()
        return current_tab.get_config()