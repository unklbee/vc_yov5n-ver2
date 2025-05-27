## Optimized Video Source (`src/utils/video_source.py`)

"""Optimized video source handling"""
import cv2
from typing import Tuple, Optional, Union
from pathlib import Path

class VideoSource:
    """Universal video source handler"""

    def __init__(self, source: Union[str, int, Path]):
        self.source = source
        self.cap = None
        self.properties = {}
        self._frame_count = 0

    def open(self) -> bool:
        """Open video source"""
        try:
            self.cap = cv2.VideoCapture(self.source)
            if self.cap.isOpened():
                self._get_properties()
                return True
        except Exception as e:
            print(f"Failed to open video source: {e}")
        return False

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame from source"""
        if not self.cap or not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if ret:
            self._frame_count += 1

        return ret, frame

    def release(self):
        """Release video source"""
        if self.cap:
            self.cap.release()
            self.cap = None

    def _get_properties(self):
        """Get video properties"""
        if self.cap:
            self.properties = {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            }

    def get_properties(self) -> dict:
        """Get video properties"""
        return self.properties.copy()

    def seek(self, frame_number: int) -> bool:
        """Seek to specific frame"""
        if self.cap:
            return self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        return False

    def get_current_frame_number(self) -> int:
        """Get current frame number"""
        return self._frame_count

    @classmethod
    def create(cls, source_config: dict) -> Optional['VideoSource']:
        """Factory method to create video source from config"""
        source_type = source_config.get('type', '').lower()

        if source_type == 'webcam':
            camera_id = source_config.get('camera_id', 0)
            return cls(camera_id)

        elif source_type == 'file':
            file_path = source_config.get('file_path', '')
            if file_path and Path(file_path).exists():
                return cls(file_path)

        elif source_type == 'rtsp':
            rtsp_url = source_config.get('rtsp_url', '')
            if rtsp_url:
                return cls(rtsp_url)

        return None