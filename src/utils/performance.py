## 1. Advanced Performance Monitor (`src/utils/performance.py`)

"""
Advanced performance monitoring and optimization
"""
import time
import psutil
import threading
from collections import deque
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    fps: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    gpu_usage: float = 0.0
    frame_time: float = 0.0
    detection_time: float = 0.0
    tracking_time: float = 0.0
    rendering_time: float = 0.0

class PerformanceMonitor:
    """Advanced performance monitoring"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics_history = deque(maxlen=window_size)
        self.start_time = time.time()
        self.last_update = time.time()

        # Monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()

        # Current metrics
        self.current_metrics = PerformanceMetrics()

    def _monitor_system(self):
        """Background system monitoring"""
        while self.monitoring:
            try:
                # CPU and Memory
                self.current_metrics.cpu_usage = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                self.current_metrics.memory_usage = memory.percent

                # GPU (if available)
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        self.current_metrics.gpu_usage = gpus[0].load * 100
                except ImportError:
                    pass

                time.sleep(1)  # Update every second

            except Exception as e:
                print(f"Performance monitoring error: {e}")

    def update_frame_metrics(self, frame_time: float, detection_time: float = 0.0,
                             tracking_time: float = 0.0, rendering_time: float = 0.0):
        """Update frame-specific metrics"""
        current_time = time.time()

        # Calculate FPS
        time_diff = current_time - self.last_update
        self.current_metrics.fps = 1.0 / time_diff if time_diff > 0 else 0.0

        # Update timing metrics
        self.current_metrics.frame_time = frame_time
        self.current_metrics.detection_time = detection_time
        self.current_metrics.tracking_time = tracking_time
        self.current_metrics.rendering_time = rendering_time

        # Store in history
        self.metrics_history.append(asdict(self.current_metrics))

        self.last_update = current_time

    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.current_metrics

    def get_average_metrics(self, window: int = None) -> Dict[str, float]:
        """Get average metrics over specified window"""
        if not self.metrics_history:
            return {}

        window_size = min(window or self.window_size, len(self.metrics_history))
        recent_metrics = list(self.metrics_history)[-window_size:]

        # Calculate averages
        averages = {}
        for key in recent_metrics[0].keys():
            values = [m[key] for m in recent_metrics if m[key] is not None]
            averages[f"avg_{key}"] = sum(values) / len(values) if values else 0.0

        return averages

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.metrics_history:
            return {}

        current = asdict(self.current_metrics)
        averages = self.get_average_metrics()

        # Calculate additional stats
        fps_values = [m['fps'] for m in self.metrics_history if m['fps'] > 0]

        return {
            'current': current,
            'averages': averages,
            'fps_stats': {
                'min': min(fps_values) if fps_values else 0,
                'max': max(fps_values) if fps_values else 0,
                'avg': sum(fps_values) / len(fps_values) if fps_values else 0
            },
            'uptime': time.time() - self.start_time,
            'total_frames': len(self.metrics_history)
        }

    def stop(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)

class AdaptivePerformanceManager:
    """Adaptive performance management"""

    def __init__(self, target_fps: float = 30.0):
        self.target_fps = target_fps
        self.monitor = PerformanceMonitor()

        # Adaptive settings
        self.frame_skip = 1
        self.input_size_scale = 1.0
        self.min_input_size = 320
        self.max_input_size = 640

        # Performance thresholds
        self.low_fps_threshold = target_fps * 0.7
        self.high_cpu_threshold = 80.0
        self.high_memory_threshold = 85.0

    def should_adjust_performance(self) -> Dict[str, Any]:
        """Check if performance adjustments are needed"""
        metrics = self.monitor.get_current_metrics()
        adjustments = {}

        # FPS too low
        if metrics.fps < self.low_fps_threshold:
            adjustments['increase_frame_skip'] = True
            adjustments['reduce_input_size'] = True

        # CPU usage too high
        if metrics.cpu_usage > self.high_cpu_threshold:
            adjustments['increase_frame_skip'] = True

        # Memory usage too high
        if metrics.memory_usage > self.high_memory_threshold:
            adjustments['reduce_trail_length'] = True
            adjustments['reduce_buffer_size'] = True

        # Good performance - can improve quality
        if (metrics.fps > self.target_fps * 1.2 and
                metrics.cpu_usage < 60 and
                metrics.memory_usage < 70):
            adjustments['decrease_frame_skip'] = True
            adjustments['increase_input_size'] = True

        return adjustments

    def get_optimized_config(self, base_config: Dict) -> Dict:
        """Get performance-optimized configuration"""
        config = base_config.copy()
        adjustments = self.should_adjust_performance()

        # Adjust frame skip
        if adjustments.get('increase_frame_skip'):
            config['frame_skip'] = min(config.get('frame_skip', 1) + 1, 5)
        elif adjustments.get('decrease_frame_skip'):
            config['frame_skip'] = max(config.get('frame_skip', 1) - 1, 1)

        # Adjust input size
        current_size = config.get('input_shape', [416, 416])[0]

        if adjustments.get('reduce_input_size'):
            new_size = max(current_size - 32, self.min_input_size)
            config['input_shape'] = [new_size, new_size]
        elif adjustments.get('increase_input_size'):
            new_size = min(current_size + 32, self.max_input_size)
            config['input_shape'] = [new_size, new_size]

        return config