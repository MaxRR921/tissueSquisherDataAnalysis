from pyueye import ueye
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
from datetime import datetime
import time
import threading


class UEyeCamera:
    def __init__(self):
        self.hcam = ueye.HIDS(0)
        self.mem_ptr = None
        self.mem_id = None
        self.width = None
        self.height = None
        self.bits_per_pixel = 8

        self.init_camera()

    def check(self, ret, name):
        if ret != ueye.IS_SUCCESS:
            raise RuntimeError(f"{name} failed with error code {ret}")

    def init_camera(self):
        ret = ueye.is_InitCamera(self.hcam, None)
        self.check(ret, "is_InitCamera")

        sensor_info = ueye.SENSORINFO()
        ret = ueye.is_GetSensorInfo(self.hcam, sensor_info)
        self.check(ret, "is_GetSensorInfo")

        self.width = int(sensor_info.nMaxWidth)
        self.height = int(sensor_info.nMaxHeight)

        ret = ueye.is_SetColorMode(self.hcam, ueye.IS_CM_MONO8)
        self.check(ret, "is_SetColorMode")

        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()

        ret = ueye.is_AllocImageMem(
            self.hcam,
            self.width,
            self.height,
            self.bits_per_pixel,
            self.mem_ptr,
            self.mem_id
        )
        self.check(ret, "is_AllocImageMem")

        ret = ueye.is_SetImageMem(self.hcam, self.mem_ptr, self.mem_id)
        self.check(ret, "is_SetImageMem")

        ret = ueye.is_CaptureVideo(self.hcam, ueye.IS_DONT_WAIT)
        self.check(ret, "is_CaptureVideo")

    def set_exposure(self, exposure_ms):
        exposure = ueye.double(float(exposure_ms))
        return ueye.is_Exposure(
            self.hcam,
            ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
            exposure,
            ueye.sizeof(exposure)
        )

    def get_exposure(self):
        exposure = ueye.double(0.0)
        ret = ueye.is_Exposure(
            self.hcam,
            ueye.IS_EXPOSURE_CMD_GET_EXPOSURE,
            exposure,
            ueye.sizeof(exposure)
        )

        if ret == ueye.IS_SUCCESS:
            return float(exposure.value)

        return None

    def set_gain(self, gain):
        gain = max(0, min(100, int(gain)))
        return ueye.is_SetHardwareGain(
            self.hcam,
            gain,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER
        )

    def get_gain(self):
        gain = ueye.is_SetHardwareGain(
            self.hcam,
            ueye.IS_GET_MASTER_GAIN,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER
        )

        if gain >= 0:
            return int(gain)

        return None

    def set_auto_exposure_gain(self, enabled):
        value = ueye.double(1.0 if enabled else 0.0)
        zero = ueye.double(0.0)

        results = []

        if hasattr(ueye, "IS_SET_ENABLE_AUTO_SENSOR_SHUTTER"):
            ret_exposure = ueye.is_SetAutoParameter(
                self.hcam,
                ueye.IS_SET_ENABLE_AUTO_SENSOR_SHUTTER,
                value,
                zero
            )
        else:
            ret_exposure = ueye.IS_NO_SUCCESS

        if ret_exposure != ueye.IS_SUCCESS:
            ret_exposure = ueye.is_SetAutoParameter(
                self.hcam,
                ueye.IS_SET_ENABLE_AUTO_SHUTTER,
                value,
                zero
            )

        if hasattr(ueye, "IS_SET_ENABLE_AUTO_SENSOR_GAIN"):
            ret_gain = ueye.is_SetAutoParameter(
                self.hcam,
                ueye.IS_SET_ENABLE_AUTO_SENSOR_GAIN,
                value,
                zero
            )
        else:
            ret_gain = ueye.IS_NO_SUCCESS

        if ret_gain != ueye.IS_SUCCESS:
            ret_gain = ueye.is_SetAutoParameter(
                self.hcam,
                ueye.IS_SET_ENABLE_AUTO_GAIN,
                value,
                zero
            )

        results.append(("auto exposure", ret_exposure))
        results.append(("auto gain", ret_gain))

        return results

    def set_auto_reference(self, reference_value):
        value = ueye.double(float(reference_value))
        zero = ueye.double(0.0)

        return ueye.is_SetAutoParameter(
            self.hcam,
            ueye.IS_SET_AUTO_REFERENCE,
            value,
            zero
        )

    def get_frame(self):
        frame_data = ueye.get_data(
            self.mem_ptr,
            self.width,
            self.height,
            self.bits_per_pixel,
            self.width,
            copy=True
        )

        frame = np.reshape(frame_data, (self.height, self.width))
        return frame

    def close(self):
        if self.mem_ptr is not None and self.mem_id is not None:
            ueye.is_StopLiveVideo(self.hcam, ueye.IS_FORCE_VIDEO_STOP)
            ueye.is_FreeImageMem(self.hcam, self.mem_ptr, self.mem_id)

        ueye.is_ExitCamera(self.hcam)


class MicroscopeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JDSU FVD-2400 uEye Microscope")

        self.camera = None
        self.current_frame = None
        self.debug_frame = None
        self.photo = None
        self.frame_counter = 0
        self.last_display_time = None
        self.capture_running = False
        self.capture_thread = None
        self.capture_lock = threading.Lock()
        self.camera_io_lock = threading.Lock()
        self.latest_camera_frame = None
        self.latest_camera_time = None
        self.latest_camera_counter = 0
        self.last_displayed_camera_counter = -1
        self.capture_error = None
        self.guide_enabled = False
        self.auto_center_guide = True
        self.manual_guide_center = None
        self.last_guide_center = None
        self.show_rejected_mask = False

        self.display_width = 1024
        self.display_height = 768

        self.exposure_var = tk.DoubleVar(value=20.0)
        self.gain_var = tk.IntVar(value=30)
        self.auto_var = tk.BooleanVar(value=False)
        self.auto_reference_var = tk.DoubleVar(value=128.0)
        self.guide_low_threshold_var = tk.IntVar(value=80)
        self.guide_high_threshold_var = tk.IntVar(value=100)
        self.guide_radius_var = tk.IntVar(value=154)
        self.bowtie_outer_radius_var = tk.IntVar(value=50)
        self.bowtie_inner_radius_var = tk.IntVar(value=15)
        self.bowtie_sweep_angle_var = tk.DoubleVar(value=75.0)
        self.fiber_angle_var = tk.DoubleVar(value=45)
        self.status_var = tk.StringVar(value="Starting")
        self.frame_timer_var = tk.StringVar(value="Frame delay: --")

        try:
            self.camera = UEyeCamera()
            self.camera.set_exposure(self.exposure_var.get())
            self.camera.set_gain(self.gain_var.get())
            self.status_var.set("Camera connected")
        except Exception as e:
            self.camera = None
            self.status_var.set(f"No camera detected. Open an image to debug. {e}")

        self.build_gui()

        if self.camera is not None:
            self.start_capture_thread()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_frame()

    def build_gui(self):
        self.root.geometry("1360x860")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=4)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=0)

        image_frame = ttk.Frame(
            main_frame,
            width=self.display_width,
            height=self.display_height
        )
        image_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        image_frame.grid_propagate(False)

        self.image_label = tk.Label(image_frame, bg="black")
        self.image_label.place(x=0, y=0, width=self.display_width, height=self.display_height)
        self.image_label.bind("<Button-1>", self.on_image_click)
        self.show_placeholder_frame()

        frame_timer_label = ttk.Label(main_frame, textvariable=self.frame_timer_var)
        frame_timer_label.grid(row=1, column=0, sticky="sw", padx=5, pady=(0, 5))

        settings_frame = ttk.Frame(main_frame)
        settings_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.rowconfigure(8, weight=1)

        guide_radius_label = ttk.Label(settings_frame, text="Guide radius")
        guide_radius_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        guide_radius_entry = ttk.Entry(
            settings_frame,
            textvariable=self.guide_radius_var,
            width=8
        )
        guide_radius_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        bowtie_outer_label = ttk.Label(settings_frame, text="Bowtie outer radius")
        bowtie_outer_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        bowtie_outer_entry = ttk.Entry(
            settings_frame,
            textvariable=self.bowtie_outer_radius_var,
            width=8
        )
        bowtie_outer_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        bowtie_inner_label = ttk.Label(settings_frame, text="Bowtie inner radius")
        bowtie_inner_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        bowtie_inner_entry = ttk.Entry(
            settings_frame,
            textvariable=self.bowtie_inner_radius_var,
            width=8
        )
        bowtie_inner_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        bowtie_sweep_label = ttk.Label(settings_frame, text="Bowtie sweep angle")
        bowtie_sweep_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        bowtie_sweep_entry = ttk.Entry(
            settings_frame,
            textvariable=self.bowtie_sweep_angle_var,
            width=8
        )
        bowtie_sweep_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        fiber_angle_label = ttk.Label(settings_frame, text="Fiber angle")
        fiber_angle_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        fiber_angle_entry = ttk.Entry(
            settings_frame,
            textvariable=self.fiber_angle_var,
            width=8
        )
        fiber_angle_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        reticle_button_frame = ttk.Frame(settings_frame)
        reticle_button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=5, pady=(15, 5))

        guide_button = ttk.Button(reticle_button_frame, text="toggle guide", command=self.toggle_guide)
        guide_button.pack(side="left", padx=(0, 5))

        self.auto_center_button = ttk.Button(
            reticle_button_frame,
            text="Auto center guide: on",
            command=self.toggle_auto_center_guide
        )
        self.auto_center_button.pack(side="left", padx=5)

        image_button_frame = ttk.Frame(settings_frame)
        image_button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        save_button = ttk.Button(image_button_frame, text="Save Frame", command=self.save_frame)
        save_button.pack(side="left", padx=(0, 5))

        open_image_button = ttk.Button(
            image_button_frame,
            text="Open Image",
            command=self.open_image
        )
        open_image_button.pack(side="left", padx=5)

        quit_button = ttk.Button(settings_frame, text="Quit", command=self.on_close)
        quit_button.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=(15, 5))

        sliders_frame = ttk.Frame(settings_frame)
        sliders_frame.grid(row=8, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)
        sliders_frame.columnconfigure(1, weight=1)

        auto_check = ttk.Checkbutton(
            sliders_frame,
            text="Auto exposure/gain",
            variable=self.auto_var,
            command=self.on_auto_change
        )
        auto_check.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        auto_ref_label = ttk.Label(sliders_frame, text="Auto target")
        auto_ref_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        auto_ref_slider = ttk.Scale(
            sliders_frame,
            from_=40,
            to=220,
            variable=self.auto_reference_var,
            command=self.on_auto_reference_change
        )
        auto_ref_slider.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        self.auto_ref_value_label = ttk.Label(sliders_frame, text="128")
        self.auto_ref_value_label.grid(row=1, column=2, sticky="e", padx=5, pady=5)

        exposure_label = ttk.Label(sliders_frame, text="Exposure (ms)")
        exposure_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        self.exposure_slider = ttk.Scale(
            sliders_frame,
            from_=0.1,
            to=100.0,
            variable=self.exposure_var,
            command=self.on_exposure_change
        )
        self.exposure_slider.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.exposure_value_label = ttk.Label(sliders_frame, text="20.0")
        self.exposure_value_label.grid(row=2, column=2, sticky="e", padx=5, pady=5)

        gain_label = ttk.Label(sliders_frame, text="Gain")
        gain_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)

        self.gain_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=100,
            variable=self.gain_var,
            command=self.on_gain_change
        )
        self.gain_slider.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        self.gain_value_label = ttk.Label(sliders_frame, text="30")
        self.gain_value_label.grid(row=3, column=2, sticky="e", padx=5, pady=5)

        guide_low_label = ttk.Label(sliders_frame, text="Guide dark cutoff")
        guide_low_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        self.guide_low_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=255,
            variable=self.guide_low_threshold_var,
            command=self.on_guide_threshold_change
        )
        self.guide_low_slider.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        self.guide_low_slider.bind("<ButtonPress-1>", self.show_mask_preview)
        self.guide_low_slider.bind("<ButtonRelease-1>", self.hide_mask_preview)

        self.guide_low_value_label = ttk.Label(sliders_frame, text="50")
        self.guide_low_value_label.grid(row=4, column=2, sticky="e", padx=5, pady=5)

        guide_high_label = ttk.Label(sliders_frame, text="Guide bright cutoff")
        guide_high_label.grid(row=5, column=0, sticky="w", padx=5, pady=5)

        self.guide_high_slider = ttk.Scale(
            sliders_frame,
            from_=0,
            to=255,
            variable=self.guide_high_threshold_var,
            command=self.on_guide_threshold_change
        )
        self.guide_high_slider.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        self.guide_high_slider.bind("<ButtonPress-1>", self.show_mask_preview)
        self.guide_high_slider.bind("<ButtonRelease-1>", self.hide_mask_preview)
        self.root.bind_all("<ButtonRelease-1>", self.hide_mask_preview)

        self.guide_high_value_label = ttk.Label(sliders_frame, text="130")
        self.guide_high_value_label.grid(row=5, column=2, sticky="e", padx=5, pady=5)

        status_label = ttk.Label(sliders_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def on_auto_change(self):
        if self.camera is None:
            self.status_var.set("No camera detected")
            return

        enabled = self.auto_var.get()

        with self.camera_io_lock:
            self.camera.set_auto_reference(self.auto_reference_var.get())
            results = self.camera.set_auto_exposure_gain(enabled)

        if enabled:
            self.exposure_slider.state(["disabled"])
            self.gain_slider.state(["disabled"])
        else:
            self.exposure_slider.state(["!disabled"])
            self.gain_slider.state(["!disabled"])

        result_text = ", ".join([f"{name}: {ret}" for name, ret in results])

        if enabled:
            self.status_var.set(f"Auto enabled. {result_text}")
        else:
            self.status_var.set(f"Auto disabled. {result_text}")

    def on_auto_reference_change(self, value):
        reference = float(value)
        self.auto_ref_value_label.config(text=f"{reference:.0f}")

        if self.auto_var.get() and self.camera is not None:
            with self.camera_io_lock:
                ret = self.camera.set_auto_reference(reference)
            self.status_var.set(f"Auto target set to {reference:.0f}, ret={ret}")

    def on_exposure_change(self, value):
        if self.auto_var.get() or self.camera is None:
            return

        exposure = float(value)
        self.exposure_value_label.config(text=f"{exposure:.1f}")
        with self.camera_io_lock:
            ret = self.camera.set_exposure(exposure)

        if ret == ueye.IS_SUCCESS:
            self.status_var.set(f"Exposure set to {exposure:.1f} ms")
        else:
            self.status_var.set(f"Exposure change failed: error {ret}")

    def on_gain_change(self, value):
        if self.auto_var.get() or self.camera is None:
            return

        gain = int(float(value))
        self.gain_value_label.config(text=str(gain))
        with self.camera_io_lock:
            ret = self.camera.set_gain(gain)

        if ret == ueye.IS_SUCCESS:
            self.status_var.set(f"Gain set to {gain}")
        else:
            self.status_var.set(f"Gain change failed: error {ret}")

    def on_guide_threshold_change(self, value):
        low = int(self.guide_low_threshold_var.get())
        high = int(self.guide_high_threshold_var.get())

        self.guide_low_value_label.config(text=str(low))
        self.guide_high_value_label.config(text=str(high))

        if self.guide_enabled:
            self.status_var.set(f"Guide thresholds {low}-{high}")

    def update_auto_slider_values(self):
        if self.camera is None:
            return

        with self.camera_io_lock:
            exposure = self.camera.get_exposure()
            gain = self.camera.get_gain()

        if exposure is not None:
            exposure = max(0.1, min(100.0, exposure))
            self.exposure_var.set(exposure)
            self.exposure_value_label.config(text=f"{exposure:.1f}")

        if gain is not None:
            gain = max(0, min(100, gain))
            self.gain_var.set(gain)
            self.gain_value_label.config(text=str(gain))

    def start_capture_thread(self):
        if self.capture_thread is not None:
            return

        self.capture_running = True
        self.capture_thread = threading.Thread(
            target=self.capture_loop,
            daemon=True
        )
        self.capture_thread.start()

    def capture_loop(self):
        while self.capture_running:
            try:
                with self.camera_io_lock:
                    frame = self.camera.get_frame()
                capture_time = time.perf_counter()

                with self.capture_lock:
                    self.latest_camera_frame = frame
                    self.latest_camera_time = capture_time
                    self.latest_camera_counter += 1
                    self.capture_error = None
            except Exception as e:
                with self.capture_lock:
                    self.capture_error = str(e)

                time.sleep(0.05)
                continue

            time.sleep(0.001)

    def get_latest_camera_frame(self):
        with self.capture_lock:
            return (
                self.latest_camera_frame,
                self.latest_camera_time,
                self.latest_camera_counter,
                self.capture_error
            )

    def toggle_guide(self):
        self.guide_enabled = not self.guide_enabled
        state = "enabled" if self.guide_enabled else "disabled"
        self.status_var.set(f"Guide {state}")

    def toggle_auto_center_guide(self):
        self.auto_center_guide = not self.auto_center_guide

        if self.auto_center_guide:
            self.auto_center_button.config(text="Auto center guide: on")
            self.status_var.set("Guide auto centering enabled")
            return

        if self.last_guide_center is not None:
            self.manual_guide_center = self.last_guide_center
        elif self.current_frame is not None:
            display_frame = cv2.resize(
                self.current_frame,
                (self.display_width, self.display_height)
            ).astype(np.uint8)
            self.manual_guide_center = self.find_largest_circle(display_frame)

        if self.manual_guide_center is None:
            self.manual_guide_center = (
                self.display_width // 2,
                self.display_height // 2
            )

        self.auto_center_button.config(text="Auto center guide: off")
        self.status_var.set("Guide auto centering disabled")

    def on_image_click(self, event):
        if self.auto_center_guide:
            return

        x = max(0, min(self.display_width - 1, int(event.x)))
        y = max(0, min(self.display_height - 1, int(event.y)))
        self.manual_guide_center = (x, y)
        self.last_guide_center = self.manual_guide_center
        self.status_var.set(f"Guide center set to {x}, {y}")

    def show_mask_preview(self, event):
        self.show_rejected_mask = True

    def hide_mask_preview(self, event):
        self.show_rejected_mask = False

    def get_guide_thresholds(self):
        low = int(self.guide_low_threshold_var.get())
        high = int(self.guide_high_threshold_var.get())

        if low > high:
            low, high = high, low

        return low, high

    def find_largest_circle(self, grayscale_frame):
        frame = grayscale_frame.astype(np.uint8)
        blurred = cv2.GaussianBlur(frame, (9, 9), 0)

        low, high = self.get_guide_thresholds()
        mask = cv2.inRange(blurred, low, high)

        kernel_size = max(3, min(frame.shape[:2]) // 80)
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        min_area = frame.shape[0] * frame.shape[1] * 0.01
        max_width = frame.shape[1] * 0.95
        max_height = frame.shape[0] * 0.95

        candidate_contours = []

        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, width, height = cv2.boundingRect(contour)

            if area < min_area:
                continue

            touches_edges = sum([
                x <= 1,
                y <= 1,
                x + width >= frame.shape[1] - 1,
                y + height >= frame.shape[0] - 1
            ])

            if touches_edges >= 2:
                continue

            if width >= max_width and height >= max_height:
                continue

            candidate_contours.append(contour)

        if not candidate_contours:
            return None

        largest_contour = max(candidate_contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(largest_contour)

        if radius <= 0:
            return None

        return int(round(x)), int(round(y))

    def draw_rejected_mask(self, display_frame):
        low, high = self.get_guide_thresholds()
        blurred = cv2.GaussianBlur(display_frame, (9, 9), 0)
        accepted_mask = cv2.inRange(blurred, low, high)
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2RGB)
        display_frame[accepted_mask == 0] = (0, 180, 255)

        return display_frame

    def bowtie_point(self, x, y, radius, angle_degrees):
        angle = np.deg2rad(angle_degrees)
        return [
            int(round(x + radius * np.cos(angle))),
            int(round(y - radius * np.sin(angle)))
        ]

    def draw_bowtie_side(
            self,
            display_frame,
            x,
            y,
            inner_radius,
            outer_radius,
            center_angle,
            sweep_angle):
        half_sweep = sweep_angle / 2.0
        start_angle = center_angle - half_sweep
        end_angle = center_angle + half_sweep
        steps = max(8, int(abs(sweep_angle) / 4))

        outer_angles = np.linspace(start_angle, end_angle, steps)
        inner_angles = np.linspace(end_angle, start_angle, steps)

        points = [
            self.bowtie_point(x, y, outer_radius, angle)
            for angle in outer_angles
        ]
        points.extend([
            self.bowtie_point(x, y, inner_radius, angle)
            for angle in inner_angles
        ])

        cv2.polylines(
            display_frame,
            [np.array(points, dtype=np.int32)],
            True,
            (255, 0, 0),
            1
        )

    def draw_bowtie(self, display_frame, x, y):
        try:
            outer_radius = max(1, int(self.bowtie_outer_radius_var.get()))
            inner_radius = max(1, int(self.bowtie_inner_radius_var.get()))
            sweep_angle = max(0.0, min(180.0, float(self.bowtie_sweep_angle_var.get())))
            fiber_angle = float(self.fiber_angle_var.get())
        except tk.TclError:
            return display_frame

        if inner_radius >= outer_radius or sweep_angle <= 0:
            return display_frame

        self.draw_bowtie_side(
            display_frame,
            x,
            y,
            inner_radius,
            outer_radius,
            fiber_angle,
            sweep_angle
        )
        self.draw_bowtie_side(
            display_frame,
            x,
            y,
            inner_radius,
            outer_radius,
            fiber_angle + 180.0,
            sweep_angle
        )

        return display_frame

    def get_guide_center(self, source_frame):
        if self.auto_center_guide:
            center = self.find_largest_circle(source_frame)

            if center is not None:
                self.last_guide_center = center

            return center

        return self.manual_guide_center

    def draw_guide(self, display_frame, source_frame=None):
        if source_frame is None:
            source_frame = display_frame

        if len(display_frame.shape) == 2:
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2RGB)

        center = self.get_guide_center(source_frame)

        if center is None:
            return display_frame

        x, y = center

        try:
            radius = max(1, int(self.guide_radius_var.get()))
        except tk.TclError:
            return display_frame

        cv2.circle(display_frame, (x, y), radius, (255, 0, 0), 1)
        cv2.circle(display_frame, (x, y), 4, (255, 0, 0), -1)
        display_frame = self.draw_bowtie(display_frame, x, y)

        return display_frame

    def show_placeholder_frame(self):
        placeholder = np.full(
            (self.display_height, self.display_width),
            32,
            dtype=np.uint8
        )
        message = "No camera. Open an image to debug."
        text_size, _ = cv2.getTextSize(
            message,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            2
        )
        text_x = max(0, (self.display_width - text_size[0]) // 2)
        text_y = self.display_height // 2

        cv2.putText(
            placeholder,
            message,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            180,
            2,
            cv2.LINE_AA
        )

        image = Image.fromarray(placeholder, mode="L")
        self.photo = ImageTk.PhotoImage(image=image)
        self.image_label.configure(image=self.photo)

    def update_frame(self):
        update_start = time.perf_counter()
        source_age_ms = None

        try:
            if self.debug_frame is None:
                if self.camera is None:
                    self.frame_timer_var.set("Frame delay: waiting for camera/image")
                    self.root.after(100, self.update_frame)
                    return

                (
                    camera_frame,
                    camera_time,
                    camera_counter,
                    capture_error
                ) = self.get_latest_camera_frame()

                if capture_error is not None:
                    self.status_var.set(f"Capture error: {capture_error}")

                if camera_frame is None:
                    self.frame_timer_var.set("Frame delay: waiting for camera frame")
                    self.root.after(5, self.update_frame)
                    return

                self.current_frame = camera_frame
                self.last_displayed_camera_counter = camera_counter

                if camera_time is not None:
                    source_age_ms = (update_start - camera_time) * 1000.0
            else:
                self.current_frame = self.debug_frame

            if self.current_frame.shape[:2] == (self.display_height, self.display_width):
                display_frame = self.current_frame
            else:
                display_frame = cv2.resize(
                    self.current_frame,
                    (self.display_width, self.display_height)
                )

            display_frame = display_frame.astype(np.uint8, copy=False)

            source_frame = display_frame

            if self.show_rejected_mask:
                display_frame = self.draw_rejected_mask(display_frame)

            if self.guide_enabled:
                display_frame = self.draw_guide(display_frame, source_frame)
                image = Image.fromarray(display_frame, mode="RGB")
            elif self.show_rejected_mask:
                image = Image.fromarray(display_frame, mode="RGB")
            else:
                image = Image.fromarray(display_frame, mode="L")

            self.photo = ImageTk.PhotoImage(image=image)
            self.image_label.configure(image=self.photo)

            self.frame_counter += 1
            display_time = time.perf_counter()
            update_ms = (display_time - update_start) * 1000.0

            if self.last_display_time is None:
                frame_text = "Frame delay: --"
            else:
                frame_ms = (display_time - self.last_display_time) * 1000.0
                fps = 1000.0 / frame_ms if frame_ms > 0 else 0.0
                frame_text = f"Frame delay: {frame_ms:.1f} ms ({fps:.1f} fps)"

            if source_age_ms is None:
                age_text = "source age: image"
            else:
                age_text = f"source age: {source_age_ms:.1f} ms"

            self.frame_timer_var.set(
                f"{frame_text} | {age_text} | update: {update_ms:.1f} ms"
            )

            self.last_display_time = display_time

            if self.auto_var.get() and self.frame_counter % 10 == 0:
                self.update_auto_slider_values()

        except Exception as e:
            self.status_var.set(f"Frame update error: {e}")

        self.root.after(30, self.update_frame)

    def open_image(self):
        filename = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("All files", "*.*")
            ]
        )

        if not filename:
            return

        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

        if image is None:
            self.status_var.set(f"Could not open {filename}")
            return

        self.debug_frame = image
        self.current_frame = image
        self.status_var.set(f"Opened {filename}")

    def save_frame(self):
        if self.current_frame is None:
            self.status_var.set("No frame to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fiber_frame_{timestamp}.png"

        cv2.imwrite(filename, self.current_frame)
        self.status_var.set(f"Saved {filename}")

    def on_close(self):
        try:
            self.capture_running = False

            if self.capture_thread is not None:
                self.capture_thread.join(timeout=0.5)

            if self.camera is not None:
                with self.camera_io_lock:
                    self.camera.close()
        finally:
            self.root.destroy()


def main():
    root = tk.Tk()
    app = MicroscopeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
