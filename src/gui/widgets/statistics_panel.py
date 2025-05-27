"""
src/gui/widgets/statistics_panel.py
Statistics panel widget with real-time data visualization
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGroupBox, QProgressBar, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from typing import Dict, Any, List
import time
from datetime import datetime


class MetricCard(QFrame):
    """Individual metric display card"""

    def __init__(self, title: str, value: str = "0", unit: str = "", icon: str = "●", parent=None):
        super().__init__(parent)

        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #3C3F41;
                border: 1px solid #555555;
                border-radius: 8px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #4A88C7;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("color: #4A88C7; font-size: 14px; font-weight: bold;")
        self.icon_label.setFixedWidth(20)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #9E9E9E; font-size: 11px; font-weight: 500;")

        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Value display
        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #BBBBBB; font-size: 18px; font-weight: bold;")

        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("color: #9E9E9E; font-size: 12px;")

        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.unit_label)
        value_layout.addStretch()

        layout.addLayout(header_layout)
        layout.addLayout(value_layout)

    def update_value(self, value: str, color: str = None):
        """Update metric value"""
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(
                f"color: {color}; font-size: 18px; font-weight: bold;"
            )

    def set_icon_color(self, color: str):
        """Set icon color"""
        self.icon_label.setStyleSheet(
            f"color: {color}; font-size: 14px; font-weight: bold;"
        )


class SystemMetricsGroup(QGroupBox):
    """System performance metrics group"""

    def __init__(self, parent=None):
        super().__init__("System Metrics", parent)

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

        layout = QGridLayout(self)
        layout.setSpacing(8)

        # Create metric cards
        self.fps_card = MetricCard("FPS", "0.0", "", "⚡")
        self.frame_skip_card = MetricCard("Frame Skip", "1", "", "⏭")
        self.roi_card = MetricCard("ROI", "OFF", "", "⬛")
        self.lines_card = MetricCard("Lines", "0", "", "📏")

        # Add cards to grid
        layout.addWidget(self.fps_card, 0, 0)
        layout.addWidget(self.frame_skip_card, 0, 1)
        layout.addWidget(self.roi_card, 1, 0)
        layout.addWidget(self.lines_card, 1, 1)

    def update_metrics(self, stats: Dict[str, Any]):
        """Update system metrics"""
        # FPS
        fps = stats.get('fps', 0.0)
        if fps > 25:
            color = "#51cf66"  # Green
        elif fps > 15:
            color = "#FFC66D"  # Yellow
        else:
            color = "#ff6b6b"  # Red
        self.fps_card.update_value(f"{fps:.1f}", color)

        # Frame skip
        frame_skip = stats.get('frame_skip', 1)
        self.frame_skip_card.update_value(f"1/{frame_skip}")

        # ROI status
        roi_enabled = stats.get('roi_enabled', False)
        if roi_enabled:
            self.roi_card.update_value("ON", "#51cf66")
            self.roi_card.set_icon_color("#51cf66")
        else:
            self.roi_card.update_value("OFF", "#9E9E9E")
            self.roi_card.set_icon_color("#9E9E9E")

        # Lines count
        line_count = stats.get('line_count', 0)
        self.lines_card.update_value(str(line_count))
        if line_count > 0:
            self.lines_card.set_icon_color("#4A88C7")
        else:
            self.lines_card.set_icon_color("#9E9E9E")


class VehicleCountsGroup(QGroupBox):
    """Vehicle counting statistics group"""

    def __init__(self, parent=None):
        super().__init__("Vehicle Counts", parent)

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

        # Vehicle type cards
        self.vehicle_cards = {}
        vehicle_types = [
            ("car", "🚗", "Cars"),
            ("motorcycle", "🏍", "Motorcycles"),
            ("bus", "🚌", "Buses"),
            ("truck", "🚛", "Trucks")
        ]

        for vehicle_type, icon, display_name in vehicle_types:
            card_frame = QFrame()
            card_frame.setStyleSheet("""
                QFrame {
                    background-color: #3C3F41;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px;
                }
            """)

            card_layout = QHBoxLayout(card_frame)
            card_layout.setContentsMargins(12, 8, 12, 8)

            # Icon and name
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 16px;")
            icon_label.setFixedWidth(24)

            name_label = QLabel(display_name)
            name_label.setStyleSheet("color: #BBBBBB; font-weight: 500;")

            # Counts
            up_label = QLabel("↑ 0")
            up_label.setStyleSheet("color: #51cf66; font-weight: bold; font-size: 12px;")
            up_label.setMinimumWidth(40)
            up_label.setAlignment(Qt.AlignCenter)

            down_label = QLabel("↓ 0")
            down_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
            down_label.setMinimumWidth(40)
            down_label.setAlignment(Qt.AlignCenter)

            total_label = QLabel("0")
            total_label.setStyleSheet("color: #4A88C7; font-weight: bold; font-size: 14px;")
            total_label.setMinimumWidth(30)
            total_label.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(icon_label)
            card_layout.addWidget(name_label)
            card_layout.addStretch()
            card_layout.addWidget(up_label)
            card_layout.addWidget(down_label)
            card_layout.addWidget(QLabel("|"))
            card_layout.addWidget(total_label)

            self.vehicle_cards[vehicle_type] = {
                'frame': card_frame,
                'up': up_label,
                'down': down_label,
                'total': total_label
            }

            layout.addWidget(card_frame)

        # Total summary
        self.total_frame = QFrame()
        self.total_frame.setStyleSheet("""
            QFrame {
                background-color: #214283;
                border: 1px solid #4A88C7;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        total_layout = QHBoxLayout(self.total_frame)
        total_layout.setContentsMargins(12, 8, 12, 8)

        total_title = QLabel("TOTAL")
        total_title.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        self.total_up_label = QLabel("↑ 0")
        self.total_up_label.setStyleSheet("color: #51cf66; font-weight: bold; font-size: 14px;")

        self.total_down_label = QLabel("↓ 0")
        self.total_down_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px;")

        self.grand_total_label = QLabel("0")
        self.grand_total_label.setStyleSheet("color: white; font-weight: bold; font-size: 18px;")

        total_layout.addWidget(total_title)
        total_layout.addStretch()
        total_layout.addWidget(self.total_up_label)
        total_layout.addWidget(self.total_down_label)
        total_layout.addWidget(QLabel("|"))
        total_layout.addWidget(self.grand_total_label)

        layout.addWidget(self.total_frame)

    def update_counts(self, vehicle_counts: Dict[str, Dict[str, int]]):
        """Update vehicle counts"""
        total_up = 0
        total_down = 0

        for vehicle_type, cards in self.vehicle_cards.items():
            counts = vehicle_counts.get(vehicle_type, {'up': 0, 'down': 0})
            up_count = counts['up']
            down_count = counts['down']
            total_count = up_count + down_count

            cards['up'].setText(f"↑ {up_count}")
            cards['down'].setText(f"↓ {down_count}")
            cards['total'].setText(str(total_count))

            total_up += up_count
            total_down += down_count

        # Update totals
        self.total_up_label.setText(f"↑ {total_up}")
        self.total_down_label.setText(f"↓ {total_down}")
        self.grand_total_label.setText(str(total_up + total_down))


class RecentActivityGroup(QGroupBox):
    """Recent detection activity group"""

    def __init__(self, parent=None):
        super().__init__("Recent Activity", parent)

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

        # Activity table
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(3)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Vehicle", "Direction"])

        # Style the table
        self.activity_table.setStyleSheet("""
            QTableWidget {
                background-color: #3C3F41;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                gridline-color: #555555;
                outline: none;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #555555;
            }
            QTableWidget::item:selected {
                background-color: #214283;
            }
            QHeaderView::section {
                background-color: #4C5052;
                color: #BBBBBB;
                border: 1px solid #555555;
                padding: 8px;
                font-weight: bold;
            }
        """)

        # Configure table
        self.activity_table.setMaximumHeight(200)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.verticalHeader().setVisible(False)
        self.activity_table.horizontalHeader().setStretchLastSection(True)

        # Set column widths
        header = self.activity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        layout.addWidget(self.activity_table)

        # Activity buffer
        self.activity_buffer = []
        self.max_activities = 50

    def add_activity(self, vehicle_type: str, direction: str):
        """Add new activity"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Add to buffer
        self.activity_buffer.append({
            'time': timestamp,
            'vehicle': vehicle_type.capitalize(),
            'direction': '↑ Up' if direction == 'up' else '↓ Down'
        })

        # Keep only recent activities
        if len(self.activity_buffer) > self.max_activities:
            self.activity_buffer.pop(0)

        # Update table
        self._update_table()

    def _update_table(self):
        """Update activity table"""
        self.activity_table.setRowCount(len(self.activity_buffer))

        for row, activity in enumerate(reversed(self.activity_buffer)):
            # Time
            time_item = QTableWidgetItem(activity['time'])
            time_item.setTextAlignment(Qt.AlignCenter)
            self.activity_table.setItem(row, 0, time_item)

            # Vehicle
            vehicle_item = QTableWidgetItem(activity['vehicle'])
            self.activity_table.setItem(row, 1, vehicle_item)

            # Direction
            direction_item = QTableWidgetItem(activity['direction'])
            if 'Up' in activity['direction']:
                direction_item.setForeground(QColor("#51cf66"))
            else:
                direction_item.setForeground(QColor("#ff6b6b"))
            self.activity_table.setItem(row, 2, direction_item)

        # Scroll to top to show latest activity
        self.activity_table.scrollToTop()

    def clear_activities(self):
        """Clear all activities"""
        self.activity_buffer.clear()
        self.activity_table.setRowCount(0)


class StatisticsPanelWidget(QWidget):
    """Main statistics panel widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(350)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
            }
        """)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Main content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel("Statistics")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #BBBBBB;
                padding: 10px 0;
            }
        """)
        layout.addWidget(title_label)

        # Add statistics groups
        self.system_metrics = SystemMetricsGroup()
        self.vehicle_counts = VehicleCountsGroup()
        self.recent_activity = RecentActivityGroup()

        layout.addWidget(self.system_metrics)
        layout.addWidget(self.vehicle_counts)
        layout.addWidget(self.recent_activity)

        # Add stretch
        layout.addStretch()

        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(1000)  # Update every second

        # Track previous counts for activity detection
        self.previous_counts = {}

    def update_statistics(self, stats: Dict[str, Any], vehicle_counts: Dict[str, Dict[str, int]]):
        """Update all statistics"""
        # Update system metrics
        self.system_metrics.update_metrics(stats)

        # Update vehicle counts
        self.vehicle_counts.update_counts(vehicle_counts)

        # Check for new activities
        self._check_for_new_activities(vehicle_counts)

        # Store counts for next comparison
        self.previous_counts = vehicle_counts.copy()

    def _check_for_new_activities(self, current_counts: Dict[str, Dict[str, int]]):
        """Check for new vehicle counting activities"""
        for vehicle_type, counts in current_counts.items():
            prev_counts = self.previous_counts.get(vehicle_type, {'up': 0, 'down': 0})

            # Check for new up counts
            if counts['up'] > prev_counts['up']:
                diff = counts['up'] - prev_counts['up']
                for _ in range(diff):
                    self.recent_activity.add_activity(vehicle_type, 'up')

            # Check for new down counts
            if counts['down'] > prev_counts['down']:
                diff = counts['down'] - prev_counts['down']
                for _ in range(diff):
                    self.recent_activity.add_activity(vehicle_type, 'down')

    def _periodic_update(self):
        """Periodic update for time-sensitive displays"""
        # Could be used for real-time charts or time-based updates
        pass

    def clear_statistics(self):
        """Clear all statistics"""
        # Reset vehicle counts display
        empty_counts = {
            'car': {'up': 0, 'down': 0},
            'motorcycle': {'up': 0, 'down': 0},
            'bus': {'up': 0, 'down': 0},
            'truck': {'up': 0, 'down': 0}
        }
        self.vehicle_counts.update_counts(empty_counts)

        # Clear activities
        self.recent_activity.clear_activities()

        # Reset previous counts
        self.previous_counts = {}