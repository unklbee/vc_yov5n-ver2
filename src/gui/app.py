"""
Fixed src/gui/app.py - Proper Utils Integration
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction

# FIXED IMPORTS - Absolute imports dengan proper error handling
try:
    from src.gui.widgets.video import VideoWidget
    from src.gui.widgets.controls import ControlWidget
    from src.gui.widgets.stats import StatsWidget
    from src.gui.styles import apply_dark_theme
    print("✅ GUI widgets imported successfully")
except ImportError as e:
    print(f"❌ GUI widgets import error: {e}")
    sys.exit(1)

try:
    from src.core.detector import VehicleDetector
    print("✅ VehicleDetector imported successfully")
except ImportError as e:
    print(f"❌ VehicleDetector import error: {e}")
    sys.exit(1)

try:
    from src.utils.video_source import VideoSource
    from src.utils.config import ConfigManager
    from src.utils.visualizer import Visualizer
    print("✅ Utils modules imported successfully")
except ImportError as e:
    print(f"❌ Utils import error: {e}")
    print("Creating minimal fallback implementations...")

    # Fallback minimal implementations
    class VideoSource:
        @classmethod
        def create(cls, config):
            return None

    class ConfigManager:
        def __init__(self, path=None):
            self.config = type('Config', (), {
                'detection': type('Detection', (), {
                    'model_path': 'dummy.xml',
                    'device': 'CPU'
                })()
            })()

        def get_detection_dict(self):
            return {'model_path': 'dummy.xml', 'device': 'CPU'}

        def save(self):
            pass

    class Visualizer:
        @staticmethod
        def draw_detections(frame, detections, stats):
            return frame


class MainWindow(QMainWindow):
    """Fixed main window dengan proper utils integration"""

    def __init__(self, config_path: str = None):
        super().__init__()

        print("🚀 MainWindow: Initializing...")

        # Initialize managers
        self.timer = None
        self.status_bar = None
        self.stats_widget = None
        self.video_widget = None
        self.control_widget = None

        # FIXED: Proper config manager initialization
        try:
            self.config_manager = ConfigManager(config_path)
            print("✅ ConfigManager initialized")
        except Exception as e:
            print(f"❌ ConfigManager error: {e}")
            self.config_manager = ConfigManager()  # Fallback

        self.detector = None
        self.video_source = None

        # State
        self.is_running = False

        # Setup
        self.setup_ui()
        self.setup_menu()
        self.setup_timer()
        self.connect_signals()

        # Apply theme
        apply_dark_theme(self)

        print("✅ MainWindow: Initialization complete")

    def setup_ui(self):
        """Setup user interface"""
        print("🔧 MainWindow: Setting up UI...")

        self.setWindowTitle("Vehicle Detection System")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Create widgets
        try:
            self.control_widget = ControlWidget(self.config_manager)
            print("✅ ControlWidget created")
        except Exception as e:
            print(f"❌ ControlWidget error: {e}")
            self.control_widget = QWidget()  # Fallback

        try:
            self.video_widget = VideoWidget()
            print("✅ VideoWidget created")
        except Exception as e:
            print(f"❌ VideoWidget error: {e}")
            self.video_widget = QWidget()  # Fallback

        try:
            self.stats_widget = StatsWidget()
            print("✅ StatsWidget created")
        except Exception as e:
            print(f"❌ StatsWidget error: {e}")
            self.stats_widget = QWidget()  # Fallback

        # Add to splitter
        splitter.addWidget(self.control_widget)
        splitter.addWidget(self.video_widget)
        splitter.addWidget(self.stats_widget)

        # Set proportions: control(300) : video(flexible) : stats(300)
        splitter.setSizes([300, 800, 300])
        splitter.setStretchFactor(1, 1)  # Video widget stretches

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        print("✅ MainWindow: UI setup complete")

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        open_action = QAction('&Open Video...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_video_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        reset_view_action = QAction('&Reset View', self)
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_view_action)

    def setup_timer(self):
        """Setup processing timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.setSingleShot(False)

    def connect_signals(self):
        """Connect widget signals"""
        print("🔧 MainWindow: Connecting signals...")

        try:
            # Control widget signals
            if hasattr(self.control_widget, 'start_detection'):
                self.control_widget.start_detection.connect(self.toggle_detection)
                print("✅ start_detection signal connected")

            if hasattr(self.control_widget, 'source_changed'):
                self.control_widget.source_changed.connect(self.load_video_source)
                print("✅ source_changed signal connected")

            if hasattr(self.control_widget, 'device_changed'):
                self.control_widget.device_changed.connect(self.change_device)
                print("✅ device_changed signal connected")

            # Video widget signals
            if hasattr(self.video_widget, 'roi_drawn'):
                self.video_widget.roi_drawn.connect(self.set_roi)
                print("✅ roi_drawn signal connected")

            if hasattr(self.video_widget, 'line_drawn'):
                self.video_widget.line_drawn.connect(self.add_counting_line)
                print("✅ line_drawn signal connected")

            if hasattr(self.video_widget, 'annotations_cleared'):
                self.video_widget.annotations_cleared.connect(self.clear_annotations)
                print("✅ annotations_cleared signal connected")

        except Exception as e:
            print(f"❌ Signal connection error: {e}")

    def open_video_file(self):
        """Open video file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv *.wmv);;All Files (*)"
        )

        if file_path:
            config = {
                'type': 'file',
                'file_path': file_path
            }
            self.load_video_source(config)

    def load_video_source(self, source_config: dict):
        """Load video source"""
        print(f"🔧 Loading video source: {source_config}")

        try:
            # Stop current detection
            if self.is_running:
                self.toggle_detection()

            # Release old source
            if self.video_source:
                self.video_source.release()

            # Create new source
            self.video_source = VideoSource.create(source_config)

            if self.video_source and self.video_source.open():
                # Show first frame
                ret, frame = self.video_source.read()
                if ret and hasattr(self.video_widget, 'update_frame'):
                    self.video_widget.update_frame(frame)
                    self.status_bar.showMessage(f"Loaded: {source_config.get('type', 'Unknown')}")

                    # Update video info
                    props = self.video_source.get_properties()
                    if hasattr(self.stats_widget, 'update_video_info'):
                        self.stats_widget.update_video_info(props)
                    print("✅ Video source loaded successfully")
                else:
                    raise Exception("Failed to read first frame")
            else:
                raise Exception("Failed to open video source")

        except Exception as e:
            print(f"❌ Video source loading error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load video source:\n{str(e)}")

    def toggle_detection(self):
        """Toggle detection on/off"""
        if not self.video_source:
            QMessageBox.warning(self, "Warning", "Please load a video source first")
            return

        if self.is_running:
            self.stop_detection()
        else:
            self.start_detection()

    def start_detection(self):
        """Start detection"""
        print("🚀 Starting detection...")

        try:
            # Initialize detector if needed
            if not self.detector:
                config = self.config_manager.get_detection_dict()
                self.detector = VehicleDetector(config['model_path'], config)
                print("✅ Detector initialized")

            # Start processing
            self.timer.start(33)  # ~30 FPS
            self.is_running = True

            # Update UI
            if hasattr(self.control_widget, 'set_detection_state'):
                self.control_widget.set_detection_state(True)
            self.status_bar.showMessage("Detection running...")

            print("✅ Detection started")

        except Exception as e:
            print(f"❌ Detection start error: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start detection:\n{str(e)}")

    def stop_detection(self):
        """Stop detection"""
        print("🛑 Stopping detection...")

        self.timer.stop()
        self.is_running = False

        # Update UI
        if hasattr(self.control_widget, 'set_detection_state'):
            self.control_widget.set_detection_state(False)
        self.status_bar.showMessage("Detection stopped")

    def process_frame(self):
        """Process single frame - FIXED"""
        if not self.video_source or not self.detector:
            return

        try:
            # Read frame
            ret, frame = self.video_source.read()
            if not ret:
                # End of video - loop if it's a file
                if hasattr(self.video_source, 'seek'):
                    self.video_source.seek(0)
                    ret, frame = self.video_source.read()

                if not ret:
                    self.stop_detection()
                    return

            # FIXED: Run detection with proper error handling
            detections, stats = self.detector.detect(frame)

            # Debug output
            fps = stats.get('fps', 0)
            detection_count = len(detections)
            total_crossings = stats.get('total_crossings', 0)

            # Only print occasionally to avoid spam
            if self.video_source.get_current_frame_number() % 30 == 0:
                print(f"📊 Frame {self.video_source.get_current_frame_number()}: "
                      f"FPS={fps:.1f}, Det={detection_count}, Cross={total_crossings}")

            # FIXED: Draw results with proper error handling
            try:
                result_frame = Visualizer.draw_detections(frame, detections, stats)
            except Exception as e:
                print(f"❌ Visualization error: {e}")
                result_frame = frame  # Fallback to original frame

            # FIXED: Update displays with proper error handling
            if hasattr(self.video_widget, 'update_frame'):
                try:
                    self.video_widget.update_frame(result_frame)
                except Exception as e:
                    print(f"❌ Video widget update error: {e}")

            if hasattr(self.stats_widget, 'update_detection_stats'):
                try:
                    self.stats_widget.update_detection_stats(stats, detections)
                except Exception as e:
                    print(f"❌ Stats widget update error: {e}")

            # Update status
            frame_num = self.video_source.get_current_frame_number()
            self.status_bar.showMessage(
                f"FPS: {fps:.1f} | Detections: {detection_count} | "
                f"Crossings: {total_crossings} | Frame: {frame_num}"
            )

        except Exception as e:
            print(f"❌ Frame processing error: {e}")
            # Don't stop detection for single frame errors
            # self.stop_detection()

    def change_device(self, device: str):
        """Change processing device"""
        self.config_manager.update_detection(device=device)

        # Recreate detector if exists
        if self.detector:
            self.detector = None  # Will be recreated on next start

        self.status_bar.showMessage(f"Device changed to: {device}")

    def set_roi(self, points: list):
        """Set region of interest"""
        if self.detector and hasattr(self.video_widget, 'current_frame') and self.video_widget.current_frame is not None:
            frame_shape = self.video_widget.current_frame.shape
            success = self.detector.set_roi(points, frame_shape)

            if success:
                self.status_bar.showMessage("ROI set successfully")
            else:
                QMessageBox.warning(self, "Warning", "Failed to set ROI")

    def add_counting_line(self, point1: tuple, point2: tuple):
        """Add counting line"""
        if self.detector:
            success = self.detector.add_counting_line(point1, point2)

            if success:
                line_count = len(getattr(self.detector, 'counting_lines', []))
                self.status_bar.showMessage(f"Counting line {line_count} added")
            else:
                QMessageBox.warning(self, "Warning", "Failed to add counting line")

    def clear_annotations(self):
        """Clear all annotations"""
        if self.detector:
            self.detector.clear_roi_and_lines()
            if hasattr(self.stats_widget, 'clear_vehicle_counts'):
                self.stats_widget.clear_vehicle_counts()
            self.status_bar.showMessage("Annotations cleared")

    def reset_view(self):
        """Reset view to default"""
        if hasattr(self.video_widget, 'reset_view'):
            self.video_widget.reset_view()
        if hasattr(self.stats_widget, 'reset'):
            self.stats_widget.reset()

    def closeEvent(self, event):
        """Handle application close"""
        print("🔄 Application closing...")

        try:
            # Stop detection
            if self.is_running:
                self.stop_detection()

            # Release resources
            if self.video_source:
                self.video_source.release()

            # Save configuration
            self.config_manager.save()

            event.accept()
            print("✅ Application closed cleanly")

        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            event.accept()


def run_app(config_path: str = None):
    """Run the GUI application"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Vehicle Detection System")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("VDS Team")

    try:
        # Create and show main window
        window = MainWindow(config_path)
        window.show()

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        sys.exit(1)


if __name__ == "__main__":
    run_app()