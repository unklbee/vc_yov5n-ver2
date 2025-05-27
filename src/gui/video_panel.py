"""
src/gui/video_panel.py
Video display panel with drawing capabilities
"""

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
from typing import List, Tuple, Callable, Optional


class VideoPanel(ttk.Frame):
    """Video display panel with ROI and line drawing capabilities"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Drawing state
        self.drawing_mode = None  # None, 'roi', 'line'
        self.roi_points = []
        self.temp_line_points = []
        self.current_frame = None
        self.display_frame = None

        # Callbacks
        self.roi_callback = None
        self.line_callback = None
        self.clear_callback = None

        # Scale factor for display
        self.scale_factor = 1.0
        self.display_size = (640, 480)

        self._create_widgets()
        self._setup_layout()
        self._bind_events()

    def _create_widgets(self):
        """Create video panel widgets"""
        # Toolbar
        self.toolbar = ttk.Frame(self)

        self.roi_button = ttk.Button(
            self.toolbar,
            text="Draw ROI",
            command=self._start_roi_drawing
        )
        self.roi_button.pack(side=tk.LEFT, padx=2)

        self.line_button = ttk.Button(
            self.toolbar,
            text="Draw Line",
            command=self._start_line_drawing
        )
        self.line_button.pack(side=tk.LEFT, padx=2)

        self.clear_button = ttk.Button(
            self.toolbar,
            text="Clear All",
            command=self._clear_annotations
        )
        self.clear_button.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        self.mode_label = ttk.Label(self.toolbar, text="Mode: View")
        self.mode_label.pack(side=tk.LEFT, padx=5)

        # Video display area
        self.video_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=2)

        self.canvas = tk.Canvas(
            self.video_frame,
            bg='black',
            width=640,
            height=480
        )

        # Scrollbars
        self.h_scrollbar = ttk.Scrollbar(self.video_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scrollbar = ttk.Scrollbar(self.video_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # Info panel
        self.info_panel = ttk.Frame(self)

        self.info_text = tk.Text(
            self.info_panel,
            height=6,
            width=30,
            state=tk.DISABLED,
            wrap=tk.WORD
        )

        info_scrollbar = ttk.Scrollbar(self.info_panel, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)

    def _setup_layout(self):
        """Setup panel layout"""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Place widgets
        self.toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.video_frame.grid(row=1, column=0, sticky="nsew", columnspan=2)
        self.info_panel.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # Video frame layout
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        # Info panel layout
        self.info_panel.grid_columnconfigure(0, weight=1)
        self.info_text.grid(row=0, column=0, sticky="nsew")
        info_scrollbar.grid(row=0, column=1, sticky="ns")

    def _bind_events(self):
        """Bind mouse events for drawing"""
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _start_roi_drawing(self):
        """Start ROI drawing mode"""
        self.drawing_mode = 'roi'
        self.roi_points = []
        self.mode_label.config(text="Mode: Drawing ROI (Left click: add point, Right click: finish)")
        self._update_button_states()

    def _start_line_drawing(self):
        """Start line drawing mode"""
        self.drawing_mode = 'line'
        self.temp_line_points = []
        self.mode_label.config(text="Mode: Drawing Line (Click two points)")
        self._update_button_states()

    def _clear_annotations(self):
        """Clear all annotations"""
        self.drawing_mode = None
        self.roi_points = []
        self.temp_line_points = []
        self.mode_label.config(text="Mode: View")
        self._update_button_states()

        if self.clear_callback:
            self.clear_callback()

        # Redraw frame without annotations
        if self.current_frame is not None:
            self.update_frame(self.current_frame)

    def _update_button_states(self):
        """Update button states based on current mode"""
        if self.drawing_mode == 'roi':
            self.roi_button.config(state=tk.DISABLED)
            self.line_button.config(state=tk.DISABLED)
        elif self.drawing_mode == 'line':
            self.roi_button.config(state=tk.DISABLED)
            self.line_button.config(state=tk.DISABLED)
        else:
            self.roi_button.config(state=tk.NORMAL)
            self.line_button.config(state=tk.NORMAL)

    def _on_left_click(self, event):
        """Handle left mouse click"""
        if self.drawing_mode is None:
            return

        # Convert canvas coordinates to image coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        # Scale to original image coordinates
        img_x = int(canvas_x / self.scale_factor)
        img_y = int(canvas_y / self.scale_factor)

        if self.drawing_mode == 'roi':
            self.roi_points.append((img_x, img_y))
            self._update_display_with_drawings()
            self._update_info_text(f"ROI point {len(self.roi_points)}: ({img_x}, {img_y})")

        elif self.drawing_mode == 'line':
            self.temp_line_points.append((img_x, img_y))
            self._update_display_with_drawings()
            self._update_info_text(f"Line point {len(self.temp_line_points)}: ({img_x}, {img_y})")

            if len(self.temp_line_points) == 2:
                # Line complete
                if self.line_callback:
                    self.line_callback(self.temp_line_points[0], self.temp_line_points[1])

                self.drawing_mode = None
                self.temp_line_points = []
                self.mode_label.config(text="Mode: View")
                self._update_button_states()
                self._update_info_text("Line drawing completed")

    def _on_right_click(self, event):
        """Handle right mouse click"""
        if self.drawing_mode == 'roi' and len(self.roi_points) >= 3:
            # Complete ROI
            if self.roi_callback:
                self.roi_callback(self.roi_points)

            self.drawing_mode = None
            self.mode_label.config(text="Mode: View")
            self._update_button_states()
            self._update_info_text("ROI drawing completed")

    def _on_mouse_move(self, event):
        """Handle mouse movement for live drawing feedback"""
        if self.drawing_mode is None or self.current_frame is None:
            return

        # Update display with current mouse position
        self._update_display_with_drawings(event)

    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        if self.current_frame is not None:
            self._resize_and_display_frame()

    def update_frame(self, frame):
        """Update video frame"""
        self.current_frame = frame.copy()
        self._resize_and_display_frame()

    def _resize_and_display_frame(self):
        """Resize frame to fit canvas and display"""
        if self.current_frame is None:
            return

        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        # Calculate scale factor
        frame_height, frame_width = self.current_frame.shape[:2]

        scale_x = canvas_width / frame_width
        scale_y = canvas_height / frame_height
        self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't upscale

        # Calculate display size
        self.display_size = (
            int(frame_width * self.scale_factor),
            int(frame_height * self.scale_factor)
        )

        # Resize frame
        self.display_frame = cv2.resize(self.current_frame, self.display_size)

        self._display_frame_on_canvas()

    def _display_frame_on_canvas(self):
        """Display frame on canvas"""
        if self.display_frame is None:
            return

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(self.display_frame, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        self.photo = ImageTk.PhotoImage(pil_image)

        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Add drawings if in drawing mode
        if self.drawing_mode:
            self._draw_annotations_on_canvas()

    def _update_display_with_drawings(self, mouse_event=None):
        """Update display with current drawings"""
        if self.current_frame is None:
            return

        # Create a copy of the frame for drawing
        frame_copy = self.current_frame.copy()

        # Draw ROI points and lines
        if self.drawing_mode == 'roi' and self.roi_points:
            for i, point in enumerate(self.roi_points):
                cv2.circle(frame_copy, point, 5, (0, 255, 0), -1)
                if i > 0:
                    cv2.line(frame_copy, self.roi_points[i-1], point, (0, 255, 0), 2)

            # Draw line from last point to mouse if provided
            if mouse_event and len(self.roi_points) > 0:
                canvas_x = self.canvas.canvasx(mouse_event.x)
                canvas_y = self.canvas.canvasy(mouse_event.y)
                img_x = int(canvas_x / self.scale_factor)
                img_y = int(canvas_y / self.scale_factor)
                cv2.line(frame_copy, self.roi_points[-1], (img_x, img_y), (0, 255, 0), 1)

        # Draw line points
        if self.drawing_mode == 'line' and self.temp_line_points:
            for point in self.temp_line_points:
                cv2.circle(frame_copy, point, 5, (0, 255, 255), -1)

            if len(self.temp_line_points) == 1 and mouse_event:
                canvas_x = self.canvas.canvasx(mouse_event.x)
                canvas_y = self.canvas.canvasy(mouse_event.y)
                img_x = int(canvas_x / self.scale_factor)
                img_y = int(canvas_y / self.scale_factor)
                cv2.line(frame_copy, self.temp_line_points[0], (img_x, img_y), (0, 255, 255), 1)

        # Update display
        self.current_frame = frame_copy
        self._resize_and_display_frame()

    def _draw_annotations_on_canvas(self):
        """Draw annotations directly on canvas"""
        # This is called after the image is displayed to add overlay graphics
        pass

    def _update_info_text(self, message: str):
        """Update info text panel"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.insert(tk.END, f"{message}\n")
        self.info_text.see(tk.END)
        self.info_text.config(state=tk.DISABLED)

        # Limit text length
        lines = self.info_text.get("1.0", tk.END).split('\n')
        if len(lines) > 20:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete("1.0", "5.0")
            self.info_text.config(state=tk.DISABLED)

    def set_roi_callback(self, callback: Callable[[List[Tuple[int, int]]], None]):
        """Set ROI completion callback"""
        self.roi_callback = callback

    def set_line_callback(self, callback: Callable[[Tuple[int, int], Tuple[int, int]], None]):
        """Set line completion callback"""
        self.line_callback = callback

    def set_clear_callback(self, callback: Callable[[], None]):
        """Set clear annotations callback"""
        self.clear_callback = callback