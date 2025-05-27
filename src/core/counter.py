"""
Complete src/core/counter.py
LineCounter class extracted dari newdetrev1.py yang working
"""

from typing import List, Dict, Tuple
from collections import defaultdict


class LineCounter:
    """Count vehicles crossing a line - exact copy dari newdetrev1.py yang bekerja"""

    def __init__(self, line_id: int, point1: Tuple[int, int], point2: Tuple[int, int]):
        self.line_id = line_id
        self.point1 = point1
        self.point2 = point2
        self.tracked_vehicles = {}

        # Track counts per vehicle type
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
        self.total_crossings = {'up': 0, 'down': 0}

    def update(self, detections: List[Dict]) -> List[Tuple[str, str]]:
        """Update line counting - berdasarkan newdetrev1.py yang working"""
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

                # Check if vehicle crossed the line (changed from one side to another)
                if crossed != prev_side and crossed != 0 and prev_side != 0:
                    # Vehicle crossed the line
                    direction = 'up' if crossed > prev_side else 'down'
                    vehicle_type = det.get('class_name', 'car')

                    # Add to counts
                    counts.append((vehicle_type, direction))
                    self.vehicle_counts[vehicle_type][direction] += 1
                    self.total_crossings[direction] += 1

                    print(f"🚦 Vehicle {track_id} ({vehicle_type}) crossed line {self.line_id} - {direction}")

            # Update tracking
            self.tracked_vehicles[track_id] = {
                'side': crossed,
                'class': det.get('class_name', 'car'),
                'center': center
            }

        return counts

    def _check_line_crossing(self, point: Tuple[int, int]) -> int:
        """Check which side of line the point is on - exact dari newdetrev1.py"""
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
            'crossings': self.total_crossings.copy(),
            'total': sum(self.total_crossings.values()),
            'vehicle_counts': {
                vehicle_type: {
                    'up': counts['up'],
                    'down': counts['down'],
                    'total': counts['up'] + counts['down']
                }
                for vehicle_type, counts in self.vehicle_counts.items()
            },
            'tracked_vehicles': len(self.tracked_vehicles)
        }

    def reset_counts(self):
        """Reset crossing counts"""
        self.vehicle_counts = defaultdict(lambda: {'up': 0, 'down': 0})
        self.total_crossings = {'up': 0, 'down': 0}
        self.tracked_vehicles = {}
        print(f"🔄 Line {self.line_id} counts reset")