"""
src/gui/main_window.py
Main GUI window using PySide6 with JetBrains-style design
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QToolBar, QLabel, QFrame,
    QMessageBox, QProgressBar, QDockWidget
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QFont, QPixmap, QAction, QPalette, QColor
import cv2
import numpy as np
from typing import Optional, Dict, Any
import threading
import time
import os

# Import core modules
try:
    from ..core.detector import OptimizedVehicleDetector
    from ..utils.video_source import VideoSourceFactory
    from ..utils.config_manager import ConfigManager
    from ..utils.data_manager import DataManager
except ImportError:
    # Handle relative import issues during development
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from src.core.detector import OptimizedVehicleDetector
    from src.utils.video_source import VideoSourceFactory
    from src.utils.config_manager import ConfigManager
    from src.utils.data_manager import DataManager

# Import GUI modules
try:
    from .styles.jetbrains_theme import JetBrainsTheme
    from .widgets.video_widget import VideoDisplayWidget
    from .widgets.control_panel import ControlPanelWidget
    from .widgets.statistics_panel import StatisticsPanelWidget
    from .widgets.toolbar import MainToolBar
    from .dialogs.settings_dialog import SettingsDialog
    from .dialogs.source_dialog import VideoSourceDialog
except ImportError:
    # Fallback for missing GUI components
    print("⚠️ Some GUI components not found. Creating minimal interface...")

    class JetBrainsTheme:
        def get_main_stylesheet(self): return ""
        def apply_palette(self, app): pass

    class VideoDisplayWidget(QWidget):
        roi_drawn = Signal(list)
        line_drawn = Signal(tuple, tuple)
        annotations_cleared = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setMinimumSize(640, 480)
            self.setStyleSheet("background-color: #1E1E1E; border: 1px solid #555; color: white;")
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Video display not available"))

        def update_frame(self, frame): pass
        def draw_detections(self, frame, detections, detector): return frame
        def clear_display(self): pass

    class ControlPanelWidget(QWidget):
        source_changed = Signal(dict)
        device_changed = Signal(str)
        detection_toggled = Signal()
        frame_skip_changed = Signal(int)

        def __init__(self, config_manager, parent=None):
            super().__init__(parent)
            self.setFixedWidth(320)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Control panel not available"))

        def set_detection_state(self, running): pass

    class StatisticsPanelWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedWidth(350)
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Statistics panel not available"))

        def update_statistics(self, stats, vehicle_counts): pass
        def clear_statistics(self): pass

    class MainToolBar(QToolBar):
        play_pause_clicked = Signal()
        stop_clicked = Signal()
        settings_clicked = Signal()

        def __init__(self, parent=None):
            super().__init__(parent)
            self.addWidget(QLabel("Toolbar not available"))

        def set_detection_state(self, running): pass

    class SettingsDialog:
        def __init__(self, *args): pass
        def exec(self): return False

    class VideoSourceDialog:
        def __init__(self, parent=None): pass
        def exec(self): return False
        def get_source_config(self): return {}


class DetectionWorker(QThread):
    """Worker thread for vehicle detection"""

    frame_processed = Signal(np.ndarray, list, dict)
    error_occurred = Signal(str)

    def __init__(self, detector, video_source):
        super().__init__()
        self.detector = detector
        self.video_source = video_source
        self.running = False
        self.paused = False

    def run(self):
        """Main detection loop"""
        self.running = True

        while self.running:
            try:
                if not self.paused and self.video_source:
                    ret, frame = self.video_source.read()
                    if not ret:
                        continue

                    # Perform detection
                    detections, proc_time = self.detector.detect_vehicles(frame)

                    # Get statistics
                    stats = self.detector.get_statistics()

                    # Emit results
                    self.frame_processed.emit(frame, detections, stats)

                self.msleep(33)  # ~30 FPS

            except Exception as e:
                self.error_occurred.emit(str(e))
                break

    def stop(self):
        """Stop the detection thread"""
        self.running = False
        self.wait()

    def pause(self):
        """Pause detection"""
        self.paused = True

    def resume(self):
        """Resume detection"""
        self.paused = False


class VehicleDetectionMainWindow(QMainWindow):
    """Main application window with JetBrains-style design"""

    def __init__(self, config_path: str = "config/default.yaml"):
        super().__init__()

        # Initialize core components
        self.config_manager = ConfigManager(config_path)
        self.detector = None
        self.video_source = None
        self.data_manager = None
        self.detection_worker = None

        # UI state
        self.is_detection_running = False

        # Apply JetBrains theme
        self.theme = JetBrainsTheme()
        self.setStyleSheet(self.theme.get_main_stylesheet())

        self._setup_ui()
        self._setup_connections()
        self._init_data_manager()

        # Show window
        self.show()

    def _setup_ui(self):
        """Setup the main UI components"""
        self.setWindowTitle("Vehicle Detection System")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # Set window icon (optional)
        # self.setWindowIcon(QIcon("resources/icons/app_icon.png"))

        # Setup menu bar
        self._create_menu_bar()

        # Setup toolbar
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # Setup central widget with splitter
        self._create_central_widget()

        # Setup dock widgets
        self._create_dock_widgets()

        # Setup status bar
        self._create_status_bar()

    def _create_menu_bar(self):
        """Create menu bar with JetBrains-style menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_project_action = QAction("&New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)

        open_action = QAction("&Open Video...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_video_source)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_config_action = QAction("&Save Configuration", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.triggered.connect(self._save_configuration)
        file_menu.addAction(save_config_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.triggered.connect(self._open_settings)
        edit_menu.addAction(settings_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        self.show_statistics_action = QAction("Statistics Panel", self)
        self.show_statistics_action.setCheckable(True)
        self.show_statistics_action.setChecked(True)
        view_menu.addAction(self.show_statistics_action)

        self.show_controls_action = QAction("Control Panel", self)
        self.show_controls_action.setCheckable(True)
        self.show_controls_action.setChecked(True)
        view_menu.addAction(self.show_controls_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        self.start_detection_action = QAction("&Start Detection", self)
        self.start_detection_action.setShortcut("F5")
        self.start_detection_action.triggered.connect(self._toggle_detection)
        run_menu.addAction(self.start_detection_action)

        self.pause_detection_action = QAction("&Pause Detection", self)
        self.pause_detection_action.setShortcut("F6")
        self.pause_detection_action.setEnabled(False)
        self.pause_detection_action.triggered.connect(self._pause_detection)
        run_menu.addAction(self.pause_detection_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        api_test_action = QAction("Test &API Connection", self)
        api_test_action.triggered.connect(self._test_api_connection)
        tools_menu.addAction(api_test_action)

        clear_data_action = QAction("&Clear Detection Data", self)
        clear_data_action.triggered.connect(self._clear_detection_data)
        tools_menu.addAction(clear_data_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create central widget with video display"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Video display widget (center)
        self.video_widget = VideoDisplayWidget(self)
        self.main_splitter.addWidget(self.video_widget)

        # Set splitter proportions
        self.main_splitter.setSizes([300, 1000, 300])
        self.main_splitter.setStretchFactor(1, 1)  # Video widget gets most space

    def _create_dock_widgets(self):
        """Create dock widgets for panels"""
        # Control panel dock
        self.control_dock = QDockWidget("Control Panel", self)
        self.control_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.control_panel = ControlPanelWidget(self.config_manager, self)
        self.control_dock.setWidget(self.control_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)

        # Statistics panel dock
        self.statistics_dock = QDockWidget("Statistics", self)
        self.statistics_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.statistics_panel = StatisticsPanelWidget(self)
        self.statistics_dock.setWidget(self.statistics_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.statistics_dock)

        # Connect dock visibility to menu actions
        self.show_controls_action.triggered.connect(
            lambda checked: self.control_dock.setVisible(checked)
        )
        self.show_statistics_action.triggered.connect(
            lambda checked: self.statistics_dock.setVisible(checked)
        )

        # Update menu when docks are closed
        self.control_dock.visibilityChanged.connect(
            self.show_controls_action.setChecked
        )
        self.statistics_dock.visibilityChanged.connect(
            self.show_statistics_action.setChecked
        )

    def _create_status_bar(self):
        """Create status bar with indicators"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Add spacer
        spacer_label = QLabel("")
        spacer_label.setMinimumWidth(1)
        self.status_bar.addPermanentWidget(spacer_label, 1)

        # FPS indicator
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setMinimumWidth(80)
        self.status_bar.addPermanentWidget(self.fps_label)

        # Detection status indicator
        self.detection_status_label = QLabel("●")
        self.detection_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        self.detection_status_label.setToolTip("Detection Status: Stopped")
        self.status_bar.addPermanentWidget(self.detection_status_label)

        # Memory usage (placeholder)
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setMinimumWidth(100)
        self.status_bar.addPermanentWidget(self.memory_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _setup_connections(self):
        """Setup signal-slot connections"""
        try:
            # Control panel connections
            self.control_panel.source_changed.connect(self._on_source_changed)
            self.control_panel.device_changed.connect(self._on_device_changed)
            self.control_panel.detection_toggled.connect(self._toggle_detection)

            # Video widget connections
            self.video_widget.roi_drawn.connect(self._on_roi_drawn)
            self.video_widget.line_drawn.connect(self._on_line_drawn)
            self.video_widget.annotations_cleared.connect(self._on_annotations_cleared)

            # Toolbar connections
            self.toolbar.play_pause_clicked.connect(self._toggle_detection)
            self.toolbar.stop_clicked.connect(self._stop_detection)
            self.toolbar.settings_clicked.connect(self._open_settings)
        except Exception as e:
            print(f"Warning: Could not connect all signals: {e}")

    def _init_data_manager(self):
        """Initialize data manager"""
        try:
            config_dict = {
                'data_storage': self.config_manager.config.data_storage.__dict__,
                'api': self.config_manager.config.api.__dict__
            }
            self.data_manager = DataManager(config_dict)
            self.status_label.setText("Data manager initialized")
        except Exception as e:
            self._show_error(f"Failed to initialize data manager: {str(e)}")

    def _new_project(self):
        """Create new project"""
        reply = QMessageBox.question(
            self, "New Project",
            "This will reset all current settings. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._stop_detection()
            self._clear_detection_data()
            self.video_widget.clear_display()
            self.status_label.setText("New project created")

    def _open_video_source(self):
        """Open video source dialog"""
        dialog = VideoSourceDialog(self)
        if dialog.exec():
            source_config = dialog.get_source_config()
            self._on_source_changed(source_config)

    def _save_configuration(self):
        """Save current configuration"""
        try:
            self.config_manager.save_config()
            self.status_label.setText("Configuration saved")
        except Exception as e:
            self._show_error(f"Failed to save configuration: {str(e)}")

    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self.data_manager, self)
        if dialog.exec():
            self.status_label.setText("Settings updated")
            # Refresh components that depend on settings
            self._refresh_detector_config()

    def _toggle_detection(self):
        """Toggle detection on/off"""
        if self.is_detection_running:
            self._stop_detection()
        else:
            self._start_detection()

    def _start_detection(self):
        """Start vehicle detection"""
        try:
            if not self.video_source:
                self._show_error("No video source available. Please load a video source first.")
                return

            if not self.detector:
                self._initialize_detector()

            if not self.detector:
                return

            # Create and start detection worker
            self.detection_worker = DetectionWorker(self.detector, self.video_source)
            self.detection_worker.frame_processed.connect(self._on_frame_processed)
            self.detection_worker.error_occurred.connect(self._on_detection_error)
            self.detection_worker.start()

            # Update UI state
            self.is_detection_running = True
            self._update_detection_ui_state()
            self.status_label.setText("Detection started")

        except Exception as e:
            self._show_error(f"Failed to start detection: {str(e)}")

    def _stop_detection(self):
        """Stop vehicle detection"""
        if self.detection_worker:
            self.detection_worker.stop()
            self.detection_worker = None

        self.is_detection_running = False
        self._update_detection_ui_state()
        self.status_label.setText("Detection stopped")

    def _pause_detection(self):
        """Pause/resume detection"""
        if self.detection_worker:
            if self.detection_worker.paused:
                self.detection_worker.resume()
                self.pause_detection_action.setText("&Pause Detection")
                self.status_label.setText("Detection resumed")
            else:
                self.detection_worker.pause()
                self.pause_detection_action.setText("&Resume Detection")
                self.status_label.setText("Detection paused")

    def _update_detection_ui_state(self):
        """Update UI elements based on detection state"""
        if self.is_detection_running:
            self.start_detection_action.setText("&Stop Detection")
            self.pause_detection_action.setEnabled(True)
            self.detection_status_label.setStyleSheet("color: #51cf66; font-size: 14px;")
            self.detection_status_label.setToolTip("Detection Status: Running")
            self.toolbar.set_detection_state(True)
        else:
            self.start_detection_action.setText("&Start Detection")
            self.pause_detection_action.setEnabled(False)
            self.pause_detection_action.setText("&Pause Detection")
            self.detection_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            self.detection_status_label.setToolTip("Detection Status: Stopped")
            self.toolbar.set_detection_state(False)

    def _initialize_detector(self):
        """Initialize vehicle detector"""
        try:
            detection_config = self.config_manager.get_detection_config()
            self.detector = OptimizedVehicleDetector(
                detection_config['model_path'],
                detection_config['device'],
                detection_config
            )
            self.status_label.setText(f"Detector initialized on {detection_config['device']}")
        except Exception as e:
            self._show_error(f"Failed to initialize detector: {str(e)}")
            self.detector = None

    def _refresh_detector_config(self):
        """Refresh detector with new configuration"""
        if self.detector:
            try:
                detection_config = self.config_manager.get_detection_config()
                self.detector.apply_config(detection_config)
                self.status_label.setText("Detector configuration updated")
            except Exception as e:
                self._show_error(f"Failed to update detector configuration: {str(e)}")

    def _on_source_changed(self, source_config: Dict[str, Any]):
        """Handle video source change"""
        try:
            self._stop_detection()

            # Create new video source
            self.video_source = VideoSourceFactory.create_source(source_config)

            if self.video_source and self.video_source.open():
                # Display first frame
                ret, frame = self.video_source.read()
                if ret:
                    self.video_widget.update_frame(frame)
                    self.status_label.setText(f"Video source loaded: {source_config.get('type', 'Unknown')}")
                else:
                    self._show_error("Failed to read from video source")
            else:
                self._show_error("Failed to open video source")

        except Exception as e:
            self._show_error(f"Error loading video source: {str(e)}")

    def _on_device_changed(self, device: str):
        """Handle device change"""
        self.config_manager.update_detection_config(device=device)
        self._refresh_detector_config()
        self.status_label.setText(f"Processing device changed to: {device}")

    def _on_frame_processed(self, frame: np.ndarray, detections: list, stats: dict):
        """FIXED: Handle processed frame from detection worker with proper vehicle counts"""
        try:
            # Update video display
            result_frame = self.video_widget.draw_detections(frame, detections, self.detector)
            self.video_widget.update_frame(result_frame)

            # FIXED: Get proper vehicle counts from detector
            vehicle_counts = {}
            if self.detector and hasattr(self.detector, 'vehicle_counts'):
                # Convert defaultdict to regular dict for statistics panel
                vehicle_counts = {
                    vehicle_type: {
                        'up': counts['up'],
                        'down': counts['down']
                    }
                    for vehicle_type, counts in self.detector.vehicle_counts.items()
                }

                # Ensure all vehicle types are present even if count is 0
                for vehicle_type in ['car', 'motorcycle', 'bus', 'truck']:
                    if vehicle_type not in vehicle_counts:
                        vehicle_counts[vehicle_type] = {'up': 0, 'down': 0}

            # Update statistics with proper vehicle counts
            self.statistics_panel.update_statistics(stats, vehicle_counts)

            # Update status bar
            self.fps_label.setText(f"FPS: {stats['fps']:.1f}")

            # Update data manager
            if self.data_manager:
                line_stats = []
                if self.detector and hasattr(self.detector, 'line_counters'):
                    line_stats = [counter.get_statistics() for counter in self.detector.line_counters]

                self.data_manager.add_count_data(
                    vehicle_counts,  # Use the properly formatted vehicle_counts
                    stats['fps'],
                    line_stats
                )

            # Debug print untuk verify data
            total_counts = sum(sum(counts.values()) for counts in vehicle_counts.values())
            if total_counts > 0:
                print(f"📊 Vehicle counts updated: {vehicle_counts} (Total: {total_counts})")

        except Exception as e:
            print(f"Error in frame processing: {e}")
            import traceback
            traceback.print_exc()

    def _on_detection_error(self, error_message: str):
        """Handle detection error"""
        self._show_error(f"Detection error: {error_message}")
        self._stop_detection()

    def _on_roi_drawn(self, points: list):
        """Handle ROI drawing completion"""
        if self.detector and len(points) >= 3:
            frame_shape = (self.video_widget.height(), self.video_widget.width())
            self.detector.set_roi_from_points(points, frame_shape)
            self.status_label.setText("ROI set successfully")

    def _on_line_drawn(self, point1: tuple, point2: tuple):
        """Handle counting line drawing completion"""
        if self.detector:
            self.detector.add_counting_line(point1, point2)
            self.status_label.setText("Counting line added")

    def _on_annotations_cleared(self):
        """Handle annotations clearing"""
        if self.detector:
            self.detector.clear_roi_and_lines()
            self.status_label.setText("Annotations cleared")

    def _test_api_connection(self):
        """Test API connection"""
        # Implementation would go here
        self.status_label.setText("API connection test completed")

    def _clear_detection_data(self):
        """Clear all detection data"""
        if self.detector:
            self.detector.vehicle_counts.clear()
            for counter in self.detector.line_counters:
                counter.reset_counts()

        self.statistics_panel.clear_statistics()
        self.status_label.setText("Detection data cleared")

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Vehicle Detection System",
            "Vehicle Detection System v1.0.0\n\n"
            "A modern vehicle detection and tracking system\n"
            "built with PySide6 and OpenVINO.\n\n"
            "© 2024 Vehicle Detection Team"
        )

    def _show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText(f"Error: {message}")

    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Stop detection
            self._stop_detection()

            # Release video source
            if self.video_source:
                self.video_source.release()

            # Stop data manager
            if self.data_manager:
                self.data_manager.stop()

            # Save configuration
            self.config_manager.save_config()

            event.accept()

        except Exception as e:
            print(f"Error during cleanup: {e}")
            event.accept()


class VehicleDetectionApp(QApplication):
    """Main application class"""

    def __init__(self, argv):
        super().__init__(argv)

        # Set application properties
        self.setApplicationName("Vehicle Detection System")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Vehicle Detection Team")

        # Apply global font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

        # Create main window
        self.main_window = None


def run_gui_app(config_path: str = "config/default.yaml"):
    """Run the PySide6 GUI application"""
    app = VehicleDetectionApp(sys.argv)

    try:
        # Apply theme
        theme = JetBrainsTheme()
        theme.apply_palette(app)

        # Create and show main window
        main_window = VehicleDetectionMainWindow(config_path)
        app.main_window = main_window

        # Run application
        sys.exit(app.exec())
    except SystemExit:
        pass
    except Exception as e:
        print(f"❌ Error running GUI application: {e}")
        sys.exit(1)
    """Worker thread for vehicle detection"""

    frame_processed = Signal(np.ndarray, list, dict)
    error_occurred = Signal(str)

    def __init__(self, detector, video_source):
        super().__init__()
        self.detector = detector
        self.video_source = video_source
        self.running = False
        self.paused = False

    def run(self):
        """Main detection loop"""
        self.running = True

        while self.running:
            try:
                if not self.paused and self.video_source:
                    ret, frame = self.video_source.read()
                    if not ret:
                        continue

                    # Perform detection
                    detections, proc_time = self.detector.detect_vehicles(frame)

                    # Get statistics
                    stats = self.detector.get_statistics()

                    # Emit results
                    self.frame_processed.emit(frame, detections, stats)

                self.msleep(33)  # ~30 FPS

            except Exception as e:
                self.error_occurred.emit(str(e))
                break

    def stop(self):
        """Stop the detection thread"""
        self.running = False
        self.wait()

    def pause(self):
        """Pause detection"""
        self.paused = True

    def resume(self):
        """Resume detection"""
        self.paused = False


class VehicleDetectionMainWindow(QMainWindow):
    """Main application window with JetBrains-style design"""

    def __init__(self, config_path: str = "config/default.yaml"):
        super().__init__()

        # Initialize core components
        self.config_manager = ConfigManager(config_path)
        self.detector = None
        self.video_source = None
        self.data_manager = None
        self.detection_worker = None

        # UI state
        self.is_detection_running = False

        # Apply JetBrains theme
        self.theme = JetBrainsTheme()
        self.setStyleSheet(self.theme.get_main_stylesheet())

        self._setup_ui()
        self._setup_connections()
        self._init_data_manager()

        # Show window
        self.show()

    def _setup_ui(self):
        """Setup the main UI components"""
        self.setWindowTitle("Vehicle Detection System")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # Set window icon
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))

        # Setup menu bar
        self._create_menu_bar()

        # Setup toolbar
        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        # Setup central widget with splitter
        self._create_central_widget()

        # Setup dock widgets
        self._create_dock_widgets()

        # Setup status bar
        self._create_status_bar()

    def _create_menu_bar(self):
        """Create menu bar with JetBrains-style menus"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_project_action = QAction("&New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)

        open_action = QAction("&Open Video...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_video_source)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_config_action = QAction("&Save Configuration", self)
        save_config_action.setShortcut("Ctrl+S")
        save_config_action.triggered.connect(self._save_configuration)
        file_menu.addAction(save_config_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+Alt+S")
        settings_action.triggered.connect(self._open_settings)
        edit_menu.addAction(settings_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        self.show_statistics_action = QAction("Statistics Panel", self)
        self.show_statistics_action.setCheckable(True)
        self.show_statistics_action.setChecked(True)
        view_menu.addAction(self.show_statistics_action)

        self.show_controls_action = QAction("Control Panel", self)
        self.show_controls_action.setCheckable(True)
        self.show_controls_action.setChecked(True)
        view_menu.addAction(self.show_controls_action)

        # Run menu
        run_menu = menubar.addMenu("&Run")

        self.start_detection_action = QAction("&Start Detection", self)
        self.start_detection_action.setShortcut("F5")
        self.start_detection_action.triggered.connect(self._toggle_detection)
        run_menu.addAction(self.start_detection_action)

        self.pause_detection_action = QAction("&Pause Detection", self)
        self.pause_detection_action.setShortcut("F6")
        self.pause_detection_action.setEnabled(False)
        self.pause_detection_action.triggered.connect(self._pause_detection)
        run_menu.addAction(self.pause_detection_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        api_test_action = QAction("Test &API Connection", self)
        api_test_action.triggered.connect(self._test_api_connection)
        tools_menu.addAction(api_test_action)

        clear_data_action = QAction("&Clear Detection Data", self)
        clear_data_action.triggered.connect(self._clear_detection_data)
        tools_menu.addAction(clear_data_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_central_widget(self):
        """Create central widget with video display"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)

        # Video display widget (center)
        self.video_widget = VideoDisplayWidget(self)
        self.main_splitter.addWidget(self.video_widget)

        # Set splitter proportions
        self.main_splitter.setSizes([300, 1000, 300])
        self.main_splitter.setStretchFactor(1, 1)  # Video widget gets most space

    def _create_dock_widgets(self):
        """Create dock widgets for panels"""
        # Control panel dock
        self.control_dock = QDockWidget("Control Panel", self)
        self.control_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.control_panel = ControlPanelWidget(self.config_manager, self)
        self.control_dock.setWidget(self.control_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.control_dock)

        # Statistics panel dock
        self.statistics_dock = QDockWidget("Statistics", self)
        self.statistics_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.statistics_panel = StatisticsPanelWidget(self)
        self.statistics_dock.setWidget(self.statistics_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, self.statistics_dock)

        # Connect dock visibility to menu actions
        self.show_controls_action.triggered.connect(
            lambda checked: self.control_dock.setVisible(checked)
        )
        self.show_statistics_action.triggered.connect(
            lambda checked: self.statistics_dock.setVisible(checked)
        )

        # Update menu when docks are closed
        self.control_dock.visibilityChanged.connect(
            self.show_controls_action.setChecked
        )
        self.statistics_dock.visibilityChanged.connect(
            self.show_statistics_action.setChecked
        )

    def _create_status_bar(self):
        """Create status bar with indicators"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Add spacer
        self.status_bar.addPermanentWidget(QLabel(""), 1)

        # FPS indicator
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setMinimumWidth(80)
        self.status_bar.addPermanentWidget(self.fps_label)

        # Detection status indicator
        self.detection_status_label = QLabel("●")
        self.detection_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        self.detection_status_label.setToolTip("Detection Status: Stopped")
        self.status_bar.addPermanentWidget(self.detection_status_label)

        # Memory usage (placeholder)
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setMinimumWidth(100)
        self.status_bar.addPermanentWidget(self.memory_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def _setup_connections(self):
        """Setup signal-slot connections"""
        # Control panel connections
        self.control_panel.source_changed.connect(self._on_source_changed)
        self.control_panel.device_changed.connect(self._on_device_changed)
        self.control_panel.detection_toggled.connect(self._toggle_detection)

        # Video widget connections
        self.video_widget.roi_drawn.connect(self._on_roi_drawn)
        self.video_widget.line_drawn.connect(self._on_line_drawn)
        self.video_widget.annotations_cleared.connect(self._on_annotations_cleared)

        # Toolbar connections
        self.toolbar.play_pause_clicked.connect(self._toggle_detection)
        self.toolbar.stop_clicked.connect(self._stop_detection)
        self.toolbar.settings_clicked.connect(self._open_settings)

    def _init_data_manager(self):
        """Initialize data manager"""
        try:
            config_dict = {
                'data_storage': self.config_manager.config.data_storage.__dict__,
                'api': self.config_manager.config.api.__dict__
            }
            self.data_manager = DataManager(config_dict)
            self.status_label.setText("Data manager initialized")
        except Exception as e:
            self._show_error(f"Failed to initialize data manager: {str(e)}")

    def _new_project(self):
        """Create new project"""
        reply = QMessageBox.question(
            self, "New Project",
            "This will reset all current settings. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self._stop_detection()
            self._clear_detection_data()
            self.video_widget.clear_display()
            self.status_label.setText("New project created")

    def _open_video_source(self):
        """Open video source dialog"""
        dialog = VideoSourceDialog(self)
        if dialog.exec():
            source_config = dialog.get_source_config()
            self._on_source_changed(source_config)

    def _save_configuration(self):
        """Save current configuration"""
        try:
            self.config_manager.save_config()
            self.status_label.setText("Configuration saved")
        except Exception as e:
            self._show_error(f"Failed to save configuration: {str(e)}")

    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_manager, self.data_manager, self)
        if dialog.exec():
            self.status_label.setText("Settings updated")
            # Refresh components that depend on settings
            self._refresh_detector_config()

    def _toggle_detection(self):
        """Toggle detection on/off"""
        if self.is_detection_running:
            self._stop_detection()
        else:
            self._start_detection()

    def _start_detection(self):
        """Start vehicle detection"""
        try:
            if not self.video_source:
                self._show_error("No video source available. Please load a video source first.")
                return

            if not self.detector:
                self._initialize_detector()

            if not self.detector:
                return

            # Create and start detection worker
            self.detection_worker = DetectionWorker(self.detector, self.video_source)
            self.detection_worker.frame_processed.connect(self._on_frame_processed)
            self.detection_worker.error_occurred.connect(self._on_detection_error)
            self.detection_worker.start()

            # Update UI state
            self.is_detection_running = True
            self._update_detection_ui_state()
            self.status_label.setText("Detection started")

        except Exception as e:
            self._show_error(f"Failed to start detection: {str(e)}")

    def _stop_detection(self):
        """Stop vehicle detection"""
        if self.detection_worker:
            self.detection_worker.stop()
            self.detection_worker = None

        self.is_detection_running = False
        self._update_detection_ui_state()
        self.status_label.setText("Detection stopped")

    def _pause_detection(self):
        """Pause/resume detection"""
        if self.detection_worker:
            if self.detection_worker.paused:
                self.detection_worker.resume()
                self.pause_detection_action.setText("&Pause Detection")
                self.status_label.setText("Detection resumed")
            else:
                self.detection_worker.pause()
                self.pause_detection_action.setText("&Resume Detection")
                self.status_label.setText("Detection paused")

    def _update_detection_ui_state(self):
        """Update UI elements based on detection state"""
        if self.is_detection_running:
            self.start_detection_action.setText("&Stop Detection")
            self.pause_detection_action.setEnabled(True)
            self.detection_status_label.setStyleSheet("color: #51cf66; font-size: 14px;")
            self.detection_status_label.setToolTip("Detection Status: Running")
            self.toolbar.set_detection_state(True)
        else:
            self.start_detection_action.setText("&Start Detection")
            self.pause_detection_action.setEnabled(False)
            self.pause_detection_action.setText("&Pause Detection")
            self.detection_status_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            self.detection_status_label.setToolTip("Detection Status: Stopped")
            self.toolbar.set_detection_state(False)

    def _initialize_detector(self):
        """Initialize vehicle detector"""
        try:
            detection_config = self.config_manager.get_detection_config()
            self.detector = OptimizedVehicleDetector(
                detection_config['model_path'],
                detection_config['device'],
                detection_config
            )
            self.status_label.setText(f"Detector initialized on {detection_config['device']}")
        except Exception as e:
            self._show_error(f"Failed to initialize detector: {str(e)}")
            self.detector = None

    def _refresh_detector_config(self):
        """Refresh detector with new configuration"""
        if self.detector:
            try:
                detection_config = self.config_manager.get_detection_config()
                self.detector.apply_config(detection_config)
                self.status_label.setText("Detector configuration updated")
            except Exception as e:
                self._show_error(f"Failed to update detector configuration: {str(e)}")

    def _on_source_changed(self, source_config: Dict[str, Any]):
        """Handle video source change"""
        try:
            self._stop_detection()

            # Create new video source
            self.video_source = VideoSourceFactory.create_source(source_config)

            if self.video_source and self.video_source.open():
                # Display first frame
                ret, frame = self.video_source.read()
                if ret:
                    self.video_widget.update_frame(frame)
                    self.status_label.setText(f"Video source loaded: {source_config.get('type', 'Unknown')}")
                else:
                    self._show_error("Failed to read from video source")
            else:
                self._show_error("Failed to open video source")

        except Exception as e:
            self._show_error(f"Error loading video source: {str(e)}")

    def _on_device_changed(self, device: str):
        """Handle device change"""
        self.config_manager.update_detection_config(device=device)
        self._refresh_detector_config()
        self.status_label.setText(f"Processing device changed to: {device}")


    def _on_frame_processed(self, frame: np.ndarray, detections: list, stats: dict):
        """UPDATED: Handle processed frame dengan ROI debug visualization"""
        try:
            # IMPROVED: Gunakan method draw_detections yang sudah include ROI debug
            if self.detector:
                result_frame = self.detector.draw_detections(frame, detections)
            else:
                result_frame = self.video_widget.draw_detections(frame, detections, self.detector)

            # Update video display
            self.video_widget.update_frame(result_frame)

            # Get proper vehicle counts from detector
            vehicle_counts = {}
            if self.detector and hasattr(self.detector, 'vehicle_counts'):
                vehicle_counts = {
                    vehicle_type: {
                        'up': counts['up'],
                        'down': counts['down']
                    }
                    for vehicle_type, counts in self.detector.vehicle_counts.items()
                }

                # Ensure all vehicle types are present
                for vehicle_type in ['car', 'motorcycle', 'bus', 'truck']:
                    if vehicle_type not in vehicle_counts:
                        vehicle_counts[vehicle_type] = {'up': 0, 'down': 0}

            # Update statistics
            self.statistics_panel.update_statistics(stats, vehicle_counts)

            # Update status bar dengan ROI info
            fps = stats['fps']
            roi_status = "ROI ON" if stats.get('roi_enabled', False) else "ROI OFF"
            detection_count = len(detections)

            self.fps_label.setText(f"FPS: {fps:.1f}")

            # Update status dengan ROI feedback
            if stats.get('roi_enabled', False):
                status_text = f"Detection: {detection_count} vehicles in ROI area"
                self.status_label.setText(status_text)
            else:
                status_text = f"Detection: {detection_count} vehicles (full frame)"
                self.status_label.setText(status_text)

            # Update data manager
            if self.data_manager:
                line_stats = []
                if self.detector and hasattr(self.detector, 'line_counters'):
                    line_stats = [counter.get_statistics() for counter in self.detector.line_counters]

                self.data_manager.add_count_data(vehicle_counts, stats['fps'], line_stats)

            # Debug info untuk ROI
            if stats.get('roi_enabled', False):
                total_counts = sum(sum(counts.values()) for counts in vehicle_counts.values())
                if detection_count > 0:
                    print(f"🎯 ROI Detection: {detection_count} vehicles detected in ROI area")

        except Exception as e:
            print(f"Error in frame processing: {e}")
            import traceback
            traceback.print_exc()

    def _on_detection_error(self, error_message: str):
        """Handle detection error"""
        self._show_error(f"Detection error: {error_message}")
        self._stop_detection()

    def _on_roi_drawn(self, points: list):
        """Handle ROI drawing completion"""
        if self.detector and len(points) >= 3:
            frame_shape = (self.video_widget.height(), self.video_widget.width())
            self.detector.set_roi_from_points(points, frame_shape)
            self.status_label.setText("ROI set successfully")

    def _on_line_drawn(self, point1: tuple, point2: tuple):
        """Handle counting line drawing completion"""
        if self.detector:
            self.detector.add_counting_line(point1, point2)
            self.status_label.setText("Counting line added")

    def _on_roi_completed(self, points: list):
        """UPDATED: Handle ROI completion dengan better feedback"""
        try:
            self.control_bar.reset_mode()

            if self.detector and len(points) >= 3:
                # Get current frame shape
                if hasattr(self.video_widget, 'canvas') and self.video_widget.canvas.current_frame is not None:
                    frame_shape = self.video_widget.canvas.current_frame.shape[:2]

                    # Set ROI dengan validation
                    success = self.detector.set_roi_from_points(points, frame_shape)

                    if success:
                        # Calculate ROI area untuk user feedback
                        if self.detector.roi_mask is not None:
                            roi_area = np.sum(self.detector.roi_mask > 0)
                            total_area = frame_shape[0] * frame_shape[1]
                            roi_percentage = (roi_area / total_area) * 100

                            self.status_label.setText(f"ROI set successfully - {roi_percentage:.1f}% of frame")

                            # Show informative message
                            from PySide6.QtWidgets import QMessageBox
                            QMessageBox.information(
                                self,
                                "ROI Created",
                                f"ROI successfully created!\n\n"
                                f"• {len(points)} points defined\n"
                                f"• {roi_percentage:.1f}% of frame area\n"
                                f"• Detection now LIMITED to ROI area\n"
                                f"• Green overlay shows active detection zone"
                            )
                        else:
                            self.status_label.setText("ROI creation failed")
                            QMessageBox.warning(self, "ROI Error", "Failed to create ROI mask")
                    else:
                        self.status_label.setText("ROI creation failed - invalid points")
                        QMessageBox.warning(self, "ROI Error", "Invalid ROI points. Please try again with at least 3 points.")
                else:
                    print("❌ No current frame available for ROI")
                    QMessageBox.warning(self, "ROI Error", "No video frame available. Please load a video source first.")

        except Exception as e:
            print(f"ROI completion error: {e}")
            QMessageBox.critical(self, "ROI Error", f"Error creating ROI: {str(e)}")

    def _on_annotations_cleared(self):
        """UPDATED: Handle annotations clearing dengan better feedback"""
        try:
            if self.detector:
                self.detector.clear_roi_and_lines()
                self.status_label.setText("ROI and counting lines cleared - detection now uses full frame")

                # Show confirmation
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Annotations Cleared",
                    "All annotations cleared!\n\n"
                    "• ROI removed\n"
                    "• Counting lines removed\n"
                    "• Detection now uses full frame\n"
                    "• Vehicle counts reset"
                )

            self.annotations_cleared.emit()

        except Exception as e:
            print(f"Annotations clear error: {e}")

    def _test_api_connection(self):
        """Test API connection"""
        # Implementation would go here
        self.status_label.setText("API connection test completed")

    def _clear_detection_data(self):
        """Clear all detection data"""
        if self.detector:
            self.detector.vehicle_counts.clear()
            for counter in self.detector.line_counters:
                counter.reset_counts()

        self.statistics_panel.clear_statistics()
        self.status_label.setText("Detection data cleared")

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Vehicle Detection System",
            "Vehicle Detection System v1.0.0\n\n"
            "A modern vehicle detection and tracking system\n"
            "built with PySide6 and OpenVINO.\n\n"
            "© 2024 Vehicle Detection Team"
        )

    def _show_error(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText(f"Error: {message}")

    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Stop detection
            self._stop_detection()

            # Release video source
            if self.video_source:
                self.video_source.release()

            # Stop data manager
            if self.data_manager:
                self.data_manager.stop()

            # Save configuration
            self.config_manager.save_config()

            event.accept()

        except Exception as e:
            print(f"Error during cleanup: {e}")
            event.accept()


class VehicleDetectionApp(QApplication):
    """Main application class"""

    def __init__(self, argv):
        super().__init__(argv)

        # Set application properties
        self.setApplicationName("Vehicle Detection System")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Vehicle Detection Team")

        # Apply global font
        font = QFont("Segoe UI", 9)
        self.setFont(font)

        # Create main window
        self.main_window = VehicleDetectionMainWindow()


def run_gui_app(config_path: str = "config/default.yaml"):
    """Run the PySide6 GUI application"""
    app = VehicleDetectionApp(sys.argv)

    try:
        sys.exit(app.exec())
    except SystemExit:
        pass