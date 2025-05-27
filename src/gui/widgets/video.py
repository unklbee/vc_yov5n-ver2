
## 2. Video Widget (`src/gui/widgets/video.py`)

"""Simplified video display widget with drawing capabilities"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QButtonGroup, QToolButton
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QColor, QMouseEvent
)
import cv2
import numpy as np
from typing import List, Tuple, Optional


class VideoCanvas(QLabel):
    """Video canvas with drawing capabilities"""

    roi_completed = Signal(list)
    line_completed = Signal(tuple, tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                background-color: #1E1E1E;
                border: 2px solid #555555;
                border-radius: 8px;
                color: white;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("No video loaded")

        # Drawing state
        self.drawing_mode = None  # None, 'roi', 'line'
        self.roi_points = []
        self.line_points = []
        self.current_frame = None
        self.scale_factor = 1.0

        # Enable mouse tracking
        self.setMouseTracking(True)

    def set_drawing_mode(self, mode: Optional[str]):
        """Set drawing mode"""
        self.drawing_mode = mode
        self.roi_points = []
        self.line_points = []

        if mode:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        self.update()

    def update_frame(self, frame: np.ndarray):
        """Update displayed frame"""
        try:
            self.current_frame = frame.copy()

            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            # Create QImage
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

            # Scale to fit widget
            widget_size = self.size()
            if widget_size.width() > 0 and widget_size.height() > 0:
                # Calculate scale factor
                scale_x = widget_size.width() / w
                scale_y = widget_size.height() / h
                self.scale_factor = min(scale_x, scale_y, 1.0)

                # Scale image
                scaled_size = (int(w * self.scale_factor), int(h * self.scale_factor))
                pixmap = QPixmap.fromImage(qt_image).scaled(
                    scaled_size[0], scaled_size[1],
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )

                self.setPixmap(pixmap)

        except Exception as e:
            print(f"Frame update error: {e}")
            self.setText("Frame update error")

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for drawing"""
        if not self.drawing_mode or self.current_frame is None:
            return

        # Convert widget coordinates to image coordinates
        image_point = self._widget_to_image_coords(event.position().toPoint())
        if not image_point:
            return

        if self.drawing_mode == 'roi':
            if event.button() == Qt.LeftButton:
                self.roi_points.append(image_point)
                self.update()
            elif event.button() == Qt.RightButton and len(self.roi_points) >= 3:
                self.roi_completed.emit(self.roi_points.copy())
                self.roi_points = []
                self.drawing_mode = None
                self.setCursor(Qt.ArrowCursor)
                self.update()

        elif self.drawing_mode == 'line':
            if event.button() == Qt.LeftButton:
                self.line_points.append(image_point)
                self.update()

                if len(self.line_points) == 2:
                    self.line_completed.emit(self.line_points[0], self.line_points[1])
                    self.line_points = []
                    self.drawing_mode = None
                    self.setCursor(Qt.ArrowCursor)
                    self.update()

    def _widget_to_image_coords(self, widget_point: QPoint) -> Optional[Tuple[int, int]]:
        """Convert widget coordinates to image coordinates"""
        if self.current_frame is None or self.scale_factor == 0:
            return None

        # Get pixmap rect (centered in widget)
        if not self.pixmap():
            return None

        pixmap_rect = self.pixmap().rect()
        widget_rect = self.rect()

        # Calculate pixmap position (centered)
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

        # Check if point is within pixmap
        pixmap_x = widget_point.x() - x_offset
        pixmap_y = widget_point.y() - y_offset

        if (0 <= pixmap_x < pixmap_rect.width() and
                0 <= pixmap_y < pixmap_rect.height()):

            # Scale to original image coordinates
            image_x = int(pixmap_x / self.scale_factor)
            image_y = int(pixmap_y / self.scale_factor)

            # Ensure coordinates are within bounds
            h, w = self.current_frame.shape[:2]
            image_x = max(0, min(image_x, w - 1))
            image_y = max(0, min(image_y, h - 1))

            return (image_x, image_y)

        return None

    def paintEvent(self, event):
        """Custom paint event for drawing annotations"""
        super().paintEvent(event)

        if not self.drawing_mode or not self.pixmap():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get pixmap position
        pixmap_rect = self.pixmap().rect()
        widget_rect = self.rect()
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

        # Draw ROI points
        if self.drawing_mode == 'roi' and self.roi_points:
            pen = QPen(QColor(0, 255, 0), 3)
            painter.setPen(pen)

            widget_points = []
            for point in self.roi_points:
                widget_x = int(point[0] * self.scale_factor) + x_offset
                widget_y = int(point[1] * self.scale_factor) + y_offset
                widget_points.append(QPoint(widget_x, widget_y))

            # Draw points and lines
            for i, point in enumerate(widget_points):
                painter.drawEllipse(point, 6, 6)
                if i > 0:
                    painter.drawLine(widget_points[i-1], point)

        # Draw line points
        elif self.drawing_mode == 'line' and self.line_points:
            pen = QPen(QColor(255, 255, 0), 3)
            painter.setPen(pen)

            for point in self.line_points:
                widget_x = int(point[0] * self.scale_factor) + x_offset
                widget_y = int(point[1] * self.scale_factor) + y_offset
                painter.drawEllipse(QPoint(widget_x, widget_y), 8, 8)

    def clear_annotations(self):
        """Clear all annotations"""
        self.roi_points = []
        self.line_points = []
        self.drawing_mode = None
        self.setCursor(Qt.ArrowCursor)
        self.update()


class VideoControlBar(QFrame):
    """Control bar for video operations"""

    roi_mode_requested = Signal(bool)
    line_mode_requested = Signal(bool)
    clear_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(50)
        self.setStyleSheet("""
            QFrame {
                background-color: #3C3F41;
                border: 1px solid #555555;
                border-radius: 6px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Drawing mode buttons
        self.button_group = QButtonGroup(self)

        self.roi_button = QToolButton()
        self.roi_button.setText("🔷 ROI")
        self.roi_button.setCheckable(True)
        self.roi_button.setToolTip("Draw Region of Interest")

        self.line_button = QToolButton()
        self.line_button.setText("📏 Line")
        self.line_button.setCheckable(True)
        self.line_button.setToolTip("Draw Counting Line")

        self.button_group.addButton(self.roi_button)
        self.button_group.addButton(self.line_button)
        self.button_group.setExclusive(True)

        # Clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setToolTip("Clear all annotations")

        # Status label
        self.status_label = QLabel("Mode: View")
        self.status_label.setStyleSheet("color: #FFC66D; font-weight: bold;")

        # Layout
        layout.addWidget(QLabel("Drawing:"))
        layout.addWidget(self.roi_button)
        layout.addWidget(self.line_button)
        layout.addWidget(self.clear_button)
        layout.addStretch()
        layout.addWidget(self.status_label)

        # Apply button style
        button_style = """
            QToolButton, QPushButton {
                background-color: #4C5052;
                color: #BBBBBB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QToolButton:hover, QPushButton:hover {
                background-color: #5C6365;
                border-color: #4A88C7;
            }
            QToolButton:checked {
                background-color: #365880;
                color: white;
                border-color: #4A88C7;
            }
        """

        for button in [self.roi_button, self.line_button, self.clear_button]:
            button.setStyleSheet(button_style)

        # Connect signals
        self.roi_button.toggled.connect(self._on_roi_toggled)
        self.line_button.toggled.connect(self._on_line_toggled)
        self.clear_button.clicked.connect(self._on_clear_clicked)

    def _on_roi_toggled(self, checked: bool):
        """Handle ROI button toggle"""
        if checked:
            self.status_label.setText("Mode: Drawing ROI")
            self.roi_mode_requested.emit(True)
        else:
            self.status_label.setText("Mode: View")
            self.roi_mode_requested.emit(False)

    def _on_line_toggled(self, checked: bool):
        """Handle line button toggle"""
        if checked:
            self.status_label.setText("Mode: Drawing Line")
            self.line_mode_requested.emit(True)
        else:
            self.status_label.setText("Mode: View")
            self.line_mode_requested.emit(False)

    def _on_clear_clicked(self):
        """Handle clear button click"""
        # Reset buttons
        self.button_group.setExclusive(False)
        self.roi_button.setChecked(False)
        self.line_button.setChecked(False)
        self.button_group.setExclusive(True)

        self.status_label.setText("Mode: View")
        self.clear_requested.emit()


class VideoWidget(QWidget):
    """Main video display widget"""

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

        # Connect signals
        self.control_bar.roi_mode_requested.connect(self._set_roi_mode)
        self.control_bar.line_mode_requested.connect(self._set_line_mode)
        self.control_bar.clear_requested.connect(self._clear_annotations)

        self.canvas.roi_completed.connect(self._on_roi_completed)
        self.canvas.line_completed.connect(self._on_line_completed)

    def update_frame(self, frame: np.ndarray):
        """Update displayed frame"""
        self.canvas.update_frame(frame)

    def _set_roi_mode(self, enabled: bool):
        """Set ROI drawing mode"""
        self.canvas.set_drawing_mode('roi' if enabled else None)

    def _set_line_mode(self, enabled: bool):
        """Set line drawing mode"""
        self.canvas.set_drawing_mode('line' if enabled else None)

    def _clear_annotations(self):
        """Clear all annotations"""
        self.canvas.clear_annotations()
        self.annotations_cleared.emit()

    def _on_roi_completed(self, points: list):
        """Handle ROI completion"""
        self.roi_drawn.emit(points)
        # Reset control bar
        self.control_bar.roi_button.setChecked(False)
        self.control_bar.status_label.setText("Mode: View")

    def _on_line_completed(self, point1: tuple, point2: tuple):
        """Handle line completion"""
        self.line_drawn.emit(point1, point2)
        # Reset control bar
        self.control_bar.line_button.setChecked(False)
        self.control_bar.status_label.setText("Mode: View")

    def reset_view(self):
        """Reset view"""
        self.canvas.clear_annotations()
        self.control_bar.roi_button.setChecked(False)
        self.control_bar.line_button.setChecked(False)
        self.control_bar.status_label.setText("Mode: View")

    @property
    def current_frame(self):
        """Get current frame"""
        return self.canvas.current_frame