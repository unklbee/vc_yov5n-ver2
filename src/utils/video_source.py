"""
src/utils/video_source.py
Video source management for different input types
"""

import cv2
import re
from typing import Optional, Tuple
from abc import ABC, abstractmethod


class VideoSource(ABC):
    """Abstract base class for video sources"""

    def __init__(self):
        self.cap = None
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480

    @abstractmethod
    def open(self) -> bool:
        """Open the video source"""
        pass

    @abstractmethod
    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read a frame from the source"""
        pass

    def release(self):
        """Release the video source"""
        if self.cap:
            self.cap.release()

    def get_properties(self) -> dict:
        """Get video properties"""
        if not self.cap:
            return {}

        return {
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'frame_count': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'current_frame': int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        }

    def is_opened(self) -> bool:
        """Check if source is opened"""
        return self.cap is not None and self.cap.isOpened()


class WebcamSource(VideoSource):
    """Webcam video source"""

    def __init__(self, camera_id: int = 0):
        super().__init__()
        self.camera_id = camera_id

    def open(self) -> bool:
        """Open webcam"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if self.cap.isOpened():
                # Set some default properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                return True
        except Exception as e:
            print(f"❌ Error opening webcam {self.camera_id}: {e}")
        return False

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame from webcam"""
        if not self.cap:
            return False, None
        return self.cap.read()


class FileSource(VideoSource):
    """Video file source"""

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.loop = True

    def open(self) -> bool:
        """Open video file"""
        try:
            self.cap = cv2.VideoCapture(self.file_path)
            return self.cap.isOpened()
        except Exception as e:
            print(f"❌ Error opening file {self.file_path}: {e}")
        return False

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame from file"""
        if not self.cap:
            return False, None

        ret, frame = self.cap.read()

        # Loop video if enabled and reached end
        if not ret and self.loop:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        return ret, frame

    def set_loop(self, loop: bool):
        """Enable/disable video looping"""
        self.loop = loop


class RTSPSource(VideoSource):
    """RTSP stream source"""

    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.reconnect_attempts = 3
        self.current_attempts = 0

    def open(self) -> bool:
        """Open RTSP stream"""
        try:
            self.cap = cv2.VideoCapture(self.rtsp_url)

            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if self.cap.isOpened():
                self.current_attempts = 0
                return True
        except Exception as e:
            print(f"❌ Error opening RTSP stream {self.rtsp_url}: {e}")
        return False

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame from RTSP stream"""
        if not self.cap:
            return False, None

        ret, frame = self.cap.read()

        # Try to reconnect if connection lost
        if not ret and self.current_attempts < self.reconnect_attempts:
            print(f"🔄 Attempting to reconnect to RTSP stream... ({self.current_attempts + 1}/{self.reconnect_attempts})")
            self.current_attempts += 1
            self.release()
            if self.open():
                ret, frame = self.cap.read()

        return ret, frame


class VideoSourceFactory:
    """Factory for creating video sources"""

    @staticmethod
    def create_source(source_config: dict) -> Optional[VideoSource]:
        """Create video source from configuration"""
        source_type = source_config.get('type', '').lower()

        if source_type == 'webcam':
            camera_id = source_config.get('camera_id', 0)
            return WebcamSource(camera_id)

        elif source_type == 'file':
            file_path = source_config.get('file_path', '')
            if not file_path:
                return None
            source = FileSource(file_path)
            source.set_loop(source_config.get('loop', True))
            return source

        elif source_type == 'rtsp':
            rtsp_url = source_config.get('rtsp_url', '')
            if not rtsp_url:
                return None
            return RTSPSource(rtsp_url)

        else:
            # Auto-detect source type
            source_str = source_config.get('source', '')
            return VideoSourceFactory.auto_detect(source_str)

    @staticmethod
    def auto_detect(source: str) -> Optional[VideoSource]:
        """Auto-detect source type from string"""
        if not source:
            return None

        # Check if it's a number (webcam)
        if source.isdigit():
            return WebcamSource(int(source))

        # Check if it's RTSP URL
        if source.lower().startswith(('rtsp://', 'rtmp://')):
            return RTSPSource(source)

        # Check if it's HTTP stream
        if source.lower().startswith(('http://', 'https://')):
            return RTSPSource(source)

        # Otherwise assume it's a file
        return FileSource(source)