"""
src/core/line_counter.py - Simple line counter
"""

from typing import List, Dict, Tuple


class LineCounter:
    """Simple line counter implementation"""
    
    def __init__(self, line_id: int, point1: Tuple[int, int], point2: Tuple[int, int]):
        self.line_id = line_id
        self.point1 = point1
        self.point2 = point2
        self.tracked_vehicles = {}
        self.total_crossings = {'up': 0, 'down': 0}
    
    def update(self, detections: List[Dict]) -> List[Tuple[str, str]]:
        """Simple update - no actual line crossing detection for now"""
        return []
    
    def get_statistics(self) -> Dict:
        """Get line crossing statistics"""
        return {
            'line_id': self.line_id,
            'point1': self.point1,
            'point2': self.point2,
            'crossings': self.total_crossings.copy(),
            'total': sum(self.total_crossings.values())
        }
    
    def reset_counts(self):
        """Reset crossing counts"""
        self.total_crossings = {'up': 0, 'down': 0}
        self.tracked_vehicles = {}
