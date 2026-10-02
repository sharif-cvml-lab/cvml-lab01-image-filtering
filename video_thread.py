from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage

from config import (
    CAPTURE_HEIGHT,
    CAPTURE_WIDTH,
    DEFAULT_AVERAGING_KERNEL,
    DEFAULT_CANNY_THRESHOLD,
    DEFAULT_EDGE_MODE,
    DEFAULT_GAUSSIAN_KERNEL,
    DEFAULT_GAUSSIAN_SIGMA_TENTHS,
    DEFAULT_SOBEL_THRESHOLD,
    DEFAULT_BLUR_MODE,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    FilterParameters,
    TARGET_FPS,
)
from filters import (
    apply_averaging_blur,
    apply_canny_edge,
    apply_gaussian_blur,
    apply_sobel_edge,
)


class VideoThread(QThread):
    """Capture a webcam/file source and process frames off the GUI thread."""

    frame_ready = pyqtSignal(object, object, object, float)
    status_changed = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, source_type: str = "camera", file_path: str = "", parent=None):
        super().__init__(parent)
        self._camera_index = int(camera_index)
        self._source_type = source_type
        self._file_path = file_path
        self._parameters = FilterParameters(
            blur_mode=DEFAULT_BLUR_MODE,
            gaussian_kernel=DEFAULT_GAUSSIAN_KERNEL,
            gaussian_sigma=DEFAULT_GAUSSIAN_SIGMA_TENTHS / 10.0,
            averaging_kernel=DEFAULT_AVERAGING_KERNEL,
            edge_mode=DEFAULT_EDGE_MODE,
            sobel_threshold=DEFAULT_SOBEL_THRESHOLD,
            canny_threshold=DEFAULT_CANNY_THRESHOLD,
        )
        self._lock = threading.Lock()
        self._running = threading.Event()
        self._running.set()
        self._paused = False
        self._restart_requested = True
        self._last_status = ""

    def set_parameters(self, parameters: FilterParameters) -> None:
        with self._lock:
            self._parameters = parameters

    def set_paused(self, paused: bool) -> None:
        with self._lock:
            self._paused = bool(paused)

    def restart_source(self) -> None:
        with self._lock:
            self._restart_requested = True
            self._paused = False

    def run(self) -> None:
        cap = None
        image_frame = None
        current_frame = None
        video_ended = False
        active_path = ""
        active_source = ""
        previous_time = time.perf_counter()
        fps = 0.0
        frame_counter = 0
        fps_window_start = previous_time

        try:
            while self._running.is_set():
                source_type, source_path, camera_index, parameters, paused, restart = self._snapshot()

                if restart or source_type != active_source or source_path != active_path:
                    if cap is not None:
                        cap.release()
                        cap = None
                    image_frame = None
                    current_frame = None
                    video_ended = False
                    active_source = source_type
                    active_path = source_path
                    self._clear_restart_flag()

                    if source_type == "camera":
                        cap = cv2.VideoCapture(camera_index)
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
                        if not cap.isOpened():
                            cap.release()
                            cap = None
                            self._emit_status(
                                f"Camera {camera_index} is unavailable. Check the camera connection or select another index."
                            )
                        else:
                            self._emit_status(f"Camera {camera_index} connected.")
                    elif source_type == "file":
                        if not source_path:
                            self._emit_status("No file selected. Click Browse, then Upload.")
                        elif not os.path.isfile(source_path):
                            self._emit_status(f"File not found: {source_path}")
                        else:
                            suffix = Path(source_path).suffix.lower()
                            if suffix in IMAGE_EXTENSIONS:
                                image_frame = cv2.imread(source_path, cv2.IMREAD_COLOR)
                                if image_frame is None:
                                    self._emit_status("The selected image could not be opened.")
                                else:
                                    current_frame = image_frame.copy()
                                    self._emit_status(f"Image loaded: {Path(source_path).name}")
                            elif suffix in VIDEO_EXTENSIONS:
                                cap = cv2.VideoCapture(source_path)
                                if not cap.isOpened():
                                    cap.release()
                                    cap = None
                                    self._emit_status("The selected video could not be opened.")
                                else:
                                    self._emit_status(f"Video loaded: {Path(source_path).name}")
                            else:
                                self._emit_status("Unsupported file type. Please choose a supported image or video.")

                if source_type == "camera":
                    if cap is None:
                        time.sleep(0.25)
                        continue
                    if not paused:
                        ret, frame = cap.read()
                        if not ret:
                            self._emit_status(
                                "The camera stopped providing frames. Press Restart or check the camera connection."
                            )
                            time.sleep(0.1)
                            continue
                        current_frame = frame

                elif source_type == "file":
                    if image_frame is not None:
                        current_frame = image_frame
                    elif cap is not None and not paused and not video_ended:
                        ret, frame = cap.read()
                        if not ret:
                            video_ended = True
                            self._emit_status("Video finished. Press Restart to play it again.")
                        else:
                            current_frame = frame

                if current_frame is None:
                    time.sleep(0.05)
                    continue

                original = current_frame.copy()
                blurred = self._safe_blur(original, parameters)
                edge = self._safe_edge(original, parameters)

                try:
                    qt_original = self.convert_cv_qt(original)
                    qt_blurred = self.convert_cv_qt(blurred)
                    qt_edge = self.convert_cv_qt(edge)
                except Exception as exc:
                    self._emit_status(f"Display conversion error: {exc}. Skipping the current frame.")
                    time.sleep(0.05)
                    continue

                now = time.perf_counter()
                frame_counter += 1
                elapsed = now - fps_window_start
                if elapsed >= 0.5:
                    fps = frame_counter / elapsed
                    frame_counter = 0
                    fps_window_start = now

                self.frame_ready.emit(qt_original, qt_blurred, qt_edge, fps)

                processing_period = 1.0 / TARGET_FPS
                sleep_time = processing_period - (time.perf_counter() - previous_time)
                previous_time = time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)

        finally:
            if cap is not None:
                cap.release()

    def _snapshot(self):
        with self._lock:
            return (
                self._source_type,
                self._file_path,
                self._camera_index,
                self._parameters,
                self._paused,
                self._restart_requested,
            )

    def _clear_restart_flag(self) -> None:
        with self._lock:
            self._restart_requested = False

    def _emit_status(self, message: str) -> None:
        if message != self._last_status:
            self._last_status = message
            self.status_changed.emit(message)

    def _safe_blur(self, frame: np.ndarray, parameters: FilterParameters) -> np.ndarray:
        try:
            if parameters.blur_mode == "Gaussian":
                result = apply_gaussian_blur(
                    frame,
                    self._safe_odd_kernel(parameters.gaussian_kernel),
                    max(0.0, float(parameters.gaussian_sigma)),
                )
            else:
                result = apply_averaging_blur(frame, max(1, int(parameters.averaging_kernel)))
            if self._is_valid_image(result):
                return result
            raise ValueError("the filter returned an invalid image")
        except Exception as exc:
            self._emit_status(f"Blur processing error: {exc}. Showing the original frame.")
            return frame

    def _safe_edge(self, frame: np.ndarray, parameters: FilterParameters) -> np.ndarray:
        try:
            if parameters.edge_mode == "Sobel":
                result = apply_sobel_edge(frame, int(np.clip(parameters.sobel_threshold, 0, 255)))
            else:
                result = apply_canny_edge(frame, int(np.clip(parameters.canny_threshold, 0, 255)))
            if self._is_valid_image(result):
                if result.ndim == 3:
                    return cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                return result
            raise ValueError("the edge function returned an invalid image")
        except Exception as exc:
            self._emit_status(f"Edge processing error: {exc}. Showing a grayscale fallback.")
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def _is_valid_image(image: object) -> bool:
        return (
            isinstance(image, np.ndarray)
            and image.size > 0
            and len(image.shape) in (2, 3)
            and image.dtype == np.uint8
        )

    @staticmethod
    def _safe_odd_kernel(value: int) -> int:
        value = max(1, int(value))
        return value if value % 2 else value - 1

    @staticmethod
    def convert_cv_qt(cv_img: np.ndarray) -> QImage:
        if cv_img is None or cv_img.size == 0:
            raise ValueError("Cannot convert an empty image.")
        if len(cv_img.shape) == 3:
            rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape
            bytes_per_line = ch * w
            return QImage(
                rgb_img.data,
                w,
                h,
                bytes_per_line,
                QImage.Format.Format_RGB888,
            ).copy()

        gray = np.ascontiguousarray(cv_img)
        h, w = gray.shape
        return QImage(
            gray.data,
            w,
            h,
            w,
            QImage.Format.Format_Grayscale8,
        ).copy()

    def stop(self) -> None:
        self._running.clear()
        self.wait()
