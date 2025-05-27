## 1. Simplified Detector (`src/core/detector.py`)

"""Optimized Vehicle Detector - Lightweight and Efficient"""
import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from collections import deque, defaultdict
import time
from pathlib import Path

class VehicleDetector:
    """Lightweight vehicle detector with OpenVINO support"""

    # Class constants
    VEHICLE_CLASSES = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
    DEFAULT_CONFIG = {
        'input_shape': (416, 416),
        'conf_threshold': 0.25,
        'nms_threshold': 0.5,
        'device': 'CPU'
    }

    def __init__(self, model_path: Union[str, Path], config: Optional[Dict] = None):
        self.model_path = Path(model_path)
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # Performance tracking
        self.fps_tracker = FPSTracker()

        # Detection state
        self.roi_mask = None
        self.counting_lines = []
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

        # Lazy-loaded components
        self._model = None
        self._tracker = None

    @property
    def model(self):
        """Lazy load OpenVINO model"""
        if self._model is None:
            self._model = self._load_model()
        return self._model

    @property
    def tracker(self):
        """Lazy load tracker"""
        if self._tracker is None:
            from .tracker import SimpleTracker
            self._tracker = SimpleTracker()
        return self._tracker

    def _load_model(self):
        """Load OpenVINO model with fallback"""
        try:
            import openvino as ov
            core = ov.Core()
            model = core.read_model(str(self.model_path))
            compiled_model = core.compile_model(model, self.config['device'])
            print(f"✅ Model loaded on {self.config['device']}")
            return OpenVINOModel(compiled_model)
        except ImportError:
            print("⚠️ OpenVINO not available, using mock model")
            return MockModel()
        except Exception as e:
            print(f"⚠️ Model loading failed: {e}, using mock model")
            return MockModel()

    def detect(self, frame: np.ndarray) -> Tuple[List[Dict], Dict]:
        """Main detection method"""
        start_time = time.time()

        # Apply ROI if set
        processed_frame = self._apply_roi(frame) if self.roi_mask is not None else frame

        # Run inference
        detections = self._run_inference(processed_frame, frame.shape)

        # Track vehicles
        tracked_detections = self.tracker.update(detections)

        # Update counters
        self._update_counters(tracked_detections)

        # Calculate stats
        processing_time = time.time() - start_time
        self.fps_tracker.update(processing_time)

        stats = {
            'fps': self.fps_tracker.get_fps(),
            'processing_time': processing_time,
            'detection_count': len(tracked_detections),
            'roi_enabled': self.roi_mask is not None,
            'line_count': len(self.counting_lines)
        }

        return tracked_detections, stats

    def _apply_roi(self, frame: np.ndarray) -> np.ndarray:
        """Apply ROI mask to frame"""
        return cv2.bitwise_and(frame, frame, mask=self.roi_mask)

    def _run_inference(self, frame: np.ndarray, original_shape: Tuple) -> List[Dict]:
        """Run model inference"""
        # Preprocess
        input_tensor = self._preprocess(frame)

        # Inference
        output = self.model.predict(input_tensor)

        # Postprocess
        return self._postprocess(output, original_shape)

    def _preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for inference"""
        # Resize
        resized = cv2.resize(frame, self.config['input_shape'])

        # Normalize and format
        blob = resized.astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)  # HWC to CHW
        return np.expand_dims(blob, 0)  # Add batch dimension

    def _postprocess(self, output: np.ndarray, original_shape: Tuple) -> List[Dict]:
        """Postprocess model output"""
        detections = []
        predictions = output[0]  # Remove batch dimension

        # Filter by confidence
        confident_mask = predictions[:, 4] > self.config['conf_threshold']
        confident_preds = predictions[confident_mask]

        if len(confident_preds) == 0:
            return []

        # Extract components
        boxes = confident_preds[:, :4]
        confidences = confident_preds[:, 4]
        class_scores = confident_preds[:, 5:]
        class_ids = np.argmax(class_scores, axis=1)

        # Filter vehicles only
        vehicle_mask = np.isin(class_ids, list(self.VEHICLE_CLASSES.keys()))
        if not np.any(vehicle_mask):
            return []

        boxes = boxes[vehicle_mask]
        confidences = confidences[vehicle_mask]
        class_ids = class_ids[vehicle_mask]

        # Convert and scale boxes
        h_scale = original_shape[0] / self.config['input_shape'][0]
        w_scale = original_shape[1] / self.config['input_shape'][1]

        for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
            x_center, y_center, width, height = box

            # Convert to corner format
            x1 = int((x_center - width/2) * w_scale)
            y1 = int((y_center - height/2) * h_scale)
            x2 = int((x_center + width/2) * w_scale)
            y2 = int((y_center + height/2) * h_scale)

            # Validate bounds
            x1 = max(0, min(x1, original_shape[1] - 1))
            y1 = max(0, min(y1, original_shape[0] - 1))
            x2 = max(0, min(x2, original_shape[1] - 1))
            y2 = max(0, min(y2, original_shape[0] - 1))

            # Skip small detections
            if (x2 - x1) * (y2 - y1) < 500:
                continue

            detections.append({
                'bbox': [x1, y1, x2, y2],
                'confidence': float(conf),
                'class_id': int(class_id),
                'class_name': self.VEHICLE_CLASSES[class_id]
            })

        # Apply NMS
        return self._apply_nms(detections)

    def _apply_nms(self, detections: List[Dict]) -> List[Dict]:
        """Apply Non-Maximum Suppression"""
        if len(detections) <= 1:
            return detections

        # Sort by confidence
        detections.sort(key=lambda x: x['confidence'], reverse=True)

        keep = []
        while detections:
            current = detections.pop(0)
            keep.append(current)

            # Remove overlapping detections
            detections = [
                det for det in detections
                if self._calculate_iou(current['bbox'], det['bbox']) < self.config['nms_threshold']
            ]

        return keep

    @staticmethod
    def _calculate_iou(box1: List[int], box2: List[int]) -> float:
        """Calculate Intersection over Union"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / (union + 1e-6)

    def _update_counters(self, detections: List[Dict]):
        """Update vehicle counters"""
        # Simplified counting logic
        for detection in detections:
            track_id = detection.get('track_id', -1)
            if track_id > 0:  # Valid track
                # Count logic would go here
                pass

    def set_roi(self, points: List[Tuple[int, int]], frame_shape: Tuple[int, int]) -> bool:
        """Set Region of Interest"""
        if len(points) < 3:
            return False

        try:
            h, w = frame_shape[:2]
            self.roi_mask = np.zeros((h, w), dtype=np.uint8)
            pts = np.array(points, dtype=np.int32)
            cv2.fillPoly(self.roi_mask, [pts], 255)
            return True
        except Exception as e:
            print(f"ROI setting failed: {e}")
            return False

    def add_counting_line(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> bool:
        """Add counting line"""
        if abs(point1[0] - point2[0]) < 5 and abs(point1[1] - point2[1]) < 5:
            return False  # Points too close

        line_id = len(self.counting_lines)
        self.counting_lines.append({
            'id': line_id,
            'point1': point1,
            'point2': point2,
            'crossings': {'up': 0, 'down': 0}
        })
        return True

    def clear_roi_and_lines(self):
        """Clear ROI and counting lines"""
        self.roi_mask = None
        self.counting_lines = []
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})


class FPSTracker:
    """Lightweight FPS tracking"""

    def __init__(self, max_samples: int = 30):
        self.samples = deque(maxlen=max_samples)
        self.last_time = time.time()

    def update(self, processing_time: float = None):
        """Update FPS calculation"""
        current_time = time.time()
        if processing_time is None:
            frame_time = current_time - self.last_time
        else:
            frame_time = processing_time

        self.samples.append(frame_time)
        self.last_time = current_time

    def get_fps(self) -> float:
        """Get current FPS"""
        if len(self.samples) < 2:
            return 0.0
        avg_time = sum(self.samples) / len(self.samples)
        return 1.0 / (avg_time + 1e-6)


class OpenVINOModel:
    """OpenVINO model wrapper"""

    def __init__(self, compiled_model):
        self.model = compiled_model
        self.input_layer = compiled_model.input(0)
        self.output_layer = compiled_model.output(0)

    def predict(self, input_tensor: np.ndarray) -> np.ndarray:
        """Run inference"""
        result = self.model([input_tensor])
        return result[self.output_layer]


class MockModel:
    """Mock model for testing"""

    def predict(self, input_tensor: np.ndarray) -> np.ndarray:
        """Return mock predictions"""
        batch_size = input_tensor.shape[0]
        # Mock YOLO output: [batch, 25200, 85] for 80 classes + 5 (x,y,w,h,conf)
        return np.random.random((batch_size, 25200, 85)) * 0.1  # Low confidence values