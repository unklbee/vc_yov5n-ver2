"""
src/core/detector.py
Fixed core vehicle detection module with robust ROI handling
"""

import cv2
import numpy as np
import time
import os
from collections import deque, defaultdict
from typing import List, Dict, Tuple, Optional
import math

# Check OpenVINO installation
try:
    import openvino as ov
    OPENVINO_VERSION = "2022+"
except ImportError:
    try:
        from openvino.inference_engine import IECore
        OPENVINO_VERSION = "legacy"
    except ImportError:
        raise ImportError("OpenVINO not installed. Install with: pip install openvino")

# Import other modules with error handling
try:
    from .tracker import DeepSORTTracker
    from .line_counter import LineCounter
except ImportError:
    # Fallback imports
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)

    try:
        from core.tracker import DeepSORTTracker
        from core.line_counter import LineCounter
    except ImportError:
        # Create minimal fallback classes
        class DeepSORTTracker:
            def __init__(self):
                self.track_trails = defaultdict(lambda: deque(maxlen=30))
            def update(self, detections): return detections
            def get_last_detections(self): return []

        class LineCounter:
            def __init__(self, line_id, point1, point2):
                self.line_id = line_id
                self.point1 = point1
                self.point2 = point2
            def update(self, detections): return []
            def get_statistics(self): return {'line_id': self.line_id, 'crossings': {'up': 0, 'down': 0}}
            def reset_counts(self): pass


class OptimizedVehicleDetector:
    """
    Vehicle detection system with robust ROI, Deep SORT tracking, and line counting
    """

    def __init__(self, model_path: str, device: str = "CPU", config: Optional[Dict] = None):
        self.device = device
        self.model_path = model_path

        # Apply configuration
        if config:
            self.apply_config(config)
        else:
            self._set_defaults()

        # Initialize OpenVINO
        if OPENVINO_VERSION == "2022+":
            self.core = ov.Core()
        else:
            self.core = IECore()

        # Load model
        self.compiled_model = self._load_model()

        # Vehicle classes
        self.vehicle_classes = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

        # Deep SORT tracker
        self.tracker = DeepSORTTracker()

        # Performance monitoring
        self.fps_history = deque(maxlen=30)
        self.last_time = time.time()

        # ROI settings with robust handling
        self.roi_points = []
        self.roi_mask = None
        self.use_roi = False
        self.roi_valid = False

        # Line counter settings
        self.counting_lines = []
        self.line_counters = []
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

        # Drawing states
        self.drawing_roi = False
        self.drawing_line = False
        self.temp_line_points = []

    def _set_defaults(self):
        """Set default configuration values"""
        self.input_shape = (416, 416)
        self.conf_threshold = 0.25
        self.nms_threshold = 0.5
        self.frame_skip = 2
        self.frame_counter = 0

    def apply_config(self, config: Dict):
        """Apply configuration from dict"""
        self.input_shape = tuple(config.get('input_shape', (416, 416)))
        self.conf_threshold = config.get('conf_threshold', 0.25)
        self.nms_threshold = config.get('nms_threshold', 0.5)
        self.frame_skip = config.get('frame_skip', 2)
        self.frame_counter = 0

    def _load_model(self):
        """Load model with minimal configuration"""
        print(f"Loading model from: {self.model_path}")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        try:
            if OPENVINO_VERSION == "2022+":
                model = self.core.read_model(self.model_path)
                compiled_model = self.core.compile_model(model, device_name=self.device)
                self.input_layer = compiled_model.input(0)
                self.output_layer = compiled_model.output(0)
            else:
                net = self.core.read_network(model=self.model_path)
                compiled_model = self.core.load_network(net, device_name=self.device)
                self.input_layer = next(iter(compiled_model.input_info))
                self.output_layer = next(iter(compiled_model.outputs))

            print(f"✅ Model loaded successfully on {self.device}")
            return compiled_model

        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise

    def set_roi_from_points(self, points: List[Tuple[int, int]], frame_shape: Tuple[int, int]):
        """Create ROI mask from points with robust error handling"""
        try:
            if len(points) < 3:
                print("❌ ROI needs at least 3 points")
                return False

            h, w = frame_shape[:2]

            # Validate points
            valid_points = []
            for point in points:
                x, y = point
                # Ensure points are within frame bounds
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                valid_points.append((x, y))

            if len(valid_points) < 3:
                print("❌ Not enough valid ROI points")
                return False

            # Create mask safely
            self.roi_mask = np.zeros((h, w), dtype=np.uint8)

            # Convert points to numpy array with proper dtype
            pts = np.array(valid_points, dtype=np.int32)

            # Ensure points form a valid polygon
            if len(pts) >= 3:
                # Use cv2.fillPoly with proper error handling
                try:
                    cv2.fillPoly(self.roi_mask, [pts], 255)
                    self.use_roi = True
                    self.roi_points = valid_points
                    self.roi_valid = True
                    print(f"✅ ROI set successfully with {len(valid_points)} points")
                    return True
                except cv2.error as e:
                    print(f"❌ OpenCV error in fillPoly: {e}")
                    self.roi_mask = None
                    self.use_roi = False
                    self.roi_valid = False
                    return False
            else:
                print("❌ Invalid polygon for ROI")
                return False

        except Exception as e:
            print(f"❌ Error setting ROI: {e}")
            self.roi_mask = None
            self.use_roi = False
            self.roi_valid = False
            return False

    def add_counting_line(self, point1: Tuple[int, int], point2: Tuple[int, int]):
        """Add a counting line with validation"""
        try:
            # Validate points
            x1, y1 = point1
            x2, y2 = point2

            # Check if points are different
            if abs(x1 - x2) < 5 and abs(y1 - y2) < 5:
                print("❌ Line points are too close together")
                return False

            line_id = len(self.counting_lines)
            self.counting_lines.append((point1, point2))
            self.line_counters.append(LineCounter(line_id, point1, point2))
            print(f"✅ Counting line {line_id} added")
            return True

        except Exception as e:
            print(f"❌ Error adding counting line: {e}")
            return False

    def clear_roi_and_lines(self):
        """Clear all ROI and counting lines"""
        try:
            self.roi_points = []
            self.roi_mask = None
            self.use_roi = False
            self.roi_valid = False
            self.counting_lines = []
            self.line_counters = []
            self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
            print("✅ ROI and counting lines cleared")
        except Exception as e:
            print(f"❌ Error clearing ROI and lines: {e}")

    def set_frame_skip(self, skip_value: int):
        """Set frame skip value"""
        self.frame_skip = max(1, min(10, skip_value))

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Optimized preprocessing with robust ROI handling"""
        try:
            # Apply ROI if enabled and valid
            if self.use_roi and self.roi_mask is not None and self.roi_valid:
                # Ensure roi_mask and frame have compatible dimensions
                if self.roi_mask.shape[:2] == frame.shape[:2]:
                    frame_roi = cv2.bitwise_and(frame, frame, mask=self.roi_mask)
                else:
                    print("⚠️ ROI mask size mismatch, using full frame")
                    frame_roi = frame
            else:
                frame_roi = frame

            # Resize
            resized = cv2.resize(frame_roi, self.input_shape, interpolation=cv2.INTER_LINEAR)

            # Normalize and format
            blob = resized.astype(np.float32) / 255.0
            blob = blob.transpose(2, 0, 1)
            blob = np.expand_dims(blob, 0)

            return blob

        except Exception as e:
            print(f"❌ Error in preprocessing: {e}")
            # Fallback: use original frame
            resized = cv2.resize(frame, self.input_shape, interpolation=cv2.INTER_LINEAR)
            blob = resized.astype(np.float32) / 255.0
            blob = blob.transpose(2, 0, 1)
            blob = np.expand_dims(blob, 0)
            return blob

    def postprocess_detections(self, output: np.ndarray, original_shape: Tuple[int, int]) -> List[Dict]:
        """Post-processing with robust ROI filtering"""
        detections = []

        try:
            predictions = output[0]

            # Quick confidence filter
            mask = predictions[:, 4] > self.conf_threshold
            confident_preds = predictions[mask]

            if len(confident_preds) == 0:
                return []

            # Extract data
            boxes = confident_preds[:, :4]
            confidences = confident_preds[:, 4]
            class_ids = np.argmax(confident_preds[:, 5:], axis=1)

            # Filter vehicles only
            vehicle_mask = np.isin(class_ids, list(self.vehicle_classes.keys()))
            if not np.any(vehicle_mask):
                return []

            boxes = boxes[vehicle_mask]
            confidences = confidences[vehicle_mask]
            class_ids = class_ids[vehicle_mask]

            # Convert to corner format and scale
            h_scale = original_shape[0] / self.input_shape[0]
            w_scale = original_shape[1] / self.input_shape[1]

            for i in range(len(boxes)):
                x_center, y_center, width, height = boxes[i]

                x1 = int((x_center - width/2) * w_scale)
                y1 = int((y_center - height/2) * h_scale)
                x2 = int((x_center + width/2) * w_scale)
                y2 = int((y_center + height/2) * h_scale)

                # Ensure coordinates are within bounds
                x1 = max(0, min(x1, original_shape[1] - 1))
                y1 = max(0, min(y1, original_shape[0] - 1))
                x2 = max(0, min(x2, original_shape[1] - 1))
                y2 = max(0, min(y2, original_shape[0] - 1))

                # Check if detection is within ROI (with bounds checking)
                if self.use_roi and self.roi_mask is not None and self.roi_valid:
                    try:
                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2

                        # Ensure center is within mask bounds
                        if (0 <= center_y < self.roi_mask.shape[0] and
                                0 <= center_x < self.roi_mask.shape[1]):
                            if self.roi_mask[center_y, center_x] == 0:
                                continue
                        else:
                            continue  # Skip if center is out of bounds
                    except Exception as e:
                        print(f"⚠️ ROI check error: {e}")
                        # Continue without ROI check if there's an error

                # Skip small detections
                area = (x2 - x1) * (y2 - y1)
                if area < 500:
                    continue

                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(confidences[i]),
                    'class_id': int(class_ids[i]),
                    'class_name': self.vehicle_classes[class_ids[i]]
                })

            # Simple NMS
            if len(detections) > 1:
                detections = self._simple_nms(detections)

        except Exception as e:
            print(f"❌ Error in postprocessing: {e}")

        return detections

    def _simple_nms(self, detections: List[Dict]) -> List[Dict]:
        """Simplified NMS"""
        if len(detections) <= 1:
            return detections

        detections.sort(key=lambda x: x['confidence'], reverse=True)

        keep = []
        while detections:
            current = detections.pop(0)
            keep.append(current)

            detections = [d for d in detections
                          if self._calculate_iou(current['bbox'], d['bbox']) < self.nms_threshold]

        return keep

    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """Calculate IoU between two boxes"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

        union = area1 + area2 - intersection

        return intersection / (union + 1e-6)

    def detect_vehicles(self, frame: np.ndarray) -> Tuple[List[Dict], float]:
        """Main detection function with error handling"""
        try:
            # Frame skipping
            self.frame_counter += 1
            if self.frame_counter % self.frame_skip != 0:
                return self.tracker.get_last_detections(), 0.0

            start_time = time.time()

            # Preprocess
            input_blob = self.preprocess_frame(frame)

            # Inference
            if OPENVINO_VERSION == "2022+":
                result = self.compiled_model([input_blob])
                output = result[self.output_layer]
            else:
                result = self.compiled_model.infer({self.input_layer: input_blob})
                output = result[self.output_layer]

            # Postprocess
            detections = self.postprocess_detections(output, frame.shape[:2])

            # Update tracker
            tracked_detections = self.tracker.update(detections)

            # Update line counters
            try:
                for line_counter in self.line_counters:
                    counts = line_counter.update(tracked_detections)
                    for vehicle_type, direction in counts:
                        self.vehicle_counts[vehicle_type][direction] += 1
            except Exception as e:
                print(f"⚠️ Line counter error: {e}")

            # Calculate FPS
            processing_time = time.time() - start_time
            self.update_fps()

            return tracked_detections, processing_time

        except Exception as e:
            print(f"❌ Detection error: {e}")
            return [], 0.0

    def update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        self.fps_history.append(current_time - self.last_time)
        self.last_time = current_time

    def get_fps(self) -> float:
        """Get current FPS"""
        if len(self.fps_history) < 2:
            return 0.0
        return 1.0 / (np.mean(self.fps_history) + 1e-6)

    def get_statistics(self) -> Dict:
        """Get current statistics"""
        return {
            'fps': self.get_fps(),
            'frame_skip': self.frame_skip,
            'roi_enabled': self.use_roi and self.roi_valid,
            'line_count': len(self.counting_lines),
            'vehicle_counts': dict(self.vehicle_counts),
            'total_detections': sum(sum(counts.values()) for counts in self.vehicle_counts.values())
        }