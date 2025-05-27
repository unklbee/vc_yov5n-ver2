"""
src/core/tracker.py - Simple tracker implementation
"""

import numpy as np
from collections import deque, defaultdict
from typing import List, Dict, Tuple


class DeepSORTTracker:
    """Simple tracker implementation"""
    
    def __init__(self, max_age: int = 1, min_hits: int = 3, iou_threshold: float = 0.3):
        self.tracks = {}
        self.next_id = 1
        self.track_trails = defaultdict(lambda: deque(maxlen=30))
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.last_detections = []
    
    def update(self, detections: List[Dict]) -> List[Dict]:
        """Simple update - just add track IDs"""
        try:
            tracked_detections = []
            for i, det in enumerate(detections):
                det['track_id'] = i + 1
                tracked_detections.append(det)
                
                # Update trail
                center = self._get_center(det['bbox'])
                self.track_trails[i + 1].append(center)
            
            self.last_detections = tracked_detections
            return tracked_detections
        except Exception as e:
            print(f"Tracker error: {e}")
            return detections
    
    def _get_center(self, bbox: List[int]) -> Tuple[int, int]:
        """Get center point of bbox"""
        return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
    
    def get_last_detections(self) -> List[Dict]:
        """Get last detections"""
        return self.last_detections
    
    def reset(self):
        """Reset tracker state"""
        self.tracks = {}
        self.next_id = 1
        self.track_trails = defaultdict(lambda: deque(maxlen=30))
        self.last_detections = []
