from __future__ import annotations

from dataclasses import dataclass

APP_NAME = "CVML Lab 01 - Image Filtering"
ORGANIZATION_NAME = "Sharif CVML Lab"

CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480
TARGET_FPS = 30

DEFAULT_CAMERA_INDEX = 0
DEFAULT_THEME = "dark"

DEFAULT_BLUR_MODE = "Gaussian"
DEFAULT_GAUSSIAN_KERNEL = 5
DEFAULT_GAUSSIAN_SIGMA_TENTHS = 10  # 1.0
DEFAULT_AVERAGING_KERNEL = 5

DEFAULT_EDGE_MODE = "Sobel"
DEFAULT_SOBEL_THRESHOLD = 100
DEFAULT_CANNY_THRESHOLD = 100

DEFAULT_SETTINGS_MESSAGE = "Settings: Ready"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")
VIDEO_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v")

FILE_FILTER = (
    "Media Files (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff "
    "*.mp4 *.avi *.mov *.mkv *.webm *.m4v);;"
    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;"
    "Videos (*.mp4 *.avi *.mov *.mkv *.webm *.m4v);;"
    "All Files (*)"
)


@dataclass(frozen=True)
class FilterParameters:
    blur_mode: str
    gaussian_kernel: int
    gaussian_sigma: float
    averaging_kernel: int
    edge_mode: str
    sobel_threshold: int
    canny_threshold: int
