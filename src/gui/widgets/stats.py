"""
Fixed src/gui/widgets/stats.py - Sekarang counting akan tampil di GUI
"""

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
    """Fixed stats widget yang menampilkan counting results"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedWidth(300)
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2B2B;
                color: #BBBBBB;
            }
        """)

        # PERBAIKAN: Tracking counting data dari detector
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
        self.total_crossings = 0

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

        # PERBAIKAN: Counting stats section
        layout.addWidget(self.create_counting_section())

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

    def create_counting_section(self) -> QFrame:
        """PERBAIKAN: Create counting statistics section"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #2B2B2B;
                border: 1px solid #214283;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(section)

        # Section title
        title = QLabel("🚦 Vehicle Counting")
        title.setStyleSheet("color: #4A88C7; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)

        # Counting cards
        cards_layout = QVBoxLayout()
        cards_layout.setSpacing(5)

        self.total_crossings_card = StatCard("Total Crossings", "0")
        self.up_crossings_card = StatCard("↑ Up", "0")
        self.down_crossings_card = StatCard("↓ Down", "0")

        cards_layout.addWidget(self.total_crossings_card)
        cards_layout.addWidget(self.up_crossings_card)
        cards_layout.addWidget(self.down_crossings_card)

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
        title = QLabel("Vehicle Types")
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
        """PERBAIKAN: Update detection statistics dengan counting data"""
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

        # PERBAIKAN: Update counting statistics dari detector stats
        self._update_counting_stats(stats)

        # PERBAIKAN: Update vehicle counts dari detector data
        self._update_vehicle_counts_from_stats(stats)
        self._update_counting_display(stats)

    def _update_counting_display(self, stats: Dict[str, Any]):
        """TAMBAHAN METHOD BARU: Update counting display dari stats"""
        try:
            # Get counting data dari stats
            vehicle_counts = stats.get('vehicle_counts', {})
            total_crossings = stats.get('total_crossings', 0)

            # if total_crossings > 0:
            #     print(f"📊 GUI Update: Total crossings = {total_crossings}")

            # Update vehicle counts jika ada data counting
            if vehicle_counts:
                for vehicle_type, counts in vehicle_counts.items():
                    if vehicle_type in self.vehicle_labels:
                        up_count = counts.get('up', 0)
                        down_count = counts.get('down', 0)
                        total_type = up_count + down_count

                        # Update label
                        label_text = f"↑{up_count} ↓{down_count}"
                        if total_type > 0:
                            label_text += f" ({total_type})"

                        self.vehicle_labels[vehicle_type].setText(label_text)

                        # Highlight if active
                        if total_type > 0:
                            self.vehicle_labels[vehicle_type].setStyleSheet(
                                "color: #4A88C7; font-size: 12px; font-weight: bold;"
                            )

                # Update total count label if exists
                if hasattr(self, 'total_count_label'):
                    self.total_count_label.setText(str(total_crossings))

        except Exception as e:
            print(f"⚠️ Counting display update error: {e}")

    def _update_counting_stats(self, stats: Dict[str, Any]):
        """PERBAIKAN: Update counting stats dari detector results"""
        # Get counting data dari stats
        vehicle_counts = stats.get('vehicle_counts', {})
        total_crossings = stats.get('total_crossings', 0)
        crossing_events = stats.get('crossing_events', [])

        # Update total crossings
        self.total_crossings = total_crossings
        self.total_crossings_card.update_value(str(total_crossings), "#4A88C7")

        # Calculate up/down totals
        total_up = 0
        total_down = 0

        for vehicle_type, counts in vehicle_counts.items():
            total_up += counts.get('up', 0)
            total_down += counts.get('down', 0)

        # Update direction cards
        self.up_crossings_card.update_value(str(total_up), "#51cf66")
        self.down_crossings_card.update_value(str(total_down), "#ff6b6b")

        # Print debug info untuk memastikan data sampai
        # if crossing_events:
        #     print(f"📊 GUI Stats Update: Total={total_crossings}, Up={total_up}, Down={total_down}")

    def _update_vehicle_counts_from_stats(self, stats: Dict[str, Any]):
        """PERBAIKAN: Update vehicle counts dari detector stats, bukan local tracking"""
        # Get vehicle counts dari detector
        vehicle_counts = stats.get('vehicle_counts', {})

        # Update stored vehicle counts
        self.vehicle_counts = vehicle_counts

        # Update labels untuk setiap vehicle type
        for vehicle_type, label in self.vehicle_labels.items():
            if vehicle_type in vehicle_counts:
                up_count = vehicle_counts[vehicle_type].get('up', 0)
                down_count = vehicle_counts[vehicle_type].get('down', 0)
                total_type = up_count + down_count

                # Update label dengan format yang jelas
                label.setText(f"↑{up_count} ↓{down_count} ({total_type})")

                # Color coding berdasarkan activity
                if total_type > 0:
                    label.setStyleSheet("color: #4A88C7; font-size: 12px; font-weight: bold;")
                else:
                    label.setStyleSheet("color: #9E9E9E; font-size: 12px;")
            else:
                label.setText("↑0 ↓0 (0)")
                label.setStyleSheet("color: #9E9E9E; font-size: 12px;")

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
        self.total_crossings = 0

        # Reset counting cards
        self.total_crossings_card.update_value("0", "#9E9E9E")
        self.up_crossings_card.update_value("0", "#9E9E9E")
        self.down_crossings_card.update_value("0", "#9E9E9E")

        # Reset vehicle type labels
        for label in self.vehicle_labels.values():
            label.setText("↑0 ↓0 (0)")
            label.setStyleSheet("color: #9E9E9E; font-size: 12px;")

    def reset(self):
        """Reset all statistics"""
        # Reset performance
        self.fps_card.update_value("0.0")
        self.processing_card.update_value("0")

        # Reset detection
        self.detections_card.update_value("0")
        self.roi_card.update_value("OFF", "#9E9E9E")
        self.lines_card.update_value("0")

        # Reset counting
        self.clear_vehicle_counts()

        # Reset video info
        self.resolution_label.setText("Resolution: N/A")
        self.video_fps_label.setText("Video FPS: N/A")
        self.frame_count_label.setText("Frame: 0")

    def force_update_display(self):
        """Force update display untuk debugging"""
        self.update()
        self.repaint()
        print(f"🔄 GUI Display Force Updated - Total Crossings: {self.total_crossings}")