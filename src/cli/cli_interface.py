"""
src/cli/cli_interface.py
Command line interface for vehicle detection system
"""

import cv2
import argparse
import sys
import os
import time
from typing import Optional, Dict, Any

from ..core.detector import OptimizedVehicleDetector
from ..utils.video_source import VideoSourceFactory
from ..utils.config_manager import ConfigManager
from ..utils.data_manager import DataManager
from ..utils.visualizer import Visualizer


class CLIInterface:
    """Command line interface for vehicle detection"""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.config_manager = ConfigManager(args.config)

        # Override config with CLI arguments
        self._apply_cli_config()

        # Initialize components
        self.detector = None
        self.video_source = None
        self.data_manager = None
        self.visualizer = None

        # Output settings
        self.output_writer = None
        self.save_output = bool(args.output)

        print("🚗 Vehicle Detection System - CLI Mode")
        print(f"Configuration: {args.config}")

    def _apply_cli_config(self):
        """Apply CLI arguments to configuration"""
        if self.args.device:
            self.config_manager.update_detection_config(device=self.args.device)

        if self.args.model:
            self.config_manager.update_detection_config(model_path=self.args.model)

    def run(self):
        """Run CLI interface"""
        try:
            # Initialize components
            if not self._initialize_components():
                return False

            # Initialize video source
            if not self._initialize_video_source():
                return False

            # Initialize detector
            if not self._initialize_detector():
                return False

            # Initialize data manager
            self._initialize_data_manager()

            # Initialize visualizer
            self._initialize_visualizer()

            # Initialize output video writer if needed
            if self.save_output:
                self._initialize_output_writer()

            # Run main loop
            self._run_detection_loop()

            return True

        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        finally:
            self._cleanup()

    def _initialize_components(self) -> bool:
        """Initialize basic components"""
        print("🔧 Initializing components...")

        # Check if model exists
        model_path = self.config_manager.config.detection.model_path
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            return False

        return True

    def _initialize_video_source(self) -> bool:
        """Initialize video source"""
        print("📹 Initializing video source...")

        if self.args.source:
            # Create source from CLI argument
            source_config = {'source': self.args.source}
            self.video_source = VideoSourceFactory.auto_detect(self.args.source)
        else:
            print("❌ No video source specified. Use --source argument.")
            return False

        if not self.video_source:
            print("❌ Failed to create video source")
            return False

        if not self.video_source.open():
            print("❌ Failed to open video source")
            return False

        # Get and display video properties
        props = self.video_source.get_properties()
        print(f"✅ Video source opened:")
        print(f"   Resolution: {props.get('width', 'N/A')}x{props.get('height', 'N/A')}")
        print(f"   FPS: {props.get('fps', 'N/A')}")
        if 'frame_count' in props and props['frame_count'] > 0:
            print(f"   Frames: {props['frame_count']}")

        return True

    def _initialize_detector(self) -> bool:
        """Initialize vehicle detector"""
        print("🧠 Initializing detector...")

        try:
            detection_config = self.config_manager.get_detection_config()
            self.detector = OptimizedVehicleDetector(
                detection_config['model_path'],
                detection_config['device'],
                detection_config
            )
            print(f"✅ Detector initialized on {detection_config['device']}")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize detector: {str(e)}")
            return False

    def _initialize_data_manager(self):
        """Initialize data manager"""
        print("💾 Initializing data manager...")

        config_dict = {
            'data_storage': self.config_manager.config.data_storage.__dict__,
            'api': self.config_manager.config.api.__dict__
        }
        self.data_manager = DataManager(config_dict)
        print("✅ Data manager initialized")

    def _initialize_visualizer(self):
        """Initialize visualizer for CLI"""
        self.visualizer = Visualizer()
        print("✅ Visualizer initialized")

    def _initialize_output_writer(self):
        """Initialize video output writer"""
        if not self.args.output:
            return

        print(f"📼 Initializing output writer: {self.args.output}")

        # Get video properties
        props = self.video_source.get_properties()
        width = int(props.get('width', 640))
        height = int(props.get('height', 480))
        fps = props.get('fps', 30)

        # Define codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        try:
            self.output_writer = cv2.VideoWriter(
                self.args.output,
                fourcc,
                fps,
                (width, height)
            )

            if self.output_writer.isOpened():
                print(f"✅ Output writer initialized: {width}x{height} @ {fps} FPS")
            else:
                print("❌ Failed to initialize output writer")
                self.output_writer = None

        except Exception as e:
            print(f"❌ Error initializing output writer: {str(e)}")
            self.output_writer = None

    def _run_detection_loop(self):
        """Main detection loop for CLI"""
        print("🚀 Starting detection...")
        print("Press 'q' to quit, 's' to save screenshot, 'p' to pause/resume")

        frame_count = 0
        start_time = time.time()
        paused = False

        # Performance tracking
        fps_history = []
        last_stats_time = time.time()

        while True:
            if not paused:
                # Read frame
                ret, frame = self.video_source.read()
                if not ret:
                    print("📹 End of video reached")
                    break

                frame_count += 1

                # Perform detection
                detection_start = time.time()
                detections, proc_time = self.detector.detect_vehicles(frame)
                detection_time = time.time() - detection_start

                # Draw results
                result_frame = self.visualizer.draw_detections(
                    frame, detections, self.detector
                )

                # Add CLI-specific overlay
                self._add_cli_overlay(result_frame, frame_count, detection_time)

                # Save frame if output enabled
                if self.output_writer and self.output_writer.isOpened():
                    self.output_writer.write(result_frame)

                # Update data manager
                if self.data_manager:
                    stats = self.detector.get_statistics()
                    line_stats = [counter.get_statistics()
                                  for counter in self.detector.line_counters]
                    self.data_manager.add_count_data(
                        dict(self.detector.vehicle_counts),
                        stats['fps'],
                        line_stats
                    )

                # Calculate and display FPS
                fps_history.append(detection_time)
                if len(fps_history) > 30:
                    fps_history.pop(0)

                # Display periodic statistics
                current_time = time.time()
                if current_time - last_stats_time >= 10:  # Every 10 seconds
                    self._display_statistics(frame_count, start_time, fps_history)
                    last_stats_time = current_time

            # Display frame
            cv2.imshow('Vehicle Detection - CLI', result_frame if not paused else frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_screenshot(result_frame, frame_count)
            elif key == ord('p'):
                paused = not paused
                print(f"{'⏸️  Paused' if paused else '▶️  Resumed'}")
            elif key == ord('r'):
                # Reset counts
                if self.detector:
                    self.detector.vehicle_counts.clear()
                    for counter in self.detector.line_counters:
                        counter.reset_counts()
                    print("🔄 Counts reset")

        # Final statistics
        total_time = time.time() - start_time
        self._display_final_statistics(frame_count, total_time)

    def _add_cli_overlay(self, frame, frame_count: int, detection_time: float):
        """Add CLI-specific overlay information"""
        h, w = frame.shape[:2]

        # CLI mode indicator
        cv2.putText(frame, "CLI Mode", (w-100, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Frame counter
        cv2.putText(frame, f"Frame: {frame_count}", (w-150, h-50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Processing time
        cv2.putText(frame, f"Proc: {detection_time*1000:.1f}ms", (w-150, h-25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Controls help
        help_text = "Controls: 'q'=quit, 's'=screenshot, 'p'=pause, 'r'=reset"
        cv2.putText(frame, help_text, (10, h-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _save_screenshot(self, frame, frame_count: int):
        """Save current frame as screenshot"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}_frame_{frame_count}.jpg"

        try:
            cv2.imwrite(filename, frame)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to save screenshot: {str(e)}")

    def _display_statistics(self, frame_count: int, start_time: float, fps_history: list):
        """Display periodic statistics"""
        elapsed_time = time.time() - start_time
        avg_fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        if fps_history:
            processing_fps = 1.0 / (sum(fps_history) / len(fps_history))
        else:
            processing_fps = 0

        stats = self.detector.get_statistics()

        print(f"\n📊 Statistics (Frame {frame_count}):")
        print(f"   Runtime: {elapsed_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Processing FPS: {processing_fps:.1f}")
        print(f"   Detection FPS: {stats['fps']:.1f}")

        # Vehicle counts
        total_vehicles = 0
        print(f"   Vehicle Counts:")
        for vehicle_type, counts in self.detector.vehicle_counts.items():
            up_count = counts['up']
            down_count = counts['down']
            total_vehicles += up_count + down_count
            print(f"     {vehicle_type.capitalize()}: ↑{up_count} ↓{down_count}")

        print(f"   Total Detected: {total_vehicles}")
        print("-" * 50)

    def _display_final_statistics(self, frame_count: int, total_time: float):
        """Display final statistics"""
        print(f"\n🏁 Final Statistics:")
        print(f"   Total Frames: {frame_count}")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Average FPS: {frame_count/total_time:.2f}")

        # Final vehicle counts
        total_vehicles = 0
        print(f"   Final Vehicle Counts:")
        for vehicle_type, counts in self.detector.vehicle_counts.items():
            up_count = counts['up']
            down_count = counts['down']
            total_vehicles += up_count + down_count
            print(f"     {vehicle_type.capitalize()}: ↑{up_count} ↓{down_count} (Total: {up_count + down_count})")

        print(f"   Grand Total: {total_vehicles}")

        # Data manager statistics
        if self.data_manager:
            dm_stats = self.data_manager.get_statistics()
            print(f"   Data Buffer: {dm_stats['buffer_size']} records")
            print(f"   Storage: {'Enabled' if dm_stats['storage_enabled'] else 'Disabled'}")
            print(f"   API: {'Enabled' if dm_stats['api_enabled'] else 'Disabled'}")

    def _cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")

        try:
            # Release video source
            if self.video_source:
                self.video_source.release()

            # Release output writer
            if self.output_writer:
                self.output_writer.release()

            # Stop data manager
            if self.data_manager:
                self.data_manager.stop()

            # Close OpenCV windows
            cv2.destroyAllWindows()

            # Save configuration
            self.config_manager.save_config()

            print("✅ Cleanup completed")

        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")


def mouse_callback_cli(event, x, y, flags, param):
    """Mouse callback for CLI mode ROI and line drawing"""
    detector = param['detector']
    frame = param['frame']
    interface = param['interface']

    if event == cv2.EVENT_LBUTTONDOWN:
        if interface.drawing_mode == 'roi':
            detector.roi_points.append((x, y))
            print(f"ROI point {len(detector.roi_points)}: ({x}, {y})")
        elif interface.drawing_mode == 'line':
            detector.temp_line_points.append((x, y))
            print(f"Line point {len(detector.temp_line_points)}: ({x}, {y})")

            if len(detector.temp_line_points) == 2:
                detector.add_counting_line(detector.temp_line_points[0],
                                           detector.temp_line_points[1])
                detector.temp_line_points = []
                interface.drawing_mode = None
                print("✅ Line completed")

    elif event == cv2.EVENT_RBUTTONDOWN:
        if interface.drawing_mode == 'roi' and len(detector.roi_points) >= 3:
            detector.set_roi_from_points(detector.roi_points, frame.shape)
            interface.drawing_mode = None
            print("✅ ROI completed")


class CLIDrawingMode:
    """Enhanced CLI interface with drawing capabilities"""

    def __init__(self, args: argparse.Namespace):
        self.base_interface = CLIInterface(args)
        self.drawing_mode = None  # None, 'roi', 'line'

    def run(self):
        """Run CLI with drawing capabilities"""
        # Initialize base interface
        if not self.base_interface._initialize_components():
            return False

        if not self.base_interface._initialize_video_source():
            return False

        if not self.base_interface._initialize_detector():
            return False

        self.base_interface._initialize_data_manager()
        self.base_interface._initialize_visualizer()

        if self.base_interface.save_output:
            self.base_interface._initialize_output_writer()

        # Setup mouse callback for drawing
        cv2.namedWindow('Vehicle Detection - CLI')
        mouse_params = {
            'detector': self.base_interface.detector,
            'frame': None,
            'interface': self
        }
        cv2.setMouseCallback('Vehicle Detection - CLI', mouse_callback_cli, mouse_params)

        print("🎯 Enhanced CLI Mode with Drawing")
        print("Additional Controls:")
        print("  'o' = Start ROI drawing")
        print("  'l' = Start line drawing")
        print("  'c' = Clear ROI and lines")

        try:
            self._run_enhanced_loop(mouse_params)
            return True
        except KeyboardInterrupt:
            print("\n🛑 Detection stopped by user")
            return True
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        finally:
            self.base_interface._cleanup()

    def _run_enhanced_loop(self, mouse_params):
        """Enhanced detection loop with drawing"""
        frame_count = 0
        start_time = time.time()
        paused = False

        while True:
            if not paused:
                ret, frame = self.base_interface.video_source.read()
                if not ret:
                    print("📹 End of video reached")
                    break

                frame_count += 1
                mouse_params['frame'] = frame

                # Perform detection
                detection_start = time.time()
                detections, proc_time = self.base_interface.detector.detect_vehicles(frame)
                detection_time = time.time() - detection_start

                # Draw results
                result_frame = self.base_interface.visualizer.draw_detections(
                    frame, detections, self.base_interface.detector
                )

                # Add drawing indicators
                self._add_drawing_overlay(result_frame)

                # Add CLI overlay
                self.base_interface._add_cli_overlay(result_frame, frame_count, detection_time)

                # Save frame if output enabled
                if (self.base_interface.output_writer and
                        self.base_interface.output_writer.isOpened()):
                    self.base_interface.output_writer.write(result_frame)

            # Display frame
            cv2.imshow('Vehicle Detection - CLI', result_frame if not paused else frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.base_interface._save_screenshot(result_frame, frame_count)
            elif key == ord('p'):
                paused = not paused
                print(f"{'⏸️  Paused' if paused else '▶️  Resumed'}")
            elif key == ord('o'):
                self._start_roi_drawing()
            elif key == ord('l'):
                self._start_line_drawing()
            elif key == ord('c'):
                self._clear_annotations()

        # Final statistics
        total_time = time.time() - start_time
        self.base_interface._display_final_statistics(frame_count, total_time)

    def _add_drawing_overlay(self, frame):
        """Add drawing mode overlay"""
        if self.drawing_mode:
            h, w = frame.shape[:2]
            if self.drawing_mode == 'roi':
                text = "Drawing ROI - Left click: add point, Right click: finish"
                color = (0, 255, 0)
            elif self.drawing_mode == 'line':
                text = "Drawing Line - Click two points"
                color = (0, 255, 255)

            cv2.putText(frame, text, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    def _start_roi_drawing(self):
        """Start ROI drawing mode"""
        self.drawing_mode = 'roi'
        self.base_interface.detector.roi_points = []
        print("🎯 ROI drawing mode activated")

    def _start_line_drawing(self):
        """Start line drawing mode"""
        self.drawing_mode = 'line'
        self.base_interface.detector.temp_line_points = []
        print("📏 Line drawing mode activated")

    def _clear_annotations(self):
        """Clear all annotations"""
        self.base_interface.detector.clear_roi_and_lines()
        self.drawing_mode = None
        print("🗑️ Cleared all ROI and lines")