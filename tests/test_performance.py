## 8. Performance Test Suite (`tests/test_performance.py`)

"""
Performance test suite
"""
import pytest
import time
import numpy as np
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.detector import VehicleDetector
from src.utils.config import ConfigManager
from src.utils.performance import PerformanceMonitor, AdaptivePerformanceManager

class TestPerformance:
    """Performance test cases"""

    @pytest.fixture
    def detector(self):
        """Create detector for testing"""
        config = {'model_path': 'dummy.xml', 'device': 'CPU'}
        return VehicleDetector('dummy.xml', config)

    @pytest.fixture
    def test_frame(self):
        """Create test frame"""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def test_detection_speed(self, detector, test_frame):
        """Test detection speed meets minimum requirements"""
        # Warm up
        for _ in range(5):
            detector.detect(test_frame)

        # Measure performance
        times = []
        for _ in range(20):
            start = time.time()
            detector.detect(test_frame)
            times.append(time.time() - start)

        avg_time = sum(times) / len(times)
        fps = 1.0 / avg_time

        # Assert minimum performance
        assert fps >= 10.0, f"Detection too slow: {fps:.1f} FPS"
        assert avg_time <= 0.1, f"Detection time too high: {avg_time*1000:.1f}ms"

    def test_memory_usage(self, detector, test_frame):
        """Test memory usage stays within bounds"""
        import psutil
        import gc

        # Get baseline memory
        gc.collect()
        baseline_memory = psutil.virtual_memory().percent

        # Run detection loop
        for _ in range(100):
            detector.detect(test_frame)

        # Check memory after
        current_memory = psutil.virtual_memory().percent
        memory_increase = current_memory - baseline_memory

        # Assert memory usage is reasonable
        assert memory_increase < 5.0, f"Memory usage increased by {memory_increase:.1f}%"

    def test_performance_monitor(self):
        """Test performance monitoring"""
        monitor = PerformanceMonitor(window_size=10)

        # Simulate some frame processing
        for i in range(15):
            monitor.update_frame_metrics(
                frame_time=0.03,  # 33ms = ~30 FPS
                detection_time=0.02,
                rendering_time=0.01
            )
            time.sleep(0.01)

        # Check metrics
        current = monitor.get_current_metrics()
        assert current.fps > 0
        assert current.frame_time > 0

        averages = monitor.get_average_metrics()
        assert 'avg_fps' in averages
        assert averages['avg_fps'] > 0

        summary = monitor.get_performance_summary()
        assert 'current' in summary
        assert 'averages' in summary
        assert 'fps_stats' in summary

        monitor.stop()

    def test_adaptive_performance(self):
        """Test adaptive performance management"""
        manager = AdaptivePerformanceManager(target_fps=30.0)

        # Simulate low performance scenario
        with patch.object(manager.monitor, 'get_current_metrics') as mock_metrics:
            mock_metrics.return_value = Mock(
                fps=15.0,  # Below target
                cpu_usage=85.0,  # High CPU
                memory_usage=70.0
            )

            adjustments = manager.should_adjust_performance()
            assert adjustments.get('increase_frame_skip', False)
            assert adjustments.get('reduce_input_size', False)

        # Test config optimization
        base_config = {
            'frame_skip': 1,
            'input_shape': [416, 416]
        }

        optimized_config = manager.get_optimized_config(base_config)
        assert 'frame_skip' in optimized_config
        assert 'input_shape' in optimized_config

    @pytest.mark.slow
    def test_sustained_performance(self, detector, test_frame):
        """Test performance over sustained period"""
        duration = 10  # 10 seconds
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < duration:
            detector.detect(test_frame)
            frame_count += 1

        actual_duration = time.time() - start_time
        avg_fps = frame_count / actual_duration

        # Assert sustained performance
        assert avg_fps >= 8.0, f"Sustained FPS too low: {avg_fps:.1f}"
        assert frame_count >= 80, f"Too few frames processed: {frame_count}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])