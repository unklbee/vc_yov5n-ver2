## 2. CLI Interface (`src/cli/interface.py`)

"""Optimized CLI interface"""
import cv2
import time
import signal
from pathlib import Path

from ..core.detector import VehicleDetector
from ..utils.video_source import VideoSource
from ..utils.config import ConfigManager
from ..utils.visualizer import Visualizer

class CLIInterface:
    """Lightweight CLI interface"""

    def __init__(self, args):
        self.args = args
        self.config_manager = ConfigManager(args.config)
        self.detector = None
        self.video_source = None
        self.output_writer = None
        self.running = True

        # Apply CLI arguments to config
        if args.device:
            self.config_manager.update_detection(device=args.device)
        if args.model:
            self.config_manager.update_detection(model_path=args.model)

        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle interrupt signal"""
        print("\n🛑 Stopping detection...")
        self.running = False

    def run(self) -> bool:
        """Run CLI interface"""
        try:
            print("🚀 Initializing CLI interface...")

            # Initialize video source
            if not self._init_video_source():
                return False

            # Initialize detector
            if not self._init_detector():
                return False

            # Initialize output writer if needed
            if self.args.output:
                self._init_output_writer()

            # Run detection loop
            self._run_detection_loop()

            return True

        except Exception as e:
            print(f"❌ CLI error: {e}")
            return False
        finally:
            self._cleanup()

    def _init_video_source(self) -> bool:
        """Initialize video source"""
        source = self.args.source

        # Auto-detect source type
        if source.isdigit():
            config = {'type': 'webcam', 'camera_id': int(source)}
        elif source.startswith(('rtsp://', 'http://', 'https://')):
            config = {'type': 'rtsp', 'rtsp_url': source}
        else:
            if not Path(source).exists():
                print(f"❌ Video file not found: {source}")
                return False
            config = {'type': 'file', 'file_path': source}

        self.video_source = VideoSource.create(config)

        if not self.video_source or not self.video_source.open():
            print("❌ Failed to open video source")
            return False

        # Display video info
        props = self.video_source.get_properties()
        print(f"✅ Video source opened:")
        print(f"   Resolution: {props.get('width', 'N/A')}x{props.get('height', 'N/A')}")
        print(f"   FPS: {props.get('fps', 'N/A')}")

        return True

    def _init_detector(self) -> bool:
        """Initialize detector"""
        try:
            config = self.config_manager.get_detection_dict()
            self.detector = VehicleDetector(config['model_path'], config)
            print(f"✅ Detector initialized on {config['device']}")
            return True
        except Exception as e:
            print(f"❌ Detector initialization failed: {e}")
            return False

    def _init_output_writer(self):
        """Initialize output video writer"""
        try:
            props = self.video_source.get_properties()
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')

            self.output_writer = cv2.VideoWriter(
                self.args.output,
                fourcc,
                props.get('fps', 30),
                (props.get('width', 640), props.get('height', 480))
            )
            print(f"✅ Output writer initialized: {self.args.output}")
        except Exception as e:
            print(f"⚠️ Output writer initialization failed: {e}")

    def _run_detection_loop(self):
        """Main detection loop"""
        print("\n🎬 Starting detection...")
        print("Press 'q' to quit, 's' to save screenshot, SPACE to pause")

        frame_count = 0
        start_time = time.time()
        paused = False

        # Create window
        cv2.namedWindow('Vehicle Detection - CLI', cv2.WINDOW_RESIZABLE)

        while self.running:
            if not paused:
                # Read frame
                ret, frame = self.video_source.read()
                if not ret:
                    print("📹 End of video reached")
                    break

                frame_count += 1

                # Run detection
                detections, stats = self.detector.detect(frame)

                # Draw results
                result_frame = Visualizer.draw_detections(frame, detections, stats)

                # Add CLI overlay
                self._add_cli_overlay(result_frame, frame_count, stats)

                # Save frame if output enabled
                if self.output_writer:
                    self.output_writer.write(result_frame)

                # Display frame
                cv2.imshow('Vehicle Detection - CLI', result_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('s'):
                self._save_screenshot(result_frame, frame_count)
            elif key == ord(' '):  # SPACE
                paused = not paused
                print(f"{'⏸️ Paused' if paused else '▶️ Resumed'}")

        # Show final statistics
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0

        print(f"\n📊 Final Statistics:")
        print(f"   Frames processed: {frame_count}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average FPS: {avg_fps:.2f}")

    def _add_cli_overlay(self, frame, frame_count: int, stats: dict):
        """Add CLI-specific overlay"""
        h, w = frame.shape[:2]

        # CLI indicator
        cv2.putText(frame, "CLI Mode", (w-120, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (10, h-50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Controls help
        cv2.putText(frame, "Controls: 'q'=quit, 's'=screenshot, SPACE=pause",
                    (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _save_screenshot(self, frame, frame_count: int):
        """Save screenshot"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_frame_{frame_count}.jpg"

        try:
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Screenshot save failed: {e}")

    def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")

        try:
            if self.video_source:
                self.video_source.release()

            if self.output_writer:
                self.output_writer.release()

            cv2.destroyAllWindows()

            # Save configuration
            self.config_manager.save()

        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

def run_cli(args) -> bool:
    """Run CLI interface"""
    interface = CLIInterface(args)
    return interface.run()
