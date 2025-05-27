"""
src/core/tracker.py
Refactored berdasarkan DeepSORTTracker dari newdetrev1.py yang sudah terbukti bekerja
"""

import numpy as np
from collections import deque, defaultdict
from typing import List, Dict, Tuple


class DeepSORTTracker:
    """Simplified Deep SORT tracker implementation - exact copy dari newdetrev1.py"""

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

    def reset(self):
        """Reset tracker state"""
        self.tracks = {}
        self.next_id = 1
        self.track_trails = defaultdict(lambda: deque(maxlen=30))
        self.last_detections = []