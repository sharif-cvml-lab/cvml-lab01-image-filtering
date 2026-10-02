from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings, QSize, Qt
from PyQt6.QtGui import QImage, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from config import (
    APP_NAME,
    DEFAULT_AVERAGING_KERNEL,
    DEFAULT_BLUR_MODE,
    DEFAULT_CAMERA_INDEX,
    DEFAULT_CANNY_THRESHOLD,
    DEFAULT_EDGE_MODE,
    DEFAULT_GAUSSIAN_KERNEL,
    DEFAULT_GAUSSIAN_SIGMA_TENTHS,
    DEFAULT_SETTINGS_MESSAGE,
    DEFAULT_SOBEL_THRESHOLD,
    FILE_FILTER,
    FilterParameters,
    ORGANIZATION_NAME,
)
from video_thread import VideoThread


DARK_STYLE = """
QMainWindow, QWidget {
    background: #11151b;
    color: #e7ebf0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}
QFrame#Header, QFrame#SidebarCard, QFrame#VideoCard, QFrame#StatusBar {
    background: #171c23;
    border: 1px solid #28303a;
    border-radius: 12px;
}
QFrame#VideoCanvas {
    background: #0a0d11;
    border: 1px solid #303945;
    border-radius: 10px;
}
QLabel#Title { font-size: 22px; font-weight: 700; }
QLabel#Subtitle, QLabel#Muted { color: #8e98a6; }
QLabel#PanelTitle { font-size: 14px; font-weight: 700; }
QLabel#Metric { color: #9aa6b4; font-size: 12px; }
QLabel#MetricValue { font-size: 15px; font-weight: 700; }
QLabel#ValueChip {
    background: #202833;
    border: 1px solid #364250;
    border-radius: 6px;
    padding: 2px 8px;
    min-width: 42px;
}
QPushButton {
    background: #212833;
    color: #eef2f6;
    border: 1px solid #35404d;
    border-radius: 8px;
    padding: 8px 12px;
}
QPushButton:hover { background: #2a3441; border-color: #4e6175; }
QPushButton:pressed { background: #18202a; }
QPushButton#accent { background: #3a7d67; border-color: #4c9b80; font-weight: 700; }
QPushButton#accent:hover { background: #479276; }
QPushButton#danger { background: #322126; border-color: #5d333d; }
QSpinBox {
    background: #1a2028;
    border: 1px solid #35404d;
    border-radius: 7px;
    padding: 6px;
}
QSlider::groove:horizontal { height: 5px; background: #2b333d; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #4d9d80; border-radius: 3px; }
QSlider::handle:horizontal {
    background: #80c6ab;
    border: 1px solid #9ad9c0;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QGroupBox {
    border: 1px solid #28303a;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 700;
}
QGroupBox::title { left: 12px; padding: 0 6px; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { width: 10px; background: transparent; }
QScrollBar::handle:vertical { background: #313b47; border-radius: 5px; min-height: 30px; }
"""


class VideoLabel(QLabel):
    """Scalable image view that preserves the source aspect ratio."""

    def __init__(self):
        super().__init__()
        self._pixmap = QPixmap()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(260, 190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_frame(self, image: QImage) -> None:
        self._pixmap = QPixmap.fromImage(image)
        self._refresh_pixmap()

    def clear_frame(self) -> None:
        self._pixmap = QPixmap()
        self.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _refresh_pixmap(self) -> None:
        if self._pixmap.isNull():
            return
        self.setPixmap(
            self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )


class ValueSlider(QWidget):
    def __init__(self, title: str, minimum: int, maximum: int, value: int, parent=None):
        super().__init__(parent)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.title_label = QLabel(title)
        self.title_label.setMinimumWidth(120)
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("ValueChip")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)
        layout.addWidget(self.title_label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_label)
        self.slider.valueChanged.connect(self._on_value_changed)

    def _on_value_changed(self, value: int) -> None:
        self.value_label.setText(str(value))

    def value(self) -> int:
        return self.slider.value()

    def set_value(self, value: int) -> None:
        self.slider.setValue(value)


class AppWindow(QMainWindow):
    """Main interactive UI for Lab 01."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(QSize(1120, 740))
        self.resize(1500, 900)

        self.settings = QSettings(ORGANIZATION_NAME, APP_NAME)
        self.video_thread: VideoThread | None = None
        self.selected_file = ""
        self.source_type = "camera"
        self._closing = False

        self._build_ui()
        self._restore_settings()
        self._build_shortcuts()
        self._start_video_thread()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 12)
        root.setSpacing(12)

        header = QFrame()
        header.setObjectName("Header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        title_box = QVBoxLayout()
        title = QLabel("Image Filtering Studio")
        title.setObjectName("Title")
        subtitle = QLabel("Interactive Gaussian / Averaging filtering and Sobel / Canny edge detection")
        subtitle.setObjectName("Subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box, 1)
        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("danger")
        self.reset_button.clicked.connect(self._reset_defaults)
        header_layout.addWidget(self.reset_button)
        root.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        video_side = QWidget()
        video_layout = QVBoxLayout(video_side)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_grid = QGridLayout()
        video_grid.setSpacing(10)
        self.original_panel = self._create_video_card("Original View")
        self.blurred_panel = self._create_video_card("Blurred View")
        self.edge_panel = self._create_video_card("Edge Detection View")
        video_grid.addWidget(self.original_panel, 0, 0)
        video_grid.addWidget(self.blurred_panel, 0, 1)
        video_grid.addWidget(self.edge_panel, 0, 2)
        for column in range(3):
            video_grid.setColumnStretch(column, 1)
        video_layout.addLayout(video_grid, 1)

        status = QFrame()
        status.setObjectName("StatusBar")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(14, 8, 14, 8)
        self.status_label = QLabel("Starting source...")
        self.status_label.setObjectName("Muted")
        self.settings_label = QLabel(DEFAULT_SETTINGS_MESSAGE)
        self.settings_label.setObjectName("MetricValue")
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setObjectName("MetricValue")
        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(self.settings_label)
        status_layout.addSpacing(18)
        status_layout.addWidget(self.fps_label)
        video_layout.addWidget(status)

        splitter.addWidget(video_side)
        splitter.addWidget(self._build_sidebar())
        splitter.setSizes([1140, 380])
        root.addWidget(splitter, 1)

        self.setCentralWidget(central)
        self.setStyleSheet(DARK_STYLE)

    def _create_video_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("VideoCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setObjectName("PanelTitle")
        layout.addWidget(title_label)
        canvas = QFrame()
        canvas.setObjectName("VideoCanvas")
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        image = VideoLabel()
        image.setText("Waiting for source...")
        canvas_layout.addWidget(image)
        layout.addWidget(canvas, 1)
        card.image = image
        return card

    def _build_sidebar(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(10)

        source_box = QGroupBox("Input Source")
        source_layout = QVBoxLayout(source_box)
        camera_row = QHBoxLayout()
        camera_row.addWidget(QLabel("Camera index"))
        self.camera_spin = QSpinBox()
        self.camera_spin.setRange(0, 9)
        self.camera_spin.valueChanged.connect(self._camera_index_changed)
        camera_row.addWidget(self.camera_spin)
        source_layout.addLayout(camera_row)

        camera_buttons = QHBoxLayout()
        self.webcam_button = QPushButton("Webcam")
        self.webcam_button.clicked.connect(self._use_webcam)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._browse_file)
        self.upload_button = QPushButton("Upload")
        self.upload_button.setObjectName("accent")
        self.upload_button.setEnabled(False)
        self.upload_button.clicked.connect(self._upload_selected_file)
        camera_buttons.addWidget(self.webcam_button)
        camera_buttons.addWidget(self.browse_button)
        camera_buttons.addWidget(self.upload_button)
        source_layout.addLayout(camera_buttons)

        self.file_label = QLabel("No offline image/video selected")
        self.file_label.setObjectName("Muted")
        self.file_label.setWordWrap(True)
        source_layout.addWidget(self.file_label)

        action_row = QHBoxLayout()
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self._toggle_pause)
        self.restart_button = QPushButton("Restart")
        self.restart_button.clicked.connect(self._restart_source)
        action_row.addWidget(self.pause_button)
        action_row.addWidget(self.restart_button)
        source_layout.addLayout(action_row)
        layout.addWidget(source_box)

        blur_box = QGroupBox("Blur Configuration")
        blur_layout = QVBoxLayout(blur_box)
        self.blur_mode_button = QPushButton()
        self.blur_mode_button.clicked.connect(self._toggle_blur_mode)
        blur_layout.addWidget(self.blur_mode_button)
        self.gaussian_kernel = ValueSlider("Gaussian kernel", 1, 31, DEFAULT_GAUSSIAN_KERNEL)
        self.gaussian_sigma = ValueSlider("Gaussian sigma ×10", 0, 50, DEFAULT_GAUSSIAN_SIGMA_TENTHS)
        self.averaging_kernel = ValueSlider("Averaging kernel", 1, 31, DEFAULT_AVERAGING_KERNEL)
        blur_layout.addWidget(self.gaussian_kernel)
        blur_layout.addWidget(self.gaussian_sigma)
        blur_layout.addWidget(self.averaging_kernel)
        layout.addWidget(blur_box)

        edge_box = QGroupBox("Edge Detection Configuration")
        edge_layout = QVBoxLayout(edge_box)
        self.edge_mode_button = QPushButton()
        self.edge_mode_button.clicked.connect(self._toggle_edge_mode)
        edge_layout.addWidget(self.edge_mode_button)
        self.sobel_threshold = ValueSlider("Sobel threshold", 0, 255, DEFAULT_SOBEL_THRESHOLD)
        self.canny_threshold = ValueSlider("Canny threshold", 0, 255, DEFAULT_CANNY_THRESHOLD)
        edge_layout.addWidget(self.sobel_threshold)
        edge_layout.addWidget(self.canny_threshold)
        layout.addWidget(edge_box)

        note = QLabel(
            " "
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch(1)

        for control in (
            self.gaussian_kernel,
            self.gaussian_sigma,
            self.averaging_kernel,
            self.sobel_threshold,
            self.canny_threshold,
        ):
            control.slider.valueChanged.connect(self._parameters_changed)

        self._update_mode_buttons()
        scroll.setWidget(content)
        return scroll

    def _build_shortcuts(self) -> None:
        QShortcut(QKeySequence("Space"), self, activated=self._toggle_pause)
        QShortcut(QKeySequence("R"), self, activated=self._reset_defaults)
        QShortcut(QKeySequence("Q"), self, activated=self.close)

    def _current_parameters(self) -> FilterParameters:
        gaussian_kernel = self.gaussian_kernel.value()
        if gaussian_kernel % 2 == 0:
            gaussian_kernel = max(1, gaussian_kernel - 1)
        return FilterParameters(
            blur_mode=getattr(self, "blur_mode", DEFAULT_BLUR_MODE),
            gaussian_kernel=gaussian_kernel,
            gaussian_sigma=self.gaussian_sigma.value() / 10.0,
            averaging_kernel=max(1, self.averaging_kernel.value()),
            edge_mode=getattr(self, "edge_mode", DEFAULT_EDGE_MODE),
            sobel_threshold=self.sobel_threshold.value(),
            canny_threshold=self.canny_threshold.value(),
        )

    def _start_video_thread(self) -> None:
        self._stop_video_thread()
        self.video_thread = VideoThread(
            camera_index=self.camera_spin.value(),
            source_type=self.source_type,
            file_path=self.selected_file,
            parent=self,
        )
        self.video_thread.set_parameters(self._current_parameters())
        self.video_thread.frame_ready.connect(self._update_frames)
        self.video_thread.status_changed.connect(self.status_label.setText)
        self.video_thread.start()
        self.pause_button.setText("Pause")
        self.status_label.setText("Starting source...")

    def _stop_video_thread(self) -> None:
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.deleteLater()
            self.video_thread = None

    def _update_frames(self, qt_orig, qt_blur, qt_edge, fps: float) -> None:
        self.original_panel.image.set_frame(qt_orig)
        self.blurred_panel.image.set_frame(qt_blur)
        self.edge_panel.image.set_frame(qt_edge)
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def _parameters_changed(self) -> None:
        self._save_settings()
        if self.video_thread is not None:
            self.video_thread.set_parameters(self._current_parameters())

    def _toggle_blur_mode(self) -> None:
        self.blur_mode = "Averaging" if self.blur_mode == "Gaussian" else "Gaussian"
        self._update_mode_buttons()
        self._parameters_changed()

    def _toggle_edge_mode(self) -> None:
        self.edge_mode = "Canny" if self.edge_mode == "Sobel" else "Sobel"
        self._update_mode_buttons()
        self._parameters_changed()

    def _update_mode_buttons(self) -> None:
        self.blur_mode_button.setText(f"Current Mode: {getattr(self, 'blur_mode', DEFAULT_BLUR_MODE)}")
        self.edge_mode_button.setText(f"Current Mode: {getattr(self, 'edge_mode', DEFAULT_EDGE_MODE)}")

    def _use_webcam(self) -> None:
        self.source_type = "camera"
        self._save_settings()
        self._start_video_thread()

    def _camera_index_changed(self, _value: int) -> None:
        self._save_settings()
        if self.source_type == "camera":
            self._start_video_thread()

    def _browse_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image or Video", "", FILE_FILTER)
        if not file_path:
            return
        self.selected_file = file_path
        self.file_label.setText(f"Selected: {Path(file_path).name}")
        self.upload_button.setEnabled(True)
        self.status_label.setText("File selected. Click Upload to process it.")

    def _upload_selected_file(self) -> None:
        if not self.selected_file:
            self.status_label.setText("No file selected. Click Browse first.")
            return
        self.source_type = "file"
        self._save_settings()
        self._start_video_thread()

    def _toggle_pause(self) -> None:
        if self.video_thread is None:
            return
        paused = self.pause_button.text() == "Pause"
        self.video_thread.set_paused(paused)
        self.pause_button.setText("Resume" if paused else "Pause")

    def _restart_source(self) -> None:
        if self.video_thread is not None:
            self.video_thread.restart_source()
            self.pause_button.setText("Pause")
            self.status_label.setText("Restarting source...")
        else:
            self._start_video_thread()

    def _reset_defaults(self) -> None:
        self.camera_spin.setValue(DEFAULT_CAMERA_INDEX)
        self.blur_mode = DEFAULT_BLUR_MODE
        self.edge_mode = DEFAULT_EDGE_MODE
        self.gaussian_kernel.set_value(DEFAULT_GAUSSIAN_KERNEL)
        self.gaussian_sigma.set_value(DEFAULT_GAUSSIAN_SIGMA_TENTHS)
        self.averaging_kernel.set_value(DEFAULT_AVERAGING_KERNEL)
        self.sobel_threshold.set_value(DEFAULT_SOBEL_THRESHOLD)
        self.canny_threshold.set_value(DEFAULT_CANNY_THRESHOLD)
        self._update_mode_buttons()
        self._save_settings()
        if self.video_thread is not None:
            self.video_thread.set_parameters(self._current_parameters())
        self.status_label.setText("Parameters reset to defaults.")

    def _save_settings(self) -> None:
        self.settings.setValue("camera_index", self.camera_spin.value())
        self.settings.setValue("blur_mode", getattr(self, "blur_mode", DEFAULT_BLUR_MODE))
        self.settings.setValue("edge_mode", getattr(self, "edge_mode", DEFAULT_EDGE_MODE))
        self.settings.setValue("gaussian_kernel", self.gaussian_kernel.value())
        self.settings.setValue("gaussian_sigma_tenths", self.gaussian_sigma.value())
        self.settings.setValue("averaging_kernel", self.averaging_kernel.value())
        self.settings.setValue("sobel_threshold", self.sobel_threshold.value())
        self.settings.setValue("canny_threshold", self.canny_threshold.value())
        self.settings.sync()
        self.settings_label.setText("Settings: Saved")

    def _restore_settings(self) -> None:
        self.camera_spin.setValue(self.settings.value("camera_index", DEFAULT_CAMERA_INDEX, int))
        self.blur_mode = self.settings.value("blur_mode", DEFAULT_BLUR_MODE)
        self.edge_mode = self.settings.value("edge_mode", DEFAULT_EDGE_MODE)
        self.gaussian_kernel.set_value(self._restore_odd("gaussian_kernel", DEFAULT_GAUSSIAN_KERNEL))
        self.gaussian_sigma.set_value(int(self.settings.value("gaussian_sigma_tenths", DEFAULT_GAUSSIAN_SIGMA_TENTHS)))
        self.averaging_kernel.set_value(int(self.settings.value("averaging_kernel", DEFAULT_AVERAGING_KERNEL)))
        self.sobel_threshold.set_value(int(self.settings.value("sobel_threshold", DEFAULT_SOBEL_THRESHOLD)))
        self.canny_threshold.set_value(int(self.settings.value("canny_threshold", DEFAULT_CANNY_THRESHOLD)))
        self._update_mode_buttons()
        self.settings_label.setText("Settings: Restored")

    def _restore_odd(self, key: str, default: int) -> int:
        value = int(self.settings.value(key, default))
        value = max(1, min(31, value))
        return value if value % 2 else value - 1

    def closeEvent(self, event) -> None:
        if not self._closing:
            self._closing = True
            self._save_settings()
            self._stop_video_thread()
        event.accept()


def create_application() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APP_NAME)
    return app
