## 7. System Monitor Widget (`src/gui/widgets/system_monitor.py`)

"""
Real-time system monitoring widget
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QGridLayout
)
from PySide6.QtCore import QTimer, Signal
from PySide6.QtGui import QFont
import psutil
from typing import Dict, Any

class SystemMetricWidget(QFrame):
    """Individual system metric display"""

    def __init__(self, title: str, unit: str = "%", parent=None):
        super().__init__(parent)

        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #3C3F41;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #FFC66D; font-weight: bold; font-size: 12px;")
        layout.addWidget(self.title_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4A88C7;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Value label
        self.value_label = QLabel("0" + unit)
        self.value_label.setStyleSheet("color: #BBBBBB; font-size: 11px;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)

        self.unit = unit

    def update_value(self, value: float, max_value: float = 100):
        """Update metric value"""
        percentage = min(int((value / max_value) * 100), 100)
        self.progress_bar.setValue(percentage)

        if self.unit == "%":
            self.value_label.setText(f"{value:.1f}%")
        elif self.unit == "GB":
            self.value_label.setText(f"{value:.1f}GB")
        elif self.unit == "":
            self.value_label.setText(f"{value:.1f}")
        else:
            self.value_label.setText(f"{value:.1f}{self.unit}")

        # Color coding based on percentage
        if percentage > 90:
            color = "#ff6b6b"  # Red
        elif percentage > 75:
            color = "#FFC66D"  # Yellow
        else:
            color = "#4A88C7"  # Blue

        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)

class SystemMonitorWidget(QWidget):
    """Real-time system monitoring widget"""

    # Signals
    performance_warning = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        self.setup_ui()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Update every second

        # Warning thresholds
        self.cpu_warning_threshold = 85.0
        self.memory_warning_threshold = 90.0
        self.temp_warning_threshold = 80.0

    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("System Monitor")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFC66D; padding: 5px 0;")
        layout.addWidget(title)

        # Metrics grid
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(8)

        # Create metric widgets
        self.cpu_widget = SystemMetricWidget("CPU Usage", "%")
        self.memory_widget = SystemMetricWidget("Memory", "%")
        self.disk_widget = SystemMetricWidget("Disk I/O", "MB/s")
        self.network_widget = SystemMetricWidget("Network", "MB/s")

        # Arrange in grid
        metrics_grid.addWidget(self.cpu_widget, 0, 0)
        metrics_grid.addWidget(self.memory_widget, 0, 1)
        metrics_grid.addWidget(self.disk_widget, 1, 0)
        metrics_grid.addWidget(self.network_widget, 1, 1)

        layout.addLayout(metrics_grid)

        # Additional info
        self.info_label = QLabel("System: Normal")
        self.info_label.setStyleSheet("color: #51cf66; font-weight: 500; padding: 5px;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Initialize counters for network/disk
        self.last_disk_io = psutil.disk_io_counters()
        self.last_network_io = psutil.net_io_counters()
        self.last_update_time = time.time()

    def update_metrics(self):
        """Update all system metrics"""
        try:
            current_time = time.time()
            time_delta = current_time - self.last_update_time

            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_widget.update_value(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.memory_widget.update_value(memory.percent)

            # Disk I/O
            current_disk_io = psutil.disk_io_counters()
            if self.last_disk_io and time_delta > 0:
                disk_read_speed = (current_disk_io.read_bytes - self.last_disk_io.read_bytes) / (1024*1024) / time_delta
                disk_write_speed = (current_disk_io.write_bytes - self.last_disk_io.write_bytes) / (1024*1024) / time_delta
                disk_speed = disk_read_speed + disk_write_speed
                self.disk_widget.update_value(disk_speed, 100)  # Max 100 MB/s scale

            # Network I/O
            current_network_io = psutil.net_io_counters()
            if self.last_network_io and time_delta > 0:
                net_sent_speed = (current_network_io.bytes_sent - self.last_network_io.bytes_sent) / (1024*1024) / time_delta
                net_recv_speed = (current_network_io.bytes_recv - self.last_network_io.bytes_recv) / (1024*1024) / time_delta
                net_speed = net_sent_speed + net_recv_speed
                self.network_widget.update_value(net_speed, 50)  # Max 50 MB/s scale

            # Update last values
            self.last_disk_io = current_disk_io
            self.last_network_io = current_network_io
            self.last_update_time = current_time

            # Check for warnings
            self.check_performance_warnings(cpu_percent, memory.percent)

        except Exception as e:
            print(f"System monitor update error: {e}")

    def check_performance_warnings(self, cpu_percent: float, memory_percent: float):
        """Check for performance warnings"""
        warnings = []

        if cpu_percent > self.cpu_warning_threshold:
            warnings.append(f"High CPU usage: {cpu_percent:.1f}%")

        if memory_percent > self.memory_warning_threshold:
            warnings.append(f"High memory usage: {memory_percent:.1f}%")

        if warnings:
            warning_text = " | ".join(warnings)
            self.info_label.setText(f"⚠️ {warning_text}")
            self.info_label.setStyleSheet("color: #FFC66D; font-weight: 500; padding: 5px;")
            self.performance_warning.emit(warning_text)
        else:
            self.info_label.setText("✅ System: Normal")
            self.info_label.setStyleSheet("color: #51cf66; font-weight: 500; padding: 5px;")

    def get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'available_memory_gb': psutil.virtual_memory().available / (1024**3)
        }