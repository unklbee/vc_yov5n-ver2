"""
src/utils/visualizer.py
Simple visualization utilities for detection results
"""

import cv2
import numpy as np
from typing import List, Dict, Any


class Visualizer:
    """Simple visualization utilities for detection results"""
    
    def __init__(self):
        # Color scheme for different vehicle types
        self.colors = {
            'car': (0, 255, 0),        # Green
            'motorcycle': (255, 255, 0), # Yellow
            'bus': (255, 0, 0),        # Red
            'truck': (0, 0, 255),      # Blue
            'default': (128, 128, 128)  # Gray
        }
        
        # Line colors
        self.roi_color = (0, 255, 0)      # Green
        self.line_color = (0, 255, 255)   # Yellow
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict], detector) -> np.ndarray:
        """Draw all detection results on frame"""
        result_frame = frame.copy()
        
        try:
            # Draw simple vehicle detections
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                class_name = det.get('class_name', 'vehicle')
                track_id = det.get('track_id', -1)
                
                # Get color for vehicle type
                color = self.colors.get(class_name, self.colors['default'])
                
                # Draw bounding box
                cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f"{class_name}"
                if track_id > 0:
                    label += f" #{track_id}"
                
                cv2.putText(result_frame, label, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw simple stats
            fps = getattr(detector, 'get_fps', lambda: 0)()
            cv2.putText(result_frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        except Exception as e:
            print(f"Visualization error: {e}")
        
        return result_frame
