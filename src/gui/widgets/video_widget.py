"""
src/gui/widgets/video_widget.py
Robust video display widget with comprehensive error handling
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QButtonGroup, QToolButton, QSpacerItem,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QTimer
from PySide6.QtGui import (
    QPixmap, QPainter, QPen, QBrush, QColor, QFont,
    QMouseEvent, QPaintEvent, QResizeEvent, QImage
)
import cv2
import numpy as np
from typing import List, Tuple, Optional
import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.append(src_dir)


class VideoCanvas(QLabel):
    """Custom canvas for video display with robust drawing capabilities"""

    # Signals
    roi_completed = Signal(list)
    line_completed = Signal(tuple, tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup widget
        self.setMinimumSize(640, 480)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border: 2px solid #555555;
                border-radius: 8px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("No video loaded\n\nLoad a video source to begin")

        # Drawing state
        self.drawing_mode = None  # None, 'roi', 'line'
        self.roi_points = []
        self.temp_line_points = []
        self.is_drawing = False

        # Current frame data
        self.current_frame = None
        self.display_pixmap = None
        self.scale_factor = 1.0
        self.frame_size = (640, 480)

        # Drawing colors
        self.roi_color = QColor(76, 175, 80)      # Green
        self.line_color = QColor(255, 193, 7)     # Yellow
        self.point_color = QColor(33, 150, 243)   # Blue

        # Enable mouse tracking
        self.setMouseTracking(True)

        # Error handling
        self.last_error = None

    def set_drawing_mode(self, mode: str):
        """Set drawing mode with validation"""
        try:
            self.drawing_mode = mode
            self.roi_points = []
            self.temp_line_points = []
            self.is_drawing = False

            if mode:
                self.setCursor(Qt.CrossCursor)
                if mode == 'roi':
                    self.setToolTip("ROI Drawing Mode:\nLeft click: Add point\nRight click: Finish ROI")
                elif mode == 'line':
                    self.setToolTip("Line Drawing Mode:\nClick two points to create counting line")
            else:
                self.setCursor(Qt.ArrowCursor)
                self.setToolTip("")

            self.update()

        except Exception as e:
            print(f"Error setting drawing mode: {e}")

    def clear_annotations(self):
        """Clear all annotations safely"""
        try:
            self.roi_points = []
            self.temp_line_points = []
            self.drawing_mode = None
            self.is_drawing = False
            self.setCursor(Qt.ArrowCursor)
            self.setToolTip("")
            self.update()
        except Exception as e:
            print(f"Error clearing annotations: {e}")

    def update_frame(self, frame: np.ndarray):
        """Update displayed frame with error handling"""
        try:
            if frame is None:
                return

            # Validate frame
            if len(frame.shape) != 3 or frame.shape[2] != 3:
                print("Invalid frame format")
                return

            self.current_frame = frame.copy()
            self.frame_size = (frame.shape[1], frame.shape[0])  # (width, height)
            self._convert_and_display_frame()

        except Exception as e:
            print(f"Error updating frame: {e}")
            self.setText(f"Frame update error:\n{str(e)}")

    def _convert_and_display_frame(self):
        """Convert OpenCV frame to QPixmap with comprehensive error handling"""
        try:
            if self.current_frame is None:
                return

            # Convert BGR to RGB safely
            try:
                rgb_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            except cv2.error as e:
                print(f"Color conversion error: {e}")
                return

            # Get widget size
            widget_size = self.size()
            if widget_size.width() <= 0 or widget_size.height() <= 0:
                return

            frame_height, frame_width = rgb_frame.shape[:2]
            if frame_height <= 0 or frame_width <= 0:
                return

            # Calculate scale factor to fit frame in widget
            scale_x = widget_size.width() / frame_width
            scale_y = widget_size.height() / frame_height
            self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't upscale

            # Resize frame
            new_width = max(1, int(frame_width * self.scale_factor))
            new_height = max(1, int(frame_height * self.scale_factor))

            try:
                resized_frame = cv2.resize(rgb_frame, (new_width, new_height),
                                           interpolation=cv2.INTER_LINEAR)
            except cv2.error as e:
                print(f"Resize error: {e}")
                return

            # Convert to QPixmap safely
            try:
                bytes_per_line = 3 * new_width
                q_image = QImage(resized_frame.data, new_width, new_height,
                                 bytes_per_line, QImage.Format_RGB888)
                self.display_pixmap = QPixmap.fromImage(q_image)
                self.setPixmap(self.display_pixmap)
            except Exception as e:
                print(f"QImage conversion error: {e}")
                return

        except Exception as e:
            print(f"Frame conversion error: {e}")
            self.setText(f"Display error:\n{str(e)}")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events with robust error handling"""
        try:
            if event.button() == Qt.LeftButton and self.drawing_mode:
                # Convert widget coordinates to image coordinates
                image_point = self._widget_to_image_coords(event.position().toPoint())
                if image_point:
                    if self.drawing_mode == 'roi':
                        self._handle_roi_click(image_point)
                    elif self.drawing_mode == 'line':
                        self._handle_line_click(image_point)

            elif event.button() == Qt.RightButton and self.drawing_mode == 'roi':
                self._complete_roi()

            super().mousePressEvent(event)

        except Exception as e:
            print(f"Mouse press error: {e}")
            QMessageBox.warning(self, "Drawing Error", f"Error handling mouse click: {str(e)}")

    def _handle_roi_click(self, image_point):
        """Handle ROI point addition with validation"""
        try:
            # Validate point
            x, y = image_point
            if not (0 <= x < self.frame_size[0] and 0 <= y < self.frame_size[1]):
                print("ROI point outside frame bounds")
                return

            self.roi_points.append(image_point)
            self.update()
            print(f"ROI point {len(self.roi_points)}: ({x}, {y})")

            # Auto-complete if too many points
            if len(self.roi_points) > 10:
                self._complete_roi()

        except Exception as e:
            print(f"ROI click error: {e}")

    def _handle_line_click(self, image_point):
        """Handle line point addition with validation"""
        try:
            # Validate point
            x, y = image_point
            if not (0 <= x < self.frame_size[0] and 0 <= y < self.frame_size[1]):
                print("Line point outside frame bounds")
                return

            self.temp_line_points.append(image_point)
            self.update()
            print(f"Line point {len(self.temp_line_points)}: ({x}, {y})")

            if len(self.temp_line_points) == 2:
                # Validate line (points should be different)
                p1, p2 = self.temp_line_points
                if abs(p1[0] - p2[0]) < 5 and abs(p1[1] - p2[1]) < 5:
                    QMessageBox.warning(self, "Invalid Line", "Line points are too close together")
                    self.temp_line_points = []
                    return

                # Line completed
                self.line_completed.emit(self.temp_line_points[0], self.temp_line_points[1])
                self.temp_line_points = []
                self.drawing_mode = None
                self.setCursor(Qt.ArrowCursor)
                self.setToolTip("")
                print("✅ Line completed")

        except Exception as e:
            print(f"Line click error: {e}")

    def _complete_roi(self):
        """Complete ROI with validation"""
        try:
            if len(self.roi_points) < 3:
                QMessageBox.warning(self, "Invalid ROI", "ROI needs at least 3 points")
                return

            # Validate ROI points form a valid polygon
            if self._validate_roi_polygon():
                self.roi_completed.emit(self.roi_points.copy())
                self.roi_points = []
                self.drawing_mode = None
                self.setCursor(Qt.ArrowCursor)
                self.setToolTip("")
                print("✅ ROI completed")
            else:
                QMessageBox.warning(self, "Invalid ROI", "ROI points do not form a valid polygon")

        except Exception as e:
            print(f"ROI completion error: {e}")
            QMessageBox.warning(self, "ROI Error", f"Error completing ROI: {str(e)}")

    def _validate_roi_polygon(self):
        """Validate that ROI points form a valid polygon"""
        try:
            if len(self.roi_points) < 3:
                return False

            # Check for duplicate points
            unique_points = []
            for point in self.roi_points:
                if not any(abs(point[0] - p[0]) < 5 and abs(point[1] - p[1]) < 5 for p in unique_points):
                    unique_points.append(point)

            if len(unique_points) < 3:
                return False

            # Update roi_points with unique points
            self.roi_points = unique_points
            return True

        except Exception as e:
            print(f"ROI validation error: {e}")
            return False

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events for live feedback"""
        try:
            if self.drawing_mode:
                self.update()  # Trigger repaint for live drawing feedback
            super().mouseMoveEvent(event)
        except Exception as e:
            print(f"Mouse move error: {e}")

    def paintEvent(self, event: QPaintEvent):
        """Custom paint event to draw annotations safely"""
        try:
            super().paintEvent(event)

            if not self.display_pixmap or not self.drawing_mode:
                return

            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Calculate pixmap position (centered)
            pixmap_rect = self.display_pixmap.rect()
            widget_rect = self.rect()

            x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
            y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

            # Draw ROI points and lines
            if self.drawing_mode == 'roi' and self.roi_points:
                self._draw_roi_annotations(painter, x_offset, y_offset)

            # Draw line points
            if self.drawing_mode == 'line' and self.temp_line_points:
                self._draw_line_annotations(painter, x_offset, y_offset)

        except Exception as e:
            print(f"Paint event error: {e}")

    def _draw_roi_annotations(self, painter: QPainter, x_offset: int, y_offset: int):
        """Draw ROI annotations safely"""
        try:
            if not self.roi_points:
                return

            # Set pen for ROI
            pen = QPen(self.roi_color, 3)
            painter.setPen(pen)

            # Convert image coordinates to widget coordinates
            widget_points = []
            for point in self.roi_points:
                widget_point = self._image_to_widget_coords(point, x_offset, y_offset)
                if widget_point:
                    widget_points.append(widget_point)

            if not widget_points:
                return

            # Draw points
            for point in widget_points:
                painter.drawEllipse(point, 6, 6)

            # Draw lines between points
            for i in range(1, len(widget_points)):
                painter.drawLine(widget_points[i-1], widget_points[i])

            # Draw closing line if we have enough points
            if len(widget_points) > 2:
                pen.setStyle(Qt.DashLine)
                painter.setPen(pen)
                painter.drawLine(widget_points[-1], widget_points[0])
                pen.setStyle(Qt.SolidLine)
                painter.setPen(pen)

            # Draw line from last point to mouse cursor for live feedback
            if len(widget_points) > 0:
                try:
                    mouse_pos = self.mapFromGlobal(self.cursor().pos())
                    if self.rect().contains(mouse_pos):
                        pen.setStyle(Qt.DashLine)
                        pen.setColor(self.roi_color.lighter())
                        painter.setPen(pen)
                        painter.drawLine(widget_points[-1], mouse_pos)
                except Exception:
                    pass  # Ignore cursor tracking errors

        except Exception as e:
            print(f"ROI drawing error: {e}")

    def _draw_line_annotations(self, painter: QPainter, x_offset: int, y_offset: int):
        """Draw line annotations safely"""
        try:
            if not self.temp_line_points:
                return

            # Set pen for line
            pen = QPen(self.line_color, 4)
            painter.setPen(pen)

            # Draw first point
            first_point = self._image_to_widget_coords(self.temp_line_points[0], x_offset, y_offset)
            if first_point:
                painter.drawEllipse(first_point, 8, 8)

                # If drawing second point, show live line
                if len(self.temp_line_points) == 1:
                    try:
                        mouse_pos = self.mapFromGlobal(self.cursor().pos())
                        if self.rect().contains(mouse_pos):
                            pen.setStyle(Qt.DashLine)
                            pen.setColor(self.line_color.lighter())
                            painter.setPen(pen)
                            painter.drawLine(first_point, mouse_pos)
                    except Exception:
                        pass  # Ignore cursor tracking errors

        except Exception as e:
            print(f"Line drawing error: {e}")

    def _widget_to_image_coords(self, widget_point: QPoint) -> Optional[Tuple[int, int]]:
        """Convert widget coordinates to image coordinates safely"""
        try:
            if not self.display_pixmap or self.scale_factor == 0:
                return None

            # Calculate pixmap position
            pixmap_rect = self.display_pixmap.rect()
            widget_rect = self.rect()

            x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
            y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

            # Check if point is within pixmap area
            pixmap_x = widget_point.x() - x_offset
            pixmap_y = widget_point.y() - y_offset

            if 0 <= pixmap_x < pixmap_rect.width() and 0 <= pixmap_y < pixmap_rect.height():
                # Scale to original image coordinates
                image_x = int(pixmap_x / self.scale_factor)
                image_y = int(pixmap_y / self.scale_factor)

                # Ensure coordinates are within frame bounds
                image_x = max(0, min(image_x, self.frame_size[0] - 1))
                image_y = max(0, min(image_y, self.frame_size[1] - 1))

                return (image_x, image_y)

            return None

        except Exception as e:
            print(f"Coordinate conversion error: {e}")
            return None

    def _image_to_widget_coords(self, image_point: Tuple[int, int], x_offset: int, y_offset: int) -> Optional[QPoint]:
        """Convert image coordinates to widget coordinates safely"""
        try:
            if self.scale_factor == 0:
                return None

            # Scale to display coordinates
            display_x = int(image_point[0] * self.scale_factor)
            display_y = int(image_point[1] * self.scale_factor)

            # Add offset
            widget_x = display_x + x_offset
            widget_y = display_y + y_offset

            return QPoint(widget_x, widget_y)

        except Exception as e:
            print(f"Widget coordinate conversion error: {e}")
            return None


class VideoControlBar(QFrame):
    """Control bar for video operations with error handling"""

    # Signals
    roi_mode_toggled = Signal(bool)
    line_mode_toggled = Signal(bool)
    annotations_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: #3C3F41;
                border-bottom: 1px solid #555555;
                border-radius: 8px;
                margin: 2px;
            }
        """)

        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(12)

        # Drawing mode buttons
        self.drawing_group = QButtonGroup(self)

        self.roi_button = QToolButton()
        self.roi_button.setText("🔷 Draw ROI")
        self.roi_button.setCheckable(True)
        self.roi_button.setToolTip("Draw Region of Interest\n• Left click: Add point\n• Right click: Finish ROI\n• Minimum 3 points required")
        self.roi_button.setStyleSheet(self._get_tool_button_style())

        self.line_button = QToolButton()
        self.line_button.setText("📏 Draw Line")
        self.line_button.setCheckable(True)
        self.line_button.setToolTip("Draw counting line\n• Click two points to create line\n• Used for vehicle counting")
        self.line_button.setStyleSheet(self._get_tool_button_style())

        self.drawing_group.addButton(self.roi_button, 1)
        self.drawing_group.addButton(self.line_button, 2)
        self.drawing_group.setExclusive(True)

        # Clear button
        self.clear_button = QToolButton()
        self.clear_button.setText("🗑️ Clear All")
        self.clear_button.setToolTip("Clear all annotations (ROI and lines)")
        self.clear_button.setStyleSheet(self._get_tool_button_style("error"))

        # Mode indicator
        self.mode_label = QLabel("🔍 Mode: View")
        self.mode_label.setStyleSheet("""
            QLabel {
                color: #FFC66D;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 12px;
                background-color: #2B2B2B;
                border-radius: 6px;
                border: 1px solid #555555;
            }
        """)

        # Add widgets to layout
        tools_label = QLabel("Drawing Tools:")
        tools_label.setStyleSheet("color: #BBBBBB; font-weight: 500;")

        layout.addWidget(tools_label)
        layout.addWidget(self.roi_button)
        layout.addWidget(self.line_button)
        layout.addWidget(self.clear_button)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding))
        layout.addWidget(self.mode_label)

        # Connect signals with error handling
        try:
            self.roi_button.toggled.connect(self._on_roi_toggled)
            self.line_button.toggled.connect(self._on_line_toggled)
            self.clear_button.clicked.connect(self._on_clear_clicked)
        except Exception as e:
            print(f"Signal connection error: {e}")

    def _get_tool_button_style(self, button_type: str = "default") -> str:
        """Get tool button stylesheet"""
        if button_type == "error":
            return """
                QToolButton {
                    background-color: #C75450;
                    color: white;
                    border: 1px solid #C75450;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QToolButton:hover {
                    background-color: #D64545;
                    transform: translateY(-1px);
                }
                QToolButton:pressed {
                    background-color: #B94A47;
                    transform: translateY(0px);
                }
            """
        else:
            return """
                QToolButton {
                    background-color: #4C5052;
                    color: #BBBBBB;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QToolButton:hover {
                    background-color: #5C6365;
                    border-color: #4A88C7;
                    transform: translateY(-1px);
                }
                QToolButton:checked {
                    background-color: #365880;
                    color: white;
                    border-color: #4A88C7;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                }
                QToolButton:pressed {
                    background-color: #214283;
                    transform: translateY(0px);
                }
            """

    def _on_roi_toggled(self, checked: bool):
        """Handle ROI button toggle with error handling"""
        try:
            if checked:
                self.mode_label.setText("🔷 Mode: Drawing ROI")
                self.mode_label.setStyleSheet(self.mode_label.styleSheet() + "color: #51cf66;")
                self.roi_mode_toggled.emit(True)
            else:
                self.mode_label.setText("🔍 Mode: View")
                self.mode_label.setStyleSheet(self.mode_label.styleSheet().replace("color: #51cf66;", "color: #FFC66D;"))
                self.roi_mode_toggled.emit(False)
        except Exception as e:
            print(f"ROI toggle error: {e}")

    def _on_line_toggled(self, checked: bool):
        """Handle line button toggle with error handling"""
        try:
            if checked:
                self.mode_label.setText("📏 Mode: Drawing Line")
                self.mode_label.setStyleSheet(self.mode_label.styleSheet() + "color: #FFC66D;")
                self.line_mode_toggled.emit(True)
            else:
                self.mode_label.setText("🔍 Mode: View")
                self.mode_label.setStyleSheet(self.mode_label.styleSheet().replace("color: #FFC66D;", "color: #FFC66D;"))
                self.line_mode_toggled.emit(False)
        except Exception as e:
            print(f"Line toggle error: {e}")

    def _on_clear_clicked(self):
        """Handle clear button click with confirmation"""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Clear Annotations",
                "Are you sure you want to clear all ROI and counting lines?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.drawing_group.setExclusive(False)
                self.roi_button.setChecked(False)
                self.line_button.setChecked(False)
                self.drawing_group.setExclusive(True)
                self.mode_label.setText("🔍 Mode: View")
                self.annotations_cleared.emit()

        except Exception as e:
            print(f"Clear clicked error: {e}")

    def reset_mode(self):
        """Reset to view mode safely"""
        try:
            self.drawing_group.setExclusive(False)
            self.roi_button.setChecked(False)
            self.line_button.setChecked(False)
            self.drawing_group.setExclusive(True)
            self.mode_label.setText("🔍 Mode: View")
        except Exception as e:
            print(f"Reset mode error: {e}")


class VideoDisplayWidget(QWidget):
    """Main video display widget with comprehensive error handling"""

    # Signals
    roi_drawn = Signal(list)
    line_drawn = Signal(tuple, tuple)
    annotations_cleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Control bar
        self.control_bar = VideoControlBar()
        layout.addWidget(self.control_bar)

        # Video canvas
        self.canvas = VideoCanvas()
        layout.addWidget(self.canvas)

        # Connect signals with error handling
        try:
            self.control_bar.roi_mode_toggled.connect(self._on_roi_mode_toggled)
            self.control_bar.line_mode_toggled.connect(self._on_line_mode_toggled)
            self.control_bar.annotations_cleared.connect(self._on_annotations_cleared)

            self.canvas.roi_completed.connect(self._on_roi_completed)
            self.canvas.line_completed.connect(self._on_line_completed)
        except Exception as e:
            print(f"Video widget signal connection error: {e}")

    def update_frame(self, frame: np.ndarray):
        """Update displayed frame with error handling"""
        try:
            self.canvas.update_frame(frame)
        except Exception as e:
            print(f"Frame update error: {e}")

    def draw_detections(self, frame: np.ndarray, detections: list, detector) -> np.ndarray:
        """Draw detection results on frame with robust error handling"""
        try:
            # Try to import and use visualizer
            from utils.visualizer import Visualizer
            visualizer = Visualizer()
            return visualizer.draw_detections(frame, detections, detector)
        except ImportError:
            # Fallback: simple drawing
            return self._simple_draw_detections(frame, detections, detector)
        except Exception as e:
            print(f"Detection drawing error: {e}")
            return frame

    def _simple_draw_detections(self, frame: np.ndarray, detections: list, detector) -> np.ndarray:
        """Simple fallback detection drawing"""
        try:
            result_frame = frame.copy()

            # Draw simple bounding boxes
            for det in detections:
                try:
                    x1, y1, x2, y2 = det['bbox']
                    class_name = det.get('class_name', 'vehicle')
                    track_id = det.get('track_id', -1)

                    # Color based on vehicle type
                    colors = {
                        'car': (0, 255, 0),
                        'motorcycle': (255, 255, 0),
                        'bus': (255, 0, 0),
                        'truck': (0, 0, 255)
                    }
                    color = colors.get(class_name, (128, 128, 128))

                    # Validate coordinates
                    h, w = result_frame.shape[:2]
                    x1 = max(0, min(x1, w-1))
                    y1 = max(0, min(y1, h-1))
                    x2 = max(0, min(x2, w-1))
                    y2 = max(0, min(y2, h-1))

                    # Draw box
                    cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)

                    # Draw label
                    label = f"{class_name}"
                    if track_id > 0:
                        label += f" #{track_id}"

                    cv2.putText(result_frame, label, (x1, max(y1-10, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                except Exception as e:
                    print(f"Detection drawing error for single detection: {e}")
                    continue

            return result_frame

        except Exception as e:
            print(f"Simple detection drawing error: {e}")
            return frame

    def clear_display(self):
        """Clear video display safely"""
        try:
            self.canvas.clear()
            self.canvas.setText("No video loaded\n\nLoad a video source to begin")
            self._reset_controls()
        except Exception as e:
            print(f"Clear display error: {e}")

    def _on_roi_mode_toggled(self, enabled: bool):
        """Handle ROI mode toggle with error handling"""
        try:
            if enabled:
                self.canvas.set_drawing_mode('roi')
            else:
                self.canvas.set_drawing_mode(None)
        except Exception as e:
            print(f"ROI mode toggle error: {e}")

    def _on_line_mode_toggled(self, enabled: bool):
        """Handle line mode toggle with error handling"""
        try:
            if enabled:
                self.canvas.set_drawing_mode('line')
            else:
                self.canvas.set_drawing_mode(None)
        except Exception as e:
            print(f"Line mode toggle error: {e}")

    def _on_annotations_cleared(self):
        """Handle annotations clear with error handling"""
        try:
            self.canvas.clear_annotations()
            self.annotations_cleared.emit()
        except Exception as e:
            print(f"Annotations clear error: {e}")

    def _on_roi_completed(self, points: list):
        """Handle ROI completion with error handling"""
        try:
            self.control_bar.reset_mode()
            self.roi_drawn.emit(points)
            QMessageBox.information(self, "ROI Created", f"ROI successfully created with {len(points)} points")
        except Exception as e:
            print(f"ROI completion error: {e}")

    def _on_line_completed(self, point1: tuple, point2: tuple):
        """Handle line completion with error handling"""
        try:
            self.control_bar.reset_mode()
            self.line_drawn.emit(point1, point2)
            QMessageBox.information(self, "Line Created", "Counting line successfully created")
        except Exception as e:
            print(f"Line completion error: {e}")

    def _reset_controls(self):
        """Reset control states safely"""
        try:
            self.control_bar.reset_mode()
            self.canvas.clear_annotations()
        except Exception as e:
            print(f"Reset controls error: {e}")