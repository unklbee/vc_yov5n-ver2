"""
src/gui/control_panel.py
Control panel for video source selection and system controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Callable, Dict, Any


class ControlPanel(ttk.Frame):
    """Control panel with source selection, device settings, and statistics"""

    def __init__(self, parent, config_manager, source_callback, device_callback,
                 start_stop_callback, settings_callback):
        super().__init__(parent, relief=tk.RAISED, borderwidth=1)

        self.config_manager = config_manager
        self.source_callback = source_callback
        self.device_callback = device_callback
        self.start_stop_callback = start_stop_callback
        self.settings_callback = settings_callback

        # State variables
        self.is_running = tk.BooleanVar()
        self.source_type = tk.StringVar(value="file")
        self.device_type = tk.StringVar(value="CPU")
        self.frame_skip = tk.IntVar(value=2)

        # Current source config
        self.current_source_config = {}

        self._create_widgets()
        self._setup_layout()
        self._bind_events()

        # Load initial configuration
        self._load_config()

    def _create_widgets(self):
        """Create control panel widgets"""
        # Title
        title_label = ttk.Label(self, text="Vehicle Detection Control",
                                font=('Arial', 12, 'bold'))

        # Source selection frame
        source_frame = ttk.LabelFrame(self, text="Video Source", padding=10)

        # Source type selection
        ttk.Label(source_frame, text="Source Type:").grid(row=0, column=0, sticky="w", pady=2)
        source_combo = ttk.Combobox(source_frame, textvariable=self.source_type,
                                    values=["file", "webcam", "rtsp"], state="readonly", width=15)
        source_combo.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        # File selection
        self.file_frame = ttk.Frame(source_frame)
        ttk.Label(self.file_frame, text="File:").grid(row=0, column=0, sticky="w")
        self.file_entry = ttk.Entry(self.file_frame, width=25)
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.file_button = ttk.Button(self.file_frame, text="Browse",
                                      command=self._browse_file, width=8)
        self.file_button.grid(row=0, column=2, padx=(5, 0))

        # Webcam selection
        self.webcam_frame = ttk.Frame(source_frame)
        ttk.Label(self.webcam_frame, text="Camera ID:").grid(row=0, column=0, sticky="w")
        self.camera_spin = ttk.Spinbox(self.webcam_frame, from_=0, to=10, width=15, value=0)
        self.camera_spin.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # RTSP selection
        self.rtsp_frame = ttk.Frame(source_frame)
        ttk.Label(self.rtsp_frame, text="RTSP URL:").grid(row=0, column=0, sticky="w")
        self.rtsp_entry = ttk.Entry(self.rtsp_frame, width=30)
        self.rtsp_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Load source button
        self.load_source_button = ttk.Button(source_frame, text="Load Source",
                                             command=self._load_source)

        # Device selection frame
        device_frame = ttk.LabelFrame(self, text="Processing Device", padding=10)

        device_radio_frame = ttk.Frame(device_frame)
        ttk.Radiobutton(device_radio_frame, text="CPU", variable=self.device_type,
                        value="CPU", command=self._on_device_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(device_radio_frame, text="GPU", variable=self.device_type,
                        value="GPU", command=self._on_device_change).pack(side=tk.LEFT, padx=5)

        # Performance frame
        perf_frame = ttk.LabelFrame(self, text="Performance Settings", padding=10)

        ttk.Label(perf_frame, text="Frame Skip:").grid(row=0, column=0, sticky="w", pady=2)
        self.frame_skip_scale = ttk.Scale(perf_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                          variable=self.frame_skip, command=self._on_frame_skip_change)
        self.frame_skip_scale.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))
        self.frame_skip_label = ttk.Label(perf_frame, text="2")
        self.frame_skip_label.grid(row=0, column=2, padx=(5, 0))

        # Control buttons frame
        control_frame = ttk.LabelFrame(self, text="Detection Control", padding=10)

        self.start_stop_button = ttk.Button(control_frame, text="Start Detection",
                                            command=self.start_stop_callback)

        self.settings_button = ttk.Button(control_frame, text="Settings",
                                          command=self.settings_callback)

        # Statistics frame
        stats_frame = ttk.LabelFrame(self, text="Statistics", padding=10)

        self.stats_text = tk.Text(stats_frame, height=12, width=35, state=tk.DISABLED,
                                  font=('Courier', 9))
        stats_scrollbar = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)

        # Store widgets for layout
        self.widgets = {
            'title': title_label,
            'source_frame': source_frame,
            'source_combo': source_combo,
            'device_frame': device_frame,
            'device_radio_frame': device_radio_frame,
            'perf_frame': perf_frame,
            'control_frame': control_frame,
            'stats_frame': stats_frame,
            'stats_scrollbar': stats_scrollbar
        }

        # Configure grid weights for source frame
        source_frame.grid_columnconfigure(1, weight=1)
        self.file_frame.grid_columnconfigure(1, weight=1)
        self.webcam_frame.grid_columnconfigure(1, weight=1)
        self.rtsp_frame.grid_columnconfigure(1, weight=1)
        perf_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)

    def _setup_layout(self):
        """Setup control panel layout"""
        # Configure main grid
        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Title
        self.widgets['title'].grid(row=row, column=0, pady=(10, 15), sticky="ew")
        row += 1

        # Source frame
        self.widgets['source_frame'].grid(row=row, column=0, sticky="ew", pady=5, padx=10)
        row += 1

        # Device frame
        self.widgets['device_frame'].grid(row=row, column=0, sticky="ew", pady=5, padx=10)
        self.widgets['device_radio_frame'].grid(row=0, column=0, sticky="w")
        row += 1

        # Performance frame
        self.widgets['perf_frame'].grid(row=row, column=0, sticky="ew", pady=5, padx=10)
        row += 1

        # Control frame
        self.widgets['control_frame'].grid(row=row, column=0, sticky="ew", pady=5, padx=10)
        self.start_stop_button.grid(row=0, column=0, sticky="ew", pady=2)
        self.settings_button.grid(row=1, column=0, sticky="ew", pady=2)
        row += 1

        # Statistics frame
        self.widgets['stats_frame'].grid(row=row, column=0, sticky="nsew", pady=5, padx=10)
        self.stats_text.grid(row=0, column=0, sticky="nsew")
        self.widgets['stats_scrollbar'].grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(row, weight=1)

        # Show initial source frame
        self._show_source_frame()

    def _bind_events(self):
        """Bind events"""
        self.source_type.trace('w', self._on_source_type_change)
        self.frame_skip.trace('w', self._on_frame_skip_change)

    def _load_config(self):
        """Load configuration from config manager"""
        detection_config = self.config_manager.config.detection
        self.device_type.set(detection_config.device)
        self.frame_skip.set(detection_config.frame_skip)

    def _on_source_type_change(self, *args):
        """Handle source type change"""
        self._show_source_frame()

    def _show_source_frame(self):
        """Show appropriate source configuration frame"""
        # Hide all frames
        self.file_frame.grid_remove()
        self.webcam_frame.grid_remove()
        self.rtsp_frame.grid_remove()

        # Show appropriate frame
        source_type = self.source_type.get()
        if source_type == "file":
            self.file_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        elif source_type == "webcam":
            self.webcam_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        elif source_type == "rtsp":
            self.rtsp_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)

        # Show load button
        self.load_source_button.grid(row=2, column=0, columnspan=2, pady=10)

    def _browse_file(self):
        """Browse for video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )

        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def _load_source(self):
        """Load selected video source"""
        source_type = self.source_type.get()

        if source_type == "file":
            file_path = self.file_entry.get().strip()
            if not file_path:
                messagebox.showerror("Error", "Please select a video file")
                return
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Selected file does not exist")
                return

            self.current_source_config = {
                'type': 'file',
                'file_path': file_path,
                'loop': True
            }

        elif source_type == "webcam":
            try:
                camera_id = int(self.camera_spin.get())
                self.current_source_config = {
                    'type': 'webcam',
                    'camera_id': camera_id
                }
            except ValueError:
                messagebox.showerror("Error", "Invalid camera ID")
                return

        elif source_type == "rtsp":
            rtsp_url = self.rtsp_entry.get().strip()
            if not rtsp_url:
                messagebox.showerror("Error", "Please enter RTSP URL")
                return

            self.current_source_config = {
                'type': 'rtsp',
                'rtsp_url': rtsp_url
            }

        # Call source callback
        if self.source_callback:
            self.source_callback(self.current_source_config)

    def _on_device_change(self):
        """Handle device change"""
        device = self.device_type.get()
        if self.device_callback:
            self.device_callback(device)

    def _on_frame_skip_change(self, *args):
        """Handle frame skip change"""
        skip_value = self.frame_skip.get()
        self.frame_skip_label.config(text=str(skip_value))

        # Update detector if available
        # This will be handled by the main window

    def set_running_state(self, running: bool):
        """Set running state and update button"""
        self.is_running.set(running)
        if running:
            self.start_stop_button.config(text="Stop Detection")
        else:
            self.start_stop_button.config(text="Start Detection")

    def update_statistics(self, stats: Dict[str, Any]):
        """Update statistics display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)

        # Format statistics
        stats_lines = [
            f"FPS: {stats.get('fps', 0):.1f}",
            f"Frame Skip: 1/{stats.get('frame_skip', 1)}",
            f"ROI: {'ON' if stats.get('roi_enabled', False) else 'OFF'}",
            f"Lines: {stats.get('line_count', 0)}",
            "",
            "Vehicle Counts:",
            "-" * 20
        ]

        vehicle_counts = stats.get('vehicle_counts', {})
        total_up = 0
        total_down = 0

        for vehicle_type, counts in vehicle_counts.items():
            up_count = counts.get('up', 0)
            down_count = counts.get('down', 0)
            total_up += up_count
            total_down += down_count

            stats_lines.extend([
                f"{vehicle_type.capitalize()}:",
                f"  ↑ Up: {up_count}",
                f"  ↓ Down: {down_count}",
                ""
            ])

        stats_lines.extend([
            "-" * 20,
            f"Total Up: {total_up}",
            f"Total Down: {total_down}",
            f"Grand Total: {total_up + total_down}"
        ])

        self.stats_text.insert(tk.END, "\n".join(stats_lines))
        self.stats_text.config(state=tk.DISABLED)

    def get_current_frame_skip(self) -> int:
        """Get current frame skip value"""
        return self.frame_skip.get()