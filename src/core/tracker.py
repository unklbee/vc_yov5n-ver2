## Simplified Tracker (`src/core/tracker.py`)

"""Lightweight vehicle tracker"""
import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict, deque

class SimpleTracker:
    """Lightweight object tracker"""

    def __init__(self, max_age: int = 5, min_hits: int = 3, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        self.tracks = {}
        self.next_id = 1
        self.track_trails = defaultdict(lambda: deque(maxlen=20))

    def update(self, detections: List[Dict]) -> List[Dict]:
        """Update tracks with new detections"""
        # Age existing tracks
        self._age_tracks()

        if not detections:
            return self._get_confirmed_tracks()

        # Match detections to tracks
        if self.tracks:
            self._match_detections_to_tracks(detections)
        else:
            # Initialize new tracks
            for detection in detections:
                self._create_track(detection)

        return self._get_confirmed_tracks()

    def _age_tracks(self):
        """Age all tracks and remove old ones"""
        tracks_to_remove = []
        for track_id, track in self.tracks.items():
            track['age'] += 1
            if track['age'] > self.max_age:
                tracks_to_remove.append(track_id)

        for track_id in tracks_to_remove:
            del self.tracks[track_id]
            if track_id in self.track_trails:
                del self.track_trails[track_id]

    def _match_detections_to_tracks(self, detections: List[Dict]):
        """Simple greedy matching based on IoU"""
        track_ids = list(self.tracks.keys())

        # Calculate IoU matrix
        iou_matrix = np.zeros((len(track_ids), len(detections)))
        for i, track_id in enumerate(track_ids):
            track_bbox = self.tracks[track_id]['bbox']
            for j, detection in enumerate(detections):
                iou_matrix[i, j] = self._calculate_iou(track_bbox, detection['bbox'])

        # Greedy assignment
        matched_tracks = set()
        matched_detections = set()

        # Find best matches above threshold
        while True:
            max_iou = np.max(iou_matrix)
            if max_iou < self.iou_threshold:
                break

            max_pos = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            track_idx, det_idx = max_pos

            # Update track
            track_id = track_ids[track_idx]
            self._update_track(track_id, detections[det_idx])

            matched_tracks.add(track_idx)
            matched_detections.add(det_idx)

            # Remove matched from consideration
            iou_matrix[track_idx, :] = 0
            iou_matrix[:, det_idx] = 0

        # Create new tracks for unmatched detections
        for i, detection in enumerate(detections):
            if i not in matched_detections:
                self._create_track(detection)

    def _create_track(self, detection: Dict):
        """Create new track"""
        self.tracks[self.next_id] = {
            'bbox': detection['bbox'],
            'class_name': detection['class_name'],
            'confidence': detection['confidence'],
            'age': 0,
            'hits': 1
        }
        self._update_trail(self.next_id, detection['bbox'])
        self.next_id += 1

    def _update_track(self, track_id: int, detection: Dict):
        """Update existing track"""
        self.tracks[track_id].update({
            'bbox': detection['bbox'],
            'confidence': detection['confidence'],
            'age': 0,
            'hits': self.tracks[track_id]['hits'] + 1
        })
        self._update_trail(track_id, detection['bbox'])

    def _update_trail(self, track_id: int, bbox: List[int]):
        """Update track trail"""
        center = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
        self.track_trails[track_id].append(center)

    def _get_confirmed_tracks(self) -> List[Dict]:
        """Get confirmed tracks (enough hits)"""
        confirmed = []
        for track_id, track in self.tracks.items():
            if track['hits'] >= self.min_hits:
                track_data = track.copy()
                track_data['track_id'] = track_id
                confirmed.append(track_data)
        return confirmed

    @staticmethod
    def _calculate_iou(box1: List[int], box2: List[int]) -> float:
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