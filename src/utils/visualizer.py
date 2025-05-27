"""
Complete src/utils/visualizer.py - Visualization Utils
"""

import cv2
import numpy as np
from typing import List, Dict, Any

class Visualizer:
    """Lightweight visualization for detection results"""

    # Color scheme
    COLORS = {
        'car': (0, 255, 0),
        'motorcycle': (255, 255, 0),
        'bus': (255, 0, 0),
        'truck': (0, 0, 255),
        'default': (128, 128, 128)
    }

    @classmethod
    def draw_detections(cls, frame: np.ndarray, detections: List[Dict],
                        stats: Dict[str, Any]) -> np.ndarray:
        """Draw detection results on frame"""
        result_frame = frame.copy()

        # Draw detections
        for detection in detections:
            cls._draw_detection(result_frame, detection)

        # Draw stats overlay
        cls._draw_stats_overlay(result_frame, stats, len(detections))

        return result_frame

    @classmethod
    def _draw_detection(cls, frame: np.ndarray, detection: Dict):
        """Draw single detection"""
        bbox = detection['bbox']
        class_name = detection['class_name']
        confidence = detection['confidence']
        track_id = detection.get('track_id', -1)

        x1, y1, x2, y2 = bbox
        color = cls.COLORS.get(class_name, cls.COLORS['default'])

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Draw label
        label = f"{class_name}"
        if track_id > 0:
            label += f" #{track_id}"
        label += f" {confidence:.2f}"

        # Label background
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                      (x1 + label_size[0], y1), color, -1)

        # Label text
        cv2.putText(frame, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    @classmethod
    def _draw_stats_overlay(cls, frame: np.ndarray, stats: Dict[str, Any],
                            detection_count: int):
        """Draw statistics overlay"""
        h, w = frame.shape[:2]

        # Stats background
        cv2.rectangle(frame, (10, 10), (250, 120), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (250, 120), (0, 255, 0), 2)

        # Stats text
        fps = stats.get('fps', 0)
        proc_time = stats.get('processing_time', 0) * 1000  # Convert to ms
        total_crossings = stats.get('total_crossings', 0)

        stats_lines = [
            f"FPS: {fps:.1f}",
            f"Processing: {proc_time:.1f}ms",
            f"Detections: {detection_count}",
            f"Crossings: {total_crossings}",
            f"ROI: {'ON' if stats.get('roi_enabled', False) else 'OFF'}"
        ]

        for i, line in enumerate(stats_lines):
            y_pos = 30 + i * 18
            cv2.putText(frame, line, (15, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)