"""
src/core/detector.py
Refactored berdasarkan newdetrev1.py yang sudah terbukti bekerja
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


class DeepSORTTracker:
    """Simplified Deep SORT tracker implementation - dari newdetrev1.py"""

    def __init__(self):
        self.tracks = {}
        self.next_id = 1
        self.track_trails = defaultdict(lambda: deque(maxlen=30))
        self.max_age = 1
        self.min_hits = 3
        self.iou_threshold = 0.3
        self.last_detections = []

    def update(self, detections: List[Dict]) -> List[Dict]:
        """Update tracks with new detections"""
        # Age existing tracks
        for track_id in list(self.tracks.keys()):
            self.tracks[track_id]['age'] += 1
            if self.tracks[track_id]['age'] > self.max_age:
                del self.tracks[track_id]
                if track_id in self.track_trails:
                    del self.track_trails[track_id]

        if not detections:
            return self.last_detections

        # Match detections to existing tracks
        if self.tracks:
            self._match_tracks(detections)
        else:
            # Initialize new tracks
            for det in detections:
                self._create_track(det)

        # Update trails
        tracked_detections = []
        for track_id, track in self.tracks.items():
            if track['hits'] >= self.min_hits:
                det = track['detection'].copy()
                det['track_id'] = track_id
                tracked_detections.append(det)

                # Update trail
                center = self._get_center(det['bbox'])
                self.track_trails[track_id].append(center)

        self.last_detections = tracked_detections
        return tracked_detections

    def _match_tracks(self, detections: List[Dict]):
        """Match detections to existing tracks using IoU"""
        # Create cost matrix
        track_ids = list(self.tracks.keys())
        cost_matrix = np.zeros((len(track_ids), len(detections)))

        for i, track_id in enumerate(track_ids):
            track_bbox = self.tracks[track_id]['detection']['bbox']
            for j, det in enumerate(detections):
                iou = self._calculate_iou(track_bbox, det['bbox'])
                cost_matrix[i, j] = 1 - iou  # Convert to cost

        # Simple greedy matching
        matched_tracks = set()
        matched_dets = set()

        # Sort by minimum cost
        matches = []
        for i in range(len(track_ids)):
            for j in range(len(detections)):
                if cost_matrix[i, j] < 1 - self.iou_threshold:
                    matches.append((cost_matrix[i, j], i, j))

        matches.sort()

        # Assign matches
        for cost, track_idx, det_idx in matches:
            if track_idx not in matched_tracks and det_idx not in matched_dets:
                track_id = track_ids[track_idx]
                self.tracks[track_id]['detection'] = detections[det_idx]
                self.tracks[track_id]['age'] = 0
                self.tracks[track_id]['hits'] += 1
                matched_tracks.add(track_idx)
                matched_dets.add(det_idx)

        # Create new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in matched_dets:
                self._create_track(det)

    def _create_track(self, detection: Dict):
        """Create new track"""
        self.tracks[self.next_id] = {
            'detection': detection,
            'age': 0,
            'hits': 1
        }
        self.next_id += 1

    def _get_center(self, bbox: List[int]) -> Tuple[int, int]:
        """Get center point of bbox"""
        return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)

    def _calculate_iou(self, box1: List[int], box2: List[int]) -> float:
        """Calculate IoU"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

        union = area1 + area2 - intersection

        return intersection / (union + 1e-6)

    def get_last_detections(self) -> List[Dict]:
        """Get last detections"""
        return self.last_detections


class LineCounter:
    """Count vehicles crossing a line - dari newdetrev1.py dengan improvements"""

    def __init__(self, line_id: int, point1: Tuple[int, int], point2: Tuple[int, int]):
        self.line_id = line_id
        self.point1 = point1
        self.point2 = point2
        self.tracked_vehicles = {}
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

    def update(self, detections: List[Dict]) -> List[Tuple[str, str]]:
        """Update line counting"""
        counts = []

        for det in detections:
            track_id = det.get('track_id', -1)
            if track_id == -1:
                continue

            center = ((det['bbox'][0] + det['bbox'][2]) // 2,
                      (det['bbox'][1] + det['bbox'][3]) // 2)

            # Check line crossing
            crossed = self._check_line_crossing(center)

            if track_id in self.tracked_vehicles:
                prev_side = self.tracked_vehicles[track_id]['side']
                if crossed != prev_side and crossed != 0:
                    # Vehicle crossed the line
                    direction = 'up' if crossed > prev_side else 'down'
                    vehicle_type = det['class_name']
                    counts.append((vehicle_type, direction))
                    self.vehicle_counts[vehicle_type][direction] += 1

                    print(f"🚦 Vehicle {track_id} ({vehicle_type}) crossed line {self.line_id} - {direction}")

            self.tracked_vehicles[track_id] = {
                'side': crossed,
                'class': det['class_name']
            }

        return counts

    def _check_line_crossing(self, point: Tuple[int, int]) -> int:
        """Check which side of line the point is on"""
        # Using cross product to determine side
        x1, y1 = self.point1
        x2, y2 = self.point2
        x, y = point

        cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)

        if cross > 0:
            return 1
        elif cross < 0:
            return -1
        else:
            return 0

    def get_statistics(self) -> Dict:
        """Get line crossing statistics"""
        return {
            'line_id': self.line_id,
            'point1': self.point1,
            'point2': self.point2,
            'vehicle_counts': dict(self.vehicle_counts),
            'total_crossings': sum(sum(counts.values()) for counts in self.vehicle_counts.values())
        }

    def reset_counts(self):
        """Reset crossing counts"""
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
        self.tracked_vehicles = {}


class OptimizedVehicleDetector:
    """
    Vehicle detection system with manual ROI, Deep SORT tracking, and line counting
    Refactored berdasarkan newdetrev1.py
    """

    def __init__(self, model_path: str, device: str = "CPU", config: Optional[Dict] = None):
        self.device = device
        self.model_path = model_path

        # Initialize OpenVINO
        if OPENVINO_VERSION == "2022+":
            self.core = ov.Core()
        else:
            self.core = IECore()

        # Load model
        self.compiled_model = self._load_model()

        # Detection config - sama seperti newdetrev1.py
        self.input_shape = (416, 416)
        self.conf_threshold = 0.25
        self.nms_threshold = 0.5

        # Apply custom config if provided
        if config:
            self.input_shape = tuple(config.get('input_shape', (416, 416)))
            self.conf_threshold = config.get('conf_threshold', 0.25)
            self.nms_threshold = config.get('nms_threshold', 0.5)
            self.frame_skip = config.get('frame_skip', 2)
        else:
            self.frame_skip = 2

        # Vehicle classes - sama seperti newdetrev1.py
        self.vehicle_classes = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}

        # Deep SORT tracker
        self.tracker = DeepSORTTracker()

        # Frame skipping
        self.frame_counter = 0

        # Performance monitoring
        self.fps_history = deque(maxlen=30)
        self.last_time = time.time()

        # ROI settings - improved berdasarkan newdetrev1.py
        self.roi_points = []
        self.roi_mask = None
        self.use_roi = False
        self.roi_original_shape = None         # Shape when ROI was created
        self.current_frame_shape = None        # Current processing frame shape
        self.roi_scale_factor = (1.0, 1.0)    # Scale factor for ROI adaptation

        # Line counter settings
        self.counting_lines = []
        self.line_counters = []
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})

        # Drawing states
        self.drawing_roi = False
        self.drawing_line = False
        self.temp_line_points = []

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
        """COMPREHENSIVE: ROI creation dengan dynamic shape management"""
        if len(points) < 3:
            print("❌ ROI needs at least 3 points")
            return False

        try:
            h, w = frame_shape[:2]
            print(f"🎯 Creating ROI for frame shape: {w}x{h}")

            # Store original frame shape
            self.roi_original_shape = (h, w)

            # Validate and clamp points
            validated_points = []
            for point in points:
                x, y = int(point[0]), int(point[1])
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                validated_points.append((x, y))

            # Create ROI mask
            success = self._create_roi_mask(validated_points, (h, w))

            if success:
                self.roi_points = validated_points
                self.use_roi = True
                self.current_frame_shape = (h, w)
                self.roi_scale_factor = (1.0, 1.0)

                roi_area = np.sum(self.roi_mask > 0)
                total_area = h * w
                roi_percentage = (roi_area / total_area) * 100

                print(f"✅ ROI created successfully")
                print(f"   Original shape: {self.roi_original_shape}")
                print(f"   Points: {len(validated_points)}")
                print(f"   Area: {roi_percentage:.1f}% of frame")
                return True
            else:
                return False

        except Exception as e:
            print(f"❌ Error creating ROI: {e}")
            self._reset_roi()
            return False

    def _create_roi_mask(self, points: List[Tuple[int, int]], shape: Tuple[int, int]) -> bool:
        """Create ROI mask with error handling"""
        try:
            h, w = shape
            self.roi_mask = np.zeros((h, w), dtype=np.uint8)

            if len(points) < 3:
                return False

            pts = np.array(points, dtype=np.int32)
            cv2.fillPoly(self.roi_mask, [pts], 255)

            # Validate mask
            if np.sum(self.roi_mask) == 0:
                print("❌ ROI mask is empty")
                return False

            return True

        except Exception as e:
            print(f"❌ Error creating ROI mask: {e}")
            return False

    def _update_roi_for_frame_shape(self, current_shape: Tuple[int, int]) -> bool:
        """FIXED: Update ROI mask jika frame shape berubah"""
        try:
            if not self.use_roi or not self.roi_points or self.roi_original_shape is None:
                return True

            current_h, current_w = current_shape[:2]
            original_h, original_w = self.roi_original_shape

            # Check if frame shape changed significantly
            if (abs(current_h - original_h) > 5 or abs(current_w - original_w) > 5):
                print(f"🔄 Frame shape changed: {original_w}x{original_h} → {current_w}x{current_h}")

                # Calculate scale factors
                scale_x = current_w / original_w
                scale_y = current_h / original_h

                # Scale ROI points
                scaled_points = []
                for x, y in self.roi_points:
                    new_x = int(x * scale_x)
                    new_y = int(y * scale_y)
                    new_x = max(0, min(new_x, current_w - 1))
                    new_y = max(0, min(new_y, current_h - 1))
                    scaled_points.append((new_x, new_y))

                # Create new mask with scaled points
                success = self._create_roi_mask(scaled_points, current_shape)

                if success:
                    self.roi_original_shape = current_shape
                    self.roi_points = scaled_points
                    self.current_frame_shape = current_shape
                    self.roi_scale_factor = (scale_x, scale_y)
                    print(f"✅ ROI updated for new frame shape")
                    return True
                else:
                    print("❌ Failed to update ROI for new frame shape")
                    self._reset_roi()
                    return False

            # Update current frame shape for tracking
            self.current_frame_shape = current_shape
            return True

        except Exception as e:
            print(f"❌ Error updating ROI: {e}")
            self._reset_roi()
            return False

    def add_counting_line(self, point1: Tuple[int, int], point2: Tuple[int, int]):
        """Add a counting line"""
        try:
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
        self.roi_points = []
        self.roi_mask = None
        self.use_roi = False
        self.counting_lines = []
        self.line_counters = []
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
        print("✅ ROI and counting lines cleared")

    def _reset_roi(self):
        """Reset ROI state"""
        self.roi_mask = None
        self.use_roi = False
        self.roi_original_shape = None
        self.current_frame_shape = None
        self.roi_scale_factor = (1.0, 1.0)

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """FIXED: Preprocessing dengan ROI size mismatch handling"""
        try:
            # Update ROI untuk frame shape saat ini
            current_shape = frame.shape[:2]

            if self.use_roi:
                # Ensure ROI is compatible dengan current frame
                if not self._update_roi_for_frame_shape(current_shape):
                    print("⚠️ ROI update failed, using full frame")
                    frame_roi = frame
                else:
                    # Apply ROI jika mask compatible
                    if (self.roi_mask is not None and
                            self.roi_mask.shape[:2] == frame.shape[:2]):

                        frame_roi = frame.copy()
                        frame_roi[self.roi_mask == 0] = 0  # Set area luar ROI = hitam
                        print(f"✅ ROI applied successfully to {frame.shape[:2]} frame")
                    else:
                        print(f"⚠️ ROI mask shape {self.roi_mask.shape[:2] if self.roi_mask is not None else 'None'} != frame shape {frame.shape[:2]}")
                        frame_roi = frame
            else:
                frame_roi = frame

            # Resize untuk model inference
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
        """FIXED: Post-processing dengan robust ROI filtering"""
        detections = []

        try:
            # Ensure ROI is updated untuk current frame shape
            if self.use_roi:
                self._update_roi_for_frame_shape(original_shape)

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

            roi_filtered_count = 0
            total_candidates = len(boxes)

            for i in range(len(boxes)):
                x_center, y_center, width, height = boxes[i]

                x1 = int((x_center - width/2) * w_scale)
                y1 = int((y_center - height/2) * h_scale)
                x2 = int((x_center + width/2) * w_scale)
                y2 = int((y_center + height/2) * h_scale)

                # Clamp coordinates
                x1 = max(0, min(x1, original_shape[1] - 1))
                y1 = max(0, min(y1, original_shape[0] - 1))
                x2 = max(0, min(x2, original_shape[1] - 1))
                y2 = max(0, min(y2, original_shape[0] - 1))

                # ROI filtering dengan robust checking
                if self.use_roi and self.roi_mask is not None:
                    if self.roi_mask.shape[:2] == original_shape[:2]:
                        # Check multiple points dalam bounding box
                        bbox_points = [
                            ((x1 + x2) // 2, (y1 + y2) // 2),  # Center
                            (x1, y1),  # Top-left
                            (x2, y2),  # Bottom-right
                            ((x1 + x2) // 2, y1),  # Top-center
                            ((x1 + x2) // 2, y2),  # Bottom-center
                        ]

                        points_in_roi = 0
                        for px, py in bbox_points:
                            if (0 <= py < self.roi_mask.shape[0] and
                                    0 <= px < self.roi_mask.shape[1]):
                                if self.roi_mask[py, px] > 0:
                                    points_in_roi += 1

                        # Require at least 3 out of 5 points dalam ROI
                        if points_in_roi < 3:
                            roi_filtered_count += 1
                            continue
                    else:
                        print(f"⚠️ ROI mask {self.roi_mask.shape[:2]} != frame {original_shape[:2]}")
                        # Force recreate ROI mask untuk current frame
                        if self.roi_points and len(self.roi_points) >= 3:
                            self._create_roi_mask(self.roi_points, original_shape)

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

            # Apply NMS
            if len(detections) > 1:
                detections = self._simple_nms(detections)

            if self.use_roi:
                print(f"📊 ROI filtering: {len(detections)}/{total_candidates} detections passed (filtered out: {roi_filtered_count})")
            else:
                print(f"📊 Full frame: {len(detections)} detections found")

            return detections

        except Exception as e:
            print(f"❌ Error in postprocessing: {e}")
            return []

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """IMPROVED: Draw dengan ROI visualization yang lebih clear"""
        result_frame = frame.copy()

        try:
            # Draw ROI overlay jika enabled
            if self.use_roi and self.roi_mask is not None:
                if self.roi_mask.shape[:2] == frame.shape[:2]:
                    # Create colored overlay for ROI area
                    overlay = result_frame.copy()

                    # ROI area dengan green tint
                    roi_colored = np.zeros_like(result_frame)
                    roi_colored[:, :, 1] = 50  # Green channel

                    # Apply overlay hanya di area ROI
                    mask_3ch = np.stack([self.roi_mask, self.roi_mask, self.roi_mask], axis=2)
                    mask_norm = mask_3ch.astype(np.float32) / 255.0

                    overlay = overlay + (roi_colored * mask_norm).astype(np.uint8)
                    result_frame = cv2.addWeighted(result_frame, 0.85, overlay, 0.15, 0)

                    # Draw ROI border
                    if self.roi_points:
                        pts = np.array(self.roi_points, np.int32)
                        cv2.polylines(result_frame, [pts], True, (0, 255, 0), 3)

                    # ROI info text
                    roi_area = np.sum(self.roi_mask > 0)
                    total_area = frame.shape[0] * frame.shape[1]
                    roi_percent = (roi_area / total_area) * 100

                    cv2.putText(result_frame, f"ROI: {roi_percent:.1f}% active",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(result_frame, f"Detection limited to GREEN area",
                                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Draw counting lines
            for i, (p1, p2) in enumerate(self.counting_lines):
                cv2.line(result_frame, p1, p2, (0, 255, 255), 3)
                mid_point = ((p1[0] + p2[0])//2, (p1[1] + p2[1])//2)
                cv2.putText(result_frame, f"Line {i}", mid_point,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Draw detections
            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                class_name = det['class_name']
                track_id = det.get('track_id', -1)

                # Colors
                colors = {
                    'car': (0, 255, 0),
                    'motorcycle': (255, 255, 0),
                    'bus': (255, 0, 0),
                    'truck': (0, 0, 255)
                }
                color = colors.get(class_name, (128, 128, 128))

                # Draw thick box untuk visibility
                cv2.rectangle(result_frame, (x1, y1), (x2, y2), color, 3)

                # Label
                label = f"{class_name} #{track_id}" if track_id > 0 else class_name
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                cv2.rectangle(result_frame, (x1, y1-label_size[1]-10),
                              (x1+label_size[0]+4, y1), color, -1)
                cv2.putText(result_frame, label, (x1+2, y1-6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Track trail
                if track_id in self.tracker.track_trails:
                    trail = self.tracker.track_trails[track_id]
                    for j in range(1, len(trail)):
                        cv2.line(result_frame, trail[j-1], trail[j], color, 2)

            return result_frame

        except Exception as e:
            print(f"❌ Error drawing detections: {e}")
            return frame

    def get_statistics(self) -> Dict:
        """Enhanced statistics dengan ROI info"""
        stats = {
            'fps': self.get_fps(),
            'frame_skip': self.frame_skip,
            'roi_enabled': self.use_roi,
            'line_count': len(self.counting_lines),
            'vehicle_counts': dict(self.vehicle_counts),
            'total_detections': sum(sum(counts.values()) for counts in self.vehicle_counts.values()),
            'active_tracks': len(self.tracker.tracks)
        }

        # Add ROI-specific info
        if self.use_roi and self.roi_mask is not None:
            roi_area = np.sum(self.roi_mask > 0)
            if self.current_frame_shape:
                total_area = self.current_frame_shape[0] * self.current_frame_shape[1]
                stats['roi_coverage_percent'] = (roi_area / total_area) * 100
            else:
                stats['roi_coverage_percent'] = 0
        else:
            stats['roi_coverage_percent'] = 100  # Full frame

        return stats

    def _simple_nms(self, detections: List[Dict]) -> List[Dict]:
        """Simplified NMS - sama seperti newdetrev1.py"""
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
        """Main detection function - sama seperti newdetrev1.py dengan improvements"""
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

        # Update line counters - IMPROVED untuk GUI integration
        for line_counter in self.line_counters:
            counts = line_counter.update(tracked_detections)
            for vehicle_type, direction in counts:
                self.vehicle_counts[vehicle_type][direction] += 1

        # Calculate FPS
        processing_time = time.time() - start_time
        self.update_fps()

        return tracked_detections, processing_time

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

    def apply_config(self, config: Dict):
        """Apply configuration dari config manager"""
        self.input_shape = tuple(config.get('input_shape', (416, 416)))
        self.conf_threshold = config.get('conf_threshold', 0.25)
        self.nms_threshold = config.get('nms_threshold', 0.5)
        self.frame_skip = config.get('frame_skip', 2)

    def set_frame_skip(self, skip_value: int):
        """Set frame skip value"""
        self.frame_skip = max(1, min(10, skip_value))

    # TAMBAHAN: Method untuk debug ROI
    def debug_roi_mask(self, frame: np.ndarray) -> np.ndarray:
        """Debug method untuk visualisasi ROI mask"""
        if not self.use_roi or self.roi_mask is None:
            return frame

        debug_frame = frame.copy()

        # Show ROI area dengan overlay
        if self.roi_mask.shape[:2] == frame.shape[:2]:
            # Area dalam ROI = normal
            # Area luar ROI = dimmed
            mask_3ch = cv2.cvtColor(self.roi_mask, cv2.COLOR_GRAY2BGR)
            mask_3ch = mask_3ch.astype(np.float32) / 255.0

            # Dim area outside ROI
            debug_frame = debug_frame.astype(np.float32)
            debug_frame = debug_frame * mask_3ch + debug_frame * 0.3 * (1 - mask_3ch)
            debug_frame = debug_frame.astype(np.uint8)

            # Draw ROI border
            if self.roi_points:
                pts = np.array(self.roi_points, np.int32)
                cv2.polylines(debug_frame, [pts], True, (0, 255, 0), 3)

            # Add text info
            roi_area = np.sum(self.roi_mask > 0)
            total_area = frame.shape[0] * frame.shape[1]
            roi_percent = (roi_area / total_area) * 100

            cv2.putText(debug_frame, f"ROI: {roi_percent:.1f}% of frame",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(debug_frame, "Detection LIMITED to GREEN area",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        return debug_frame