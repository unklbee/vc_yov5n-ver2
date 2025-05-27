## Statistics Widget (`src/gui/widgets/stats.py`)

"""Simplified statistics widget"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea,
    QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt
from typing import Dict, List, Any
from collections import defaultdict


class StatCard(QFrame):
    """Individual statistic card"""

    def __init__(self, title: str, value: str = "0", unit: str = "", parent=None):
        super().__init__(parent)

        self.setFixedHeight(70)
        self.setStyleSheet("""
            QFrame {
                background-color: #3C3F41;
                border: 1px solid #555555;
                border-radius: 6px;
                margin: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #9E9E9E; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.title_label)

        # Value
        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #BBBBBB; font-size: 16px; font-weight: bold;")

        self.unit_label = QLabel(unit)
        self.unit_label.setStyleSheet("color: #9E9E9E; font-size: 12px;")

        value_layout.addWidget(self.value_label)
        if unit:
            value_layout.addWidget(self.unit_label)
        value_layout.addStretch()

        layout.addLayout(value_layout)

    def update_value(self, value: str, color: str = None):
        """Update card value"""
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")


class StatsWidget(QWidget):
    """Main statistics widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        # Vehicle counts tracking
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

        self.setup_ui()

    def setup_ui(self):
        """Setup UI components"""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        # Content widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Statistics")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(title)

        # Performance stats
        layout.addWidget(self.create_performance_section())

        # Detection stats
        layout.addWidget(self.create_detection_section())

        # Vehicle counts
        layout.addWidget(self.create_vehicle_counts_section())

        # Video info
        layout.addWidget(self.create_video_info_section())

        layout.addStretch()

        # Set content to scroll area
        scroll.setWidget(content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def create_performance_section(self) -> QFrame:
        """Create performance statistics section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Performance")
        title.setStyleSheet("color: #FFC66D; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Performance cards
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(5)

        self.fps_card = StatCard("FPS", "0.0")
        self.processing_card = StatCard("Processing", "0", "ms")

        cards_layout.addWidget(self.fps_card)
        cards_layout.addWidget(self.processing_card)

        layout.addLayout(cards_layout)

        return section

    def create_detection_section(self) -> QFrame:
        """Create detection statistics section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Detection")
        title.setStyleSheet("color: #FFC66D; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Detection cards
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(5)

        self.detections_card = StatCard("Current Detections", "0")
        self.roi_card = StatCard("ROI Status", "OFF")
        self.lines_card = StatCard("Counting Lines", "0")

        cards_layout.addWidget(self.detections_card)
        cards_layout.addWidget(self.roi_card)
        cards_layout.addWidget(self.lines_card)

        layout.addLayout(cards_layout)

        return section

    def create_vehicle_counts_section(self) -> QFrame:
        """Create vehicle counts section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Vehicle Counts")
        title.setStyleSheet("color: #FFC66D; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Vehicle count labels
        self.vehicle_labels = {}
        vehicle_types = ['car', 'motorcycle', 'bus', 'truck']

        for vehicle_type in vehicle_types:
            vehicle_frame = QFrame()
            vehicle_frame.setStyleSheet("""
                QFrame {
                    background-color: #3C3F41;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 2px 0;
                }
            """)

            vehicle_layout = QHBoxLayout(vehicle_frame)
            vehicle_layout.setContentsMargins(8, 4, 8, 4)

            # Vehicle name
            name_label = QLabel(vehicle_type.capitalize())
            name_label.setStyleSheet("color: #BBBBBB; font-weight: 500;")

            # Counts
            count_label = QLabel("↑0 ↓0")
            count_label.setStyleSheet("color: #9E9E9E; font-size: 12px;")
            count_label.setAlignment(Qt.AlignRight)

            vehicle_layout.addWidget(name_label)
            vehicle_layout.addStretch()
            vehicle_layout.addWidget(count_label)

            self.vehicle_labels[vehicle_type] = count_label
            layout.addWidget(vehicle_frame)

        # Total count
        self.total_frame = QFrame()
        self.total_frame.setStyleSheet("""
            QFrame {
                background-color: #214283;
                border: 1px solid #4A88C7;
                border-radius: 4px;
                padding: 8px;
                margin: 5px 0;
            }
        """)

        total_layout = QHBoxLayout(self.total_frame)
        total_layout.setContentsMargins(8, 4, 8, 4)

        total_title = QLabel("TOTAL")
        total_title.setStyleSheet("color: white; font-weight: bold;")

        self.total_count_label = QLabel("0")
        self.total_count_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        self.total_count_label.setAlignment(Qt.AlignRight)

        total_layout.addWidget(total_title)
        total_layout.addStretch()
        total_layout.addWidget(self.total_count_label)

        layout.addWidget(self.total_frame)

        return section

    def create_video_info_section(self) -> QFrame:
        """Create video information section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("Video Info")
        title.setStyleSheet("color: #FFC66D; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Video info labels
        self.resolution_label = QLabel("Resolution: N/A")
        self.resolution_label.setStyleSheet("color: #9E9E9E; font-size: 12px; margin: 2px 0;")

        self.video_fps_label = QLabel("Video FPS: N/A")
        self.video_fps_label.setStyleSheet("color: #9E9E9E; font-size: 12px; margin: 2px 0;")

        self.frame_count_label = QLabel("Frame: 0")
        self.frame_count_label.setStyleSheet("color: #9E9E9E; font-size: 12px; margin: 2px 0;")

        layout.addWidget(self.resolution_label)
        layout.addWidget(self.video_fps_label)
        layout.addWidget(self.frame_count_label)

        return section

    def update_detection_stats(self, stats: Dict[str, Any], detections: List[Dict]):
        """Update detection statistics"""
        # Update performance
        fps = stats.get('fps', 0)
        processing_time = stats.get('processing_time', 0) * 1000  # Convert to ms

        # Color code FPS
        if fps > 25:
            fps_color = "#51cf66"  # Green
        elif fps > 15:
            fps_color = "#FFC66D"  # Yellow
        else:
            fps_color = "#ff6b6b"  # Red

        self.fps_card.update_value(f"{fps:.1f}", fps_color)
        self.processing_card.update_value(f"{processing_time:.1f}")

        # Update detection info
        detection_count = len(detections)
        self.detections_card.update_value(str(detection_count))

        # Update ROI status
        roi_enabled = stats.get('roi_enabled', False)
        if roi_enabled:
            self.roi_card.update_value("ON", "#51cf66")
        else:
            self.roi_card.update_value("OFF", "#9E9E9E")

        # Update line count
        line_count = stats.get('line_count', 0)
        self.lines_card.update_value(str(line_count))

        # Update vehicle counts (simplified - would need actual counting logic)
        self._update_vehicle_counts(detections)

    def _update_vehicle_counts(self, detections: List[Dict]):
        """Update vehicle counts display"""
        # Count current detections by type
        current_counts = defaultdict(int)
        for detection in detections:
            vehicle_type = detection.get('class_name', 'unknown')
            if vehicle_type in self.vehicle_labels:
                current_counts[vehicle_type] += 1

        # Update labels
        total = 0
        for vehicle_type, label in self.vehicle_labels.items():
            up_count = self.vehicle_counts[vehicle_type]['up']
            down_count = self.vehicle_counts[vehicle_type]['down']
            current = current_counts[vehicle_type]

            label.setText(f"↑{up_count} ↓{down_count} ({current})")
            total += up_count + down_count

        self.total_count_label.setText(str(total))

    def update_video_info(self, properties: Dict[str, Any]):
        """Update video information"""
        width = properties.get('width', 0)
        height = properties.get('height', 0)
        fps = properties.get('fps', 0)
        frame_count = properties.get('frame_count', 0)

        self.resolution_label.setText(f"Resolution: {width}×{height}")
        self.video_fps_label.setText(f"Video FPS: {fps:.1f}")

        if frame_count > 0:
            self.frame_count_label.setText(f"Total Frames: {frame_count}")
        else:
            self.frame_count_label.setText("Frame: Live")

    def clear_vehicle_counts(self):
        """Clear vehicle counts"""
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

        for label in self.vehicle_labels.values():
            label.setText("↑0 ↓0 (0)")

        self.total_count_label.setText("0")

    def reset(self):
        """Reset all statistics"""
        # Reset performance
        self.fps_card.update_value("0.0")
        self.processing_card.update_value("0")

        # Reset detection
        self.detections_card.update_value("0")
        self.roi_card.update_value("OFF", "#9E9E9E")
        self.lines_card.update_value("0")

        # Reset counts
        self.clear_vehicle_counts()

        # Reset video info
        self.resolution_label.setText("Resolution: N/A")
        self.video_fps_label.setText("Video FPS: N/A")
        self.frame_count_label.setText("Frame: 0")