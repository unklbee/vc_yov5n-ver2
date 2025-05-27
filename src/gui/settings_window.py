"""
src/gui/settings_window.py
Settings window for configuration management
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional

from ..utils.data_manager import APITester


class SettingsWindow:
    """Settings configuration window"""

    def __init__(self, parent, config_manager, data_manager):
        self.parent = parent
        self.config_manager = config_manager
        self.data_manager = data_manager

        self.window = None
        self.notebook = None

        # Configuration variables
        self._init_variables()

    def _init_variables(self):
        """Initialize configuration variables"""
        config = self.config_manager.config

        # Detection settings
        self.model_path = tk.StringVar(value=config.detection.model_path)
        self.conf_threshold = tk.DoubleVar(value=config.detection.conf_threshold)
        self.nms_threshold = tk.DoubleVar(value=config.detection.nms_threshold)

        # Tracker settings
        self.tracker_max_age = tk.IntVar(value=config.tracker.max_age)
        self.tracker_min_hits = tk.IntVar(value=config.tracker.min_hits)
        self.tracker_iou_threshold = tk.DoubleVar(value=config.tracker.iou_threshold)

        # Data storage settings
        self.storage_enabled = tk.BooleanVar(value=config.data_storage.enabled)
        self.save_interval = tk.IntVar(value=config.data_storage.save_interval)
        self.output_directory = tk.StringVar(value=config.data_storage.output_directory)
        self.data_format = tk.StringVar(value=config.data_storage.format)

        # API settings
        self.api_enabled = tk.BooleanVar(value=config.api.enabled)
        self.api_endpoint = tk.StringVar(value=config.api.endpoint)
        self.api_key = tk.StringVar(value=config.api.api_key)
        self.api_interval = tk.IntVar(value=config.api.send_interval)
        self.api_timeout = tk.IntVar(value=config.api.timeout)

    def show(self):
        """Show settings window"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Make window modal
        self.window.transient(self.parent)
        self.window.grab_set()

        self._create_widgets()
        self._setup_layout()

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create settings widgets"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)

        # Detection tab
        self._create_detection_tab()

        # Tracker tab
        self._create_tracker_tab()

        # Data storage tab
        self._create_storage_tab()

        # API tab
        self._create_api_tab()

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)

        ttk.Button(buttons_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Apply", command=self._apply_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Reset to Default", command=self._reset_to_default).pack(side=tk.LEFT)

        # Store widgets
        self.widgets = {
            'main_frame': main_frame,
            'buttons_frame': buttons_frame
        }

    def _create_detection_tab(self):
        """Create detection settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Detection")

        # Model settings
        model_frame = ttk.LabelFrame(tab, text="Model Configuration", padding=10)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Model Path:").grid(row=0, column=0, sticky="w", pady=2)
        model_entry = ttk.Entry(model_frame, textvariable=self.model_path, width=40)
        model_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))
        ttk.Button(model_frame, text="Browse", command=self._browse_model).grid(row=0, column=2, padx=(5, 0))

        model_frame.grid_columnconfigure(1, weight=1)

        # Detection parameters
        params_frame = ttk.LabelFrame(tab, text="Detection Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=5)

        ttk.Label(params_frame, text="Confidence Threshold:").grid(row=0, column=0, sticky="w", pady=2)
        conf_scale = ttk.Scale(params_frame, from_=0.1, to=0.9, orient=tk.HORIZONTAL,
                               variable=self.conf_threshold, length=200)
        conf_scale.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))
        conf_label = ttk.Label(params_frame, text="0.25")
        conf_label.grid(row=0, column=2, padx=(5, 0))

        ttk.Label(params_frame, text="NMS Threshold:").grid(row=1, column=0, sticky="w", pady=2)
        nms_scale = ttk.Scale(params_frame, from_=0.1, to=0.9, orient=tk.HORIZONTAL,
                              variable=self.nms_threshold, length=200)
        nms_scale.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))
        nms_label = ttk.Label(params_frame, text="0.5")
        nms_label.grid(row=1, column=2, padx=(5, 0))

        params_frame.grid_columnconfigure(1, weight=1)

        # Update labels when scales change
        def update_conf_label(*args):
            conf_label.config(text=f"{self.conf_threshold.get():.2f}")
        def update_nms_label(*args):
            nms_label.config(text=f"{self.nms_threshold.get():.2f}")

        self.conf_threshold.trace('w', update_conf_label)
        self.nms_threshold.trace('w', update_nms_label)

    def _create_tracker_tab(self):
        """Create tracker settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Tracker")

        tracker_frame = ttk.LabelFrame(tab, text="Tracker Parameters", padding=10)
        tracker_frame.pack(fill=tk.X, pady=5)

        ttk.Label(tracker_frame, text="Max Age:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(tracker_frame, from_=1, to=10, textvariable=self.tracker_max_age, width=10).grid(row=0, column=1, sticky="w", pady=2, padx=(5, 0))

        ttk.Label(tracker_frame, text="Min Hits:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Spinbox(tracker_frame, from_=1, to=10, textvariable=self.tracker_min_hits, width=10).grid(row=1, column=1, sticky="w", pady=2, padx=(5, 0))

        ttk.Label(tracker_frame, text="IoU Threshold:").grid(row=2, column=0, sticky="w", pady=2)
        iou_scale = ttk.Scale(tracker_frame, from_=0.1, to=0.8, orient=tk.HORIZONTAL,
                              variable=self.tracker_iou_threshold, length=200)
        iou_scale.grid(row=2, column=1, sticky="ew", pady=2, padx=(5, 0))
        iou_label = ttk.Label(tracker_frame, text="0.3")
        iou_label.grid(row=2, column=2, padx=(5, 0))

        tracker_frame.grid_columnconfigure(1, weight=1)

        def update_iou_label(*args):
            iou_label.config(text=f"{self.tracker_iou_threshold.get():.2f}")

        self.tracker_iou_threshold.trace('w', update_iou_label)

    def _create_storage_tab(self):
        """Create data storage settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Data Storage")

        # Storage enable/disable
        enable_frame = ttk.Frame(tab)
        enable_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(enable_frame, text="Enable Data Storage",
                        variable=self.storage_enabled).pack(side=tk.LEFT)

        # Storage settings
        storage_frame = ttk.LabelFrame(tab, text="Storage Configuration", padding=10)
        storage_frame.pack(fill=tk.X, pady=5)

        ttk.Label(storage_frame, text="Save Interval (seconds):").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Spinbox(storage_frame, from_=30, to=3600, textvariable=self.save_interval, width=10).grid(row=0, column=1, sticky="w", pady=2, padx=(5, 0))

        ttk.Label(storage_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", pady=2)
        dir_entry = ttk.Entry(storage_frame, textvariable=self.output_directory, width=40)
        dir_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))
        ttk.Button(storage_frame, text="Browse", command=self._browse_directory).grid(row=1, column=2, padx=(5, 0))

        ttk.Label(storage_frame, text="Data Format:").grid(row=2, column=0, sticky="w", pady=2)
        format_combo = ttk.Combobox(storage_frame, textvariable=self.data_format,
                                    values=["json", "csv", "both"], state="readonly", width=15)
        format_combo.grid(row=2, column=1, sticky="w", pady=2, padx=(5, 0))

        storage_frame.grid_columnconfigure(1, weight=1)

    def _create_api_tab(self):
        """Create API settings tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="API")

        # API enable/disable
        enable_frame = ttk.Frame(tab)
        enable_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(enable_frame, text="Enable API Sending",
                        variable=self.api_enabled).pack(side=tk.LEFT)

        # API settings
        api_frame = ttk.LabelFrame(tab, text="API Configuration", padding=10)
        api_frame.pack(fill=tk.X, pady=5)

        ttk.Label(api_frame, text="Endpoint URL:").grid(row=0, column=0, sticky="w", pady=2)
        endpoint_entry = ttk.Entry(api_frame, textvariable=self.api_endpoint, width=50)
        endpoint_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(api_frame, text="API Key:").grid(row=1, column=0, sticky="w", pady=2)
        key_entry = ttk.Entry(api_frame, textvariable=self.api_key, width=50, show="*")
        key_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(5, 0))

        ttk.Label(api_frame, text="Send Interval (seconds):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(api_frame, from_=10, to=3600, textvariable=self.api_interval, width=10).grid(row=2, column=1, sticky="w", pady=2, padx=(5, 0))

        ttk.Label(api_frame, text="Timeout (seconds):").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Spinbox(api_frame, from_=5, to=120, textvariable=self.api_timeout, width=10).grid(row=3, column=1, sticky="w", pady=2, padx=(5, 0))

        api_frame.grid_columnconfigure(1, weight=1)

        # Test API button
        test_frame = ttk.Frame(tab)
        test_frame.pack(fill=tk.X, pady=5)

        ttk.Button(test_frame, text="Test API Connection", command=self._test_api).pack(side=tk.LEFT)

        self.api_status_label = ttk.Label(test_frame, text="")
        self.api_status_label.pack(side=tk.LEFT, padx=(10, 0))

    def _setup_layout(self):
        """Setup settings window layout"""
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.widgets['buttons_frame'].pack(fill=tk.X)

    def _browse_model(self):
        """Browse for model file"""
        filetypes = [
            ("OpenVINO models", "*.xml"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=filetypes
        )

        if filename:
            self.model_path.set(filename)

    def _browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )

        if directory:
            self.output_directory.set(directory)

    def _test_api(self):
        """Test API connection"""
        endpoint = self.api_endpoint.get().strip()
        api_key = self.api_key.get().strip()
        timeout = self.api_timeout.get()

        if not endpoint:
            self.api_status_label.config(text="❌ Please enter endpoint URL", foreground="red")
            return

        self.api_status_label.config(text="🔄 Testing...", foreground="blue")
        self.window.update()

        # Test in background thread to avoid blocking UI
        import threading

        def test_connection():
            result = APITester.test_connection(endpoint, api_key, timeout)

            # Update UI in main thread
            self.window.after(0, self._update_api_status, result)

        threading.Thread(target=test_connection, daemon=True).start()

    def _update_api_status(self, result):
        """Update API test status"""
        if result['success']:
            status_text = f"✅ Success ({result['status_code']}) - {result['response_time']:.2f}s"
            color = "green"
        else:
            status_text = f"❌ {result['message']}"
            color = "red"

        self.api_status_label.config(text=status_text, foreground=color)

    def _apply_settings(self):
        """Apply settings without closing window"""
        try:
            # Update configuration
            self.config_manager.update_detection_config(
                model_path=self.model_path.get(),
                conf_threshold=self.conf_threshold.get(),
                nms_threshold=self.nms_threshold.get()
            )

            # Update tracker config
            tracker_config = self.config_manager.config.tracker
            tracker_config.max_age = self.tracker_max_age.get()
            tracker_config.min_hits = self.tracker_min_hits.get()
            tracker_config.iou_threshold = self.tracker_iou_threshold.get()

            # Update storage config
            self.config_manager.update_storage_config(
                enabled=self.storage_enabled.get(),
                save_interval=self.save_interval.get(),
                output_directory=self.output_directory.get(),
                format=self.data_format.get()
            )

            # Update API config
            self.config_manager.update_api_config(
                enabled=self.api_enabled.get(),
                endpoint=self.api_endpoint.get(),
                api_key=self.api_key.get(),
                send_interval=self.api_interval.get(),
                timeout=self.api_timeout.get()
            )

            messagebox.showinfo("Success", "Settings applied successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def _save_settings(self):
        """Save settings and close window"""
        self._apply_settings()
        self.config_manager.save_config()
        self.window.destroy()

    def _cancel(self):
        """Cancel changes and close window"""
        self.window.destroy()

    def _reset_to_default(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Confirm", "Reset all settings to default values?"):
            # Reset to default configuration
            default_config = self.config_manager._load_default_config()
            self.config_manager.config = default_config

            # Update variables
            self._init_variables()

            messagebox.showinfo("Success", "Settings reset to default values!")