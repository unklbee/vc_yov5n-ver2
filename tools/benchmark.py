## 5. Benchmark Tool (`tools/benchmark.py`)

#!/usr/bin/env python3
"""
Benchmark tool for performance testing
"""
import sys
import time
import statistics
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import ConfigManager
from src.core.detector import VehicleDetector
from src.utils.video_source import VideoSource
from src.utils.performance import PerformanceMonitor
import numpy as np

class Benchmark:
    """Performance benchmark tool"""

    def __init__(self, config_path: str = "config/default.yaml"):
        self.config_manager = ConfigManager(config_path)
        self.performance_monitor = PerformanceMonitor()

    def benchmark_detection_speed(self, num_frames: int = 100) -> Dict[str, float]:
        """Benchmark detection speed"""
        print(f"🔬 Benchmarking detection speed ({num_frames} frames)...")

        # Create detector
        config = self.config_manager.get_detection_dict()
        detector = VehicleDetector(config['model_path'], config)

        # Create dummy frames
        frame_shape = (480, 640, 3)
        frames = [np.random.randint(0, 255, frame_shape, dtype=np.uint8)
                  for _ in range(num_frames)]

        # Warm up
        for _ in range(10):
            detector.detect(frames[0])

        # Benchmark
        times = []
        start_time = time.time()

        for frame in frames:
            frame_start = time.time()
            detections, stats = detector.detect(frame)
            frame_time = time.time() - frame_start
            times.append(frame_time)

        total_time = time.time() - start_time

        return {
            'total_time': total_time,
            'avg_frame_time': statistics.mean(times),
            'min_frame_time': min(times),
            'max_frame_time': max(times),
            'fps': num_frames / total_time,
            'frames_processed': num_frames
        }

    def benchmark_memory_usage(self, duration: int = 60) -> Dict[str, float]:
        """Benchmark memory usage over time"""
        print(f"🧠 Benchmarking memory usage ({duration}s)...")

        import psutil

        # Create detector and video source
        config = self.config_manager.get_detection_dict()
        detector = VehicleDetector(config['model_path'], config)

        # Create dummy video source
        frame_shape = (480, 640, 3)

        memory_samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            # Generate and process frame
            frame = np.random.randint(0, 255, frame_shape, dtype=np.uint8)
            detections, stats = detector.detect(frame)

            # Sample memory usage
            memory = psutil.virtual_memory()
            memory_samples.append(memory.percent)

            time.sleep(0.1)  # 10 FPS simulation

        return {
            'avg_memory': statistics.mean(memory_samples),
            'max_memory': max(memory_samples),
            'min_memory': min(memory_samples),
            'memory_growth': memory_samples[-1] - memory_samples[0],
            'samples': len(memory_samples)
        }

    def benchmark_full_pipeline(self, video_path: str = None, duration: int = 30) -> Dict[str, Any]:
        """Benchmark complete pipeline"""
        print(f"🎬 Benchmarking full pipeline ({duration}s)...")

        # Create components
        config = self.config_manager.get_detection_dict()
        detector = VehicleDetector(config['model_path'], config)

        if video_path:
            video_source = VideoSource.create({'type': 'file', 'file_path': video_path})
        else:
            video_source = VideoSource.create({'type': 'webcam', 'camera_id': 0})

        if not video_source.open():
            print("❌ Failed to open video source")
            return {}

        # Benchmark
        frame_count = 0
        detection_times = []
        fps_values = []

        start_time = time.time()

        while time.time() - start_time < duration:
            ret, frame = video_source.read()
            if not ret:
                break

            # Process frame
            frame_start = time.time()
            detections, stats = detector.detect(frame)
            detection_time = time.time() - frame_start

            detection_times.append(detection_time)
            fps_values.append(stats.get('fps', 0))
            frame_count += 1

        video_source.release()

        actual_duration = time.time() - start_time

        return {
            'duration': actual_duration,
            'frames_processed': frame_count,
            'avg_fps': frame_count / actual_duration,
            'detector_fps': statistics.mean(fps_values) if fps_values else 0,
            'avg_detection_time': statistics.mean(detection_times),
            'max_detection_time': max(detection_times) if detection_times else 0,
            'min_detection_time': min(detection_times) if detection_times else 0
        }

    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("🚀 Running complete benchmark suite...")

        results = {}

        try:
            # Detection speed benchmark
            results['detection_speed'] = self.benchmark_detection_speed()

            # Memory usage benchmark
            results['memory_usage'] = self.benchmark_memory_usage(30)

            # Full pipeline benchmark
            results['full_pipeline'] = self.benchmark_full_pipeline(duration=20)

            # System info
            import psutil
            results['system_info'] = {
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'python_version': sys.version
            }

        except Exception as e:
            print(f"❌ Benchmark error: {e}")
            results['error'] = str(e)

        return results

    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results"""
        print("\n" + "="*60)
        print("📊 BENCHMARK RESULTS")
        print("="*60)

        if 'detection_speed' in results:
            speed = results['detection_speed']
            print(f"\n🔬 Detection Speed:")
            print(f"   Average FPS: {speed['fps']:.1f}")
            print(f"   Average frame time: {speed['avg_frame_time']*1000:.1f}ms")
            print(f"   Min frame time: {speed['min_frame_time']*1000:.1f}ms")
            print(f"   Max frame time: {speed['max_frame_time']*1000:.1f}ms")

        if 'memory_usage' in results:
            memory = results['memory_usage']
            print(f"\n🧠 Memory Usage:")
            print(f"   Average: {memory['avg_memory']:.1f}%")
            print(f"   Peak: {memory['max_memory']:.1f}%")
            print(f"   Growth: {memory['memory_growth']:.1f}%")

        if 'full_pipeline' in results:
            pipeline = results['full_pipeline']
            print(f"\n🎬 Full Pipeline:")
            print(f"   Real-time FPS: {pipeline['avg_fps']:.1f}")
            print(f"   Detector FPS: {pipeline['detector_fps']:.1f}")
            print(f"   Frames processed: {pipeline['frames_processed']}")
            print(f"   Average detection time: {pipeline['avg_detection_time']*1000:.1f}ms")

        if 'system_info' in results:
            system = results['system_info']
            print(f"\n💻 System Info:")
            print(f"   CPU cores: {system['cpu_count']}")
            print(f"   Total RAM: {system['memory_total_gb']:.1f} GB")

        print("\n" + "="*60)

def main():
    """Main benchmark function"""
    import argparse

    parser = argparse.ArgumentParser(description="Vehicle Detection Benchmark Tool")
    parser.add_argument("--config", default="config/default.yaml", help="Config file")
    parser.add_argument("--detection-only", action="store_true", help="Run detection benchmark only")
    parser.add_argument("--memory-only", action="store_true", help="Run memory benchmark only")
    parser.add_argument("--video", help="Video file for testing")
    parser.add_argument("--frames", type=int, default=100, help="Number of frames for detection test")
    parser.add_argument("--duration", type=int, default=30, help="Duration in seconds")

    args = parser.parse_args()

    # Create benchmark
    benchmark = Benchmark(args.config)

    try:
        if args.detection_only:
            results = {'detection_speed': benchmark.benchmark_detection_speed(args.frames)}
        elif args.memory_only:
            results = {'memory_usage': benchmark.benchmark_memory_usage(args.duration)}
        else:
            results = benchmark.run_full_benchmark()

        # Print results
        benchmark.print_results(results)

        # Save results to file
        import json
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"benchmark_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {results_file}")

    except KeyboardInterrupt:
        print("\n🛑 Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")

if __name__ == "__main__":
    main()