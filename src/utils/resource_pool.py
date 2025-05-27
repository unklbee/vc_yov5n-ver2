## 3. Resource Pool (`src/utils/resource_pool.py`)

"""
Resource pooling for better memory management
"""
import numpy as np
from collections import deque
from typing import Deque, Tuple, Optional, Dict
import threading

class FramePool:
    """Pool of reusable frame buffers"""

    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.available_frames: Deque[np.ndarray] = deque()
        self.lock = threading.Lock()

    def get_frame(self, shape: Tuple[int, ...], dtype=np.uint8) -> np.ndarray:
        """Get a frame buffer from pool or create new"""
        with self.lock:
            # Try to reuse existing frame
            for i, frame in enumerate(self.available_frames):
                if frame.shape == shape and frame.dtype == dtype:
                    return self.available_frames.popleft()

            # Create new frame if none suitable found
            return np.zeros(shape, dtype=dtype)

    def return_frame(self, frame: np.ndarray):
        """Return frame buffer to pool"""
        with self.lock:
            if len(self.available_frames) < self.max_size:
                # Clear frame data for reuse
                frame.fill(0)
                self.available_frames.append(frame)

    def clear(self):
        """Clear all pooled frames"""
        with self.lock:
            self.available_frames.clear()

class DetectionPool:
    """Pool for detection result objects"""

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.available_detections: Deque[Dict] = deque()
        self.lock = threading.Lock()

    def get_detection(self) -> Dict:
        """Get a detection object from pool"""
        with self.lock:
            if self.available_detections:
                detection = self.available_detections.popleft()
                # Clear previous data
                detection.clear()
                return detection
            else:
                return {}

    def return_detection(self, detection: Dict):
        """Return detection object to pool"""
        with self.lock:
            if len(self.available_detections) < self.max_size:
                self.available_detections.append(detection)

# Global resource pools
frame_pool = FramePool()
detection_pool = DetectionPool()