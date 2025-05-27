"""
src/gui/dialogs/settings_dialog.py
Settings dialog with JetBrains-style design
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox,
    QDoubleSpinBox, QSlider, QCheckBox, QComboBox, QFileDialog,
    QFormLayout, QDialogButtonBox, QFrame, QTextEdit, QProgressBar,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon
from typing import Optional
import os
import requests
import threading


class APITestWorker(QThread):
    """Worker thread for API testing"""

    test_completed = Signal(dict)

    def __init__(self, endpoint: str, api_key: str, timeout: int):
        super().__init__()
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout

    def run(self):
        """Run API test"""
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            test_payload = {
                'test': True,
                'timestamp': '2024-01-01T00:00:00'
            }

            response = requests.post(
                self.endpoint,
                json=test_payload,
                headers=headers,
                timeout=self.timeout
            )

            result = {
                'success': True,
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'message': f"Connection successful: {response.status_code}"
            }

        except requests.exceptions.Timeout:
            result = {
                'success': False,
                'error': 'Connection timeout',
                'message': f"Request timed out after {self.timeout} seconds"
            }
        except requests.exceptions.ConnectionError:
            result = {
                'success': False,
                'error': 'Connection error',
                'message': "Could not connect to the endpoint"
            }
        except Exception as e:
            result = {
                'success': False,
                'error': 'Unknown error',
                'message': str(e)
            }

        self.test_completed.emit(result)


class DetectionTab(QWidget):
    """Detection settings tab"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Model Configuration
        model_group = QGroupBox("Model Configuration")
        model_group.setStyleSheet(self._get_group_style())
        model_layout = QFormLayout(model_group)

        # Model path
        model_path_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setText(config_manager.config.detection.model_path)
        self.model_browse_button = QPushButton("Browse")
        self.model_browse_button.setMaximumWidth(80)
        self.model_browse_button.clicked.connect(self._browse_model)

        model_path_layout.addWidget(self.model_path_edit)
        model_path_layout.addWidget(self.model_browse_button)
        model_layout.addRow("Model Path:", model_path_layout)

        # Detection Parameters
        params_group = QGroupBox("Detection Parameters")
        params_group.setStyleSheet(self._get_group_style())
        params_layout = QFormLayout(params_group)

        # Confidence threshold
        conf_layout = QHBoxLayout()
        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(10, 90)
        self.conf_slider.setValue(int(config_manager.config.detection.conf_threshold * 100))
        self.conf_value_label = QLabel(f"{config_manager.config.detection.conf_threshold:.2f}")
        self.conf_value_label.setMinimumWidth(40)
        self.conf_value_label.setAlignment(Qt.AlignCenter)
        self.conf_value_label.setStyleSheet("background-color: #4C5052; padding: 4px; border-radius: 3px;")

        conf_layout.addWidget(self.conf_slider)
        conf_layout.addWidget(self.conf_value_label)
        params_layout.addRow("Confidence Threshold:", conf_layout)

        # NMS threshold
        nms_layout = QHBoxLayout()
        self.nms_slider = QSlider(Qt.Horizontal)
        self.nms_slider.setRange(10, 90)
        self.nms_slider.setValue(int(config_manager.config.detection.nms_threshold * 100))
        self.nms_value_label = QLabel(f"{config_manager.config.detection.nms_threshold:.2f}")
        self.nms_value_label.setMinimumWidth(40)
        self.nms_value_label.setAlignment(Qt.AlignCenter)
        self.nms_value_label.setStyleSheet("background-color: #4C5052; padding: 4px; border-radius: 3px;")

        nms_layout.addWidget(self.nms_slider)
        nms_layout.addWidget(self.nms_value_label)
        params_layout.addRow("NMS Threshold:", nms_layout)

        # Input shape
        shape_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(320, 1920)
        self.width_spinbox.setValue(config_manager.config.detection.input_shape[0])

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(240, 1080)
        self.height_spinbox.setValue(config_manager.config.detection.input_shape[1])

        shape_layout.addWidget(self.width_spinbox)
        shape_layout.addWidget(QLabel("×"))
        shape_layout.addWidget(self.height_spinbox)
        shape_layout.addStretch()
        params_layout.addRow("Input Shape:", shape_layout)

        layout.addWidget(model_group)
        layout.addWidget(params_group)
        layout.addStretch()

        # Connect signals
        self.conf_slider.valueChanged.connect(self._update_conf_label)
        self.nms_slider.valueChanged.connect(self._update_nms_label)

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

    def _browse_model(self):
        """Browse for model file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Model File",
            "",
            "OpenVINO Models (*.xml);;All Files (*)"
        )

        if file_path:
            self.model_path_edit.setText(file_path)

    def _update_conf_label(self, value: int):
        """Update confidence label"""
        conf_value = value / 100.0
        self.conf_value_label.setText(f"{conf_value:.2f}")

    def _update_nms_label(self, value: int):
        """Update NMS label"""
        nms_value = value / 100.0
        self.nms_value_label.setText(f"{nms_value:.2f}")

    def get_config(self) -> dict:
        """Get detection configuration"""
        return {
            'model_path': self.model_path_edit.text(),
            'conf_threshold': self.conf_slider.value() / 100.0,
            'nms_threshold': self.nms_slider.value() / 100.0,
            'input_shape': (self.width_spinbox.value(), self.height_spinbox.value())
        }


class TrackerTab(QWidget):
    """Tracker settings tab"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Tracker Parameters
        tracker_group = QGroupBox("Tracker Parameters")
        tracker_group.setStyleSheet(self._get_group_style())
        tracker_layout = QFormLayout(tracker_group)

        # Max age
        self.max_age_spinbox = QSpinBox()
        self.max_age_spinbox.setRange(1, 10)
        self.max_age_spinbox.setValue(config_manager.config.tracker.max_age)
        tracker_layout.addRow("Max Age:", self.max_age_spinbox)

        # Min hits
        self.min_hits_spinbox = QSpinBox()
        self.min_hits_spinbox.setRange(1, 10)
        self.min_hits_spinbox.setValue(config_manager.config.tracker.min_hits)
        tracker_layout.addRow("Min Hits:", self.min_hits_spinbox)

        # IoU threshold
        iou_layout = QHBoxLayout()
        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setRange(10, 80)
        self.iou_slider.setValue(int(config_manager.config.tracker.iou_threshold * 100))
        self.iou_value_label = QLabel(f"{config_manager.config.tracker.iou_threshold:.2f}")
        self.iou_value_label.setMinimumWidth(40)
        self.iou_value_label.setAlignment(Qt.AlignCenter)
        self.iou_value_label.setStyleSheet("background-color: #4C5052; padding: 4px; border-radius: 3px;")

        iou_layout.addWidget(self.iou_slider)
        iou_layout.addWidget(self.iou_value_label)
        tracker_layout.addRow("IoU Threshold:", iou_layout)

        # Trail length
        self.trail_length_spinbox = QSpinBox()
        self.trail_length_spinbox.setRange(10, 100)
        self.trail_length_spinbox.setValue(config_manager.config.tracker.trail_length)
        tracker_layout.addRow("Trail Length:", self.trail_length_spinbox)

        layout.addWidget(tracker_group)
        layout.addStretch()

        # Connect signals
        self.iou_slider.valueChanged.connect(self._update_iou_label)

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

    def _update_iou_label(self, value: int):
        """Update IoU label"""
        iou_value = value / 100.0
        self.iou_value_label.setText(f"{iou_value:.2f}")

    def get_config(self) -> dict:
        """Get tracker configuration"""
        return {
            'max_age': self.max_age_spinbox.value(),
            'min_hits': self.min_hits_spinbox.value(),
            'iou_threshold': self.iou_slider.value() / 100.0,
            'trail_length': self.trail_length_spinbox.value()
        }


class DataStorageTab(QWidget):
    """Data storage settings tab"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Storage Enable/Disable
        self.storage_enabled_checkbox = QCheckBox("Enable Data Storage")
        self.storage_enabled_checkbox.setChecked(config_manager.config.data_storage.enabled)
        layout.addWidget(self.storage_enabled_checkbox)

        # Storage Configuration
        storage_group = QGroupBox("Storage Configuration")
        storage_group.setStyleSheet(self._get_group_style())
        storage_layout = QFormLayout(storage_group)

        # Save interval
        self.save_interval_spinbox = QSpinBox()
        self.save_interval_spinbox.setRange(30, 3600)
        self.save_interval_spinbox.setValue(config_manager.config.data_storage.save_interval)
        self.save_interval_spinbox.setSuffix(" seconds")
        storage_layout.addRow("Save Interval:", self.save_interval_spinbox)

        # Output directory
        dir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(config_manager.config.data_storage.output_directory)
        self.dir_browse_button = QPushButton("Browse")
        self.dir_browse_button.setMaximumWidth(80)
        self.dir_browse_button.clicked.connect(self._browse_directory)

        dir_layout.addWidget(self.output_dir_edit)
        dir_layout.addWidget(self.dir_browse_button)
        storage_layout.addRow("Output Directory:", dir_layout)

        # Data format
        self.format_combo = QComboBox()
        self.format_combo.addItems(["json", "csv", "both"])
        self.format_combo.setCurrentText(config_manager.config.data_storage.format)
        storage_layout.addRow("Data Format:", self.format_combo)

        layout.addWidget(storage_group)
        layout.addStretch()

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

    def _browse_directory(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory"
        )

        if directory:
            self.output_dir_edit.setText(directory)

    def get_config(self) -> dict:
        """Get storage configuration"""
        return {
            'enabled': self.storage_enabled_checkbox.isChecked(),
            'save_interval': self.save_interval_spinbox.value(),
            'output_directory': self.output_dir_edit.text(),
            'format': self.format_combo.currentText()
        }


class APITab(QWidget):
    """API settings tab"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # API Enable/Disable
        self.api_enabled_checkbox = QCheckBox("Enable API Integration")
        self.api_enabled_checkbox.setChecked(config_manager.config.api.enabled)
        layout.addWidget(self.api_enabled_checkbox)

        # API Configuration
        api_group = QGroupBox("API Configuration")
        api_group.setStyleSheet(self._get_group_style())
        api_layout = QFormLayout(api_group)

        # Endpoint URL
        self.endpoint_edit = QLineEdit()
        self.endpoint_edit.setText(config_manager.config.api.endpoint)
        self.endpoint_edit.setPlaceholderText("https://api.example.com/vehicle-data")
        api_layout.addRow("Endpoint URL:", self.endpoint_edit)

        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(config_manager.config.api.api_key)
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Enter API key (optional)")
        api_layout.addRow("API Key:", self.api_key_edit)

        # Send interval
        self.send_interval_spinbox = QSpinBox()
        self.send_interval_spinbox.setRange(10, 3600)
        self.send_interval_spinbox.setValue(config_manager.config.api.send_interval)
        self.send_interval_spinbox.setSuffix(" seconds")
        api_layout.addRow("Send Interval:", self.send_interval_spinbox)

        # Timeout
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 120)
        self.timeout_spinbox.setValue(config_manager.config.api.timeout)
        self.timeout_spinbox.setSuffix(" seconds")
        api_layout.addRow("Timeout:", self.timeout_spinbox)

        layout.addWidget(api_group)

        # Test API
        test_group = QGroupBox("Connection Test")
        test_group.setStyleSheet(self._get_group_style())
        test_layout = QVBoxLayout(test_group)

        test_button_layout = QHBoxLayout()
        self.test_button = QPushButton("Test API Connection")
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #365880;
                color: white;
                border: 1px solid #365880;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4A7BA7;
            }
            QPushButton:disabled {
                background-color: #4C5052;
                color: #6C6C6C;
            }
        """)
        self.test_button.clicked.connect(self._test_api_connection)

        test_button_layout.addWidget(self.test_button)
        test_button_layout.addStretch()

        # Test result area
        self.test_result_text = QTextEdit()
        self.test_result_text.setMaximumHeight(100)
        self.test_result_text.setReadOnly(True)
        self.test_result_text.setPlainText("Click 'Test API Connection' to verify your settings.")

        # Progress bar
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)

        test_layout.addLayout(test_button_layout)
        test_layout.addWidget(self.test_progress)
        test_layout.addWidget(self.test_result_text)

        layout.addWidget(test_group)
        layout.addStretch()

        # API test worker
        self.api_test_worker = None

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

    def _test_api_connection(self):
        """Test API connection"""
        endpoint = self.endpoint_edit.text().strip()
        if not endpoint:
            self.test_result_text.setPlainText("❌ Please enter an endpoint URL")
            return

        # Start test
        self.test_button.setEnabled(False)
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # Indeterminate progress
        self.test_result_text.setPlainText("🔄 Testing connection...")

        # Create and start worker thread
        self.api_test_worker = APITestWorker(
            endpoint,
            self.api_key_edit.text().strip(),
            self.timeout_spinbox.value()
        )
        self.api_test_worker.test_completed.connect(self._on_test_completed)
        self.api_test_worker.start()

    def _on_test_completed(self, result: dict):
        """Handle API test completion"""
        self.test_button.setEnabled(True)
        self.test_progress.setVisible(False)

        if result['success']:
            status_text = (f"✅ Connection successful!\n"
                           f"Status Code: {result['status_code']}\n"
                           f"Response Time: {result['response_time']:.2f}s")
        else:
            status_text = f"❌ Connection failed: {result['message']}"

        self.test_result_text.setPlainText(status_text)

    def get_config(self) -> dict:
        """Get API configuration"""
        return {
            'enabled': self.api_enabled_checkbox.isChecked(),
            'endpoint': self.endpoint_edit.text().strip(),
            'api_key': self.api_key_edit.text().strip(),
            'send_interval': self.send_interval_spinbox.value(),
            'timeout': self.timeout_spinbox.value()
        }


class SettingsDialog(QDialog):
    """Main settings dialog"""

    def __init__(self, config_manager, data_manager, parent=None):
        super().__init__(parent)

        self.config_manager = config_manager
        self.data_manager = data_manager

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(600, 500)

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
                padding: 8px 16px;
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
        self.detection_tab = DetectionTab(self.config_manager)
        self.tracker_tab = TrackerTab(self.config_manager)
        self.storage_tab = DataStorageTab(self.config_manager)
        self.api_tab = APITab(self.config_manager)

        self.tab_widget.addTab(self.detection_tab, "Detection")
        self.tab_widget.addTab(self.tracker_tab, "Tracker")
        self.tab_widget.addTab(self.storage_tab, "Data Storage")
        self.tab_widget.addTab(self.api_tab, "API")

        layout.addWidget(self.tab_widget)

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        self.button_box.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background-color: #4C5052;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px 16px;
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
        self.button_box.button(QDialogButtonBox.Apply).clicked.connect(self._on_apply_clicked)

    def _on_ok_clicked(self):
        """Handle OK button click"""
        if self._apply_settings():
            self.accept()

    def _on_apply_clicked(self):
        """Handle Apply button click"""
        self._apply_settings()

    def _apply_settings(self) -> bool:
        """Apply all settings"""
        try:
            # Get configurations from tabs
            detection_config = self.detection_tab.get_config()
            tracker_config = self.tracker_tab.get_config()
            storage_config = self.storage_tab.get_config()
            api_config = self.api_tab.get_config()

            # Update config manager
            self.config_manager.update_detection_config(**detection_config)

            # Update tracker config
            tracker_cfg = self.config_manager.config.tracker
            for key, value in tracker_config.items():
                setattr(tracker_cfg, key, value)

            # Update storage config
            self.config_manager.update_storage_config(**storage_config)

            # Update API config
            self.config_manager.update_api_config(**api_config)

            # Save configuration
            self.config_manager.save_config()

            # Show success message
            QMessageBox.information(self, "Success", "Settings applied successfully!")
            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {str(e)}")
            return False