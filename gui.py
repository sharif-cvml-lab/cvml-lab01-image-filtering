from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QPushButton, QGroupBox, QStackedWidget, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from video_thread import VideoThread

class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProVision - Real-Time Image Processing Engine")
        self.resize(1200, 700)
        
        # Professional Dark Theme CSS
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #f0f0f0; font-family: 'Segoe UI', Arial; }
            QGroupBox { border: 1px solid #3a3a3a; border-radius: 8px; margin-top: 15px; font-weight: bold; font-size: 14px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; color: #4da6ff; }
            QSlider::groove:horizontal { border: 1px solid #444; height: 6px; background: #333; margin: 2px 0; border-radius: 3px; }
            QSlider::handle:horizontal { background: #4da6ff; border: 1px solid #4da6ff; width: 14px; margin: -5px 0; border-radius: 7px; }
            QPushButton { background-color: #2d2d2d; color: white; border: 1px solid #444; padding: 10px; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #4da6ff; color: #1e1e1e; border: 1px solid #4da6ff;}
            QLabel { font-size: 13px; }
        """)

        self.init_ui()
        
        # Initialize Video Thread
        self.thread = VideoThread()
        self.thread.update_frames.connect(self.update_image)
        self.thread.start()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- Top: Video Feeds ---
        video_layout = QHBoxLayout()
        
        self.lbl_original = self.create_video_label("Original View")
        self.lbl_blurred = self.create_video_label("Blurred View")
        self.lbl_edge = self.create_video_label("Edge Detection View")
        
        video_layout.addWidget(self.lbl_original)
        video_layout.addWidget(self.lbl_blurred)
        video_layout.addWidget(self.lbl_edge)
        
        main_layout.addLayout(video_layout, stretch=3)
        
        # --- Bottom: Controls ---
        control_layout = QHBoxLayout()
        
        # 1. Blur Controls Box
        blur_box = QGroupBox("Blur Configuration")
        blur_vbox = QVBoxLayout()
        
        self.btn_toggle_blur = QPushButton("Current Mode: Gaussian Blur (Click to Swap)")
        self.btn_toggle_blur.clicked.connect(self.toggle_blur_mode)
        blur_vbox.addWidget(self.btn_toggle_blur)
        
        self.blur_stack = QStackedWidget()
        
        # Gaussian Page
        gauss_widget = QWidget()
        gauss_form = QFormLayout(gauss_widget)
        self.sl_gauss_k = self.create_slider(1, 31, 5, self.update_params)
        self.sl_gauss_s = self.create_slider(0, 50, 10, self.update_params) # Divided by 10 in thread
        gauss_form.addRow("Kernel Size:", self.sl_gauss_k)
        gauss_form.addRow("Sigma Value:", self.sl_gauss_s)
        
        # Averaging Page
        avg_widget = QWidget()
        avg_form = QFormLayout(avg_widget)
        self.sl_avg_k = self.create_slider(1, 31, 5, self.update_params)
        avg_form.addRow("Kernel Size:", self.sl_avg_k)
        
        self.blur_stack.addWidget(gauss_widget)
        self.blur_stack.addWidget(avg_widget)
        blur_vbox.addWidget(self.blur_stack)
        
        blur_box.setLayout(blur_vbox)
        control_layout.addWidget(blur_box)

        # 2. Edge Controls Box
        edge_box = QGroupBox("Edge Detection Configuration")
        edge_vbox = QVBoxLayout()
        
        self.btn_toggle_edge = QPushButton("Current Mode: Sobel Filter (Click to Swap)")
        self.btn_toggle_edge.clicked.connect(self.toggle_edge_mode)
        edge_vbox.addWidget(self.btn_toggle_edge)
        
        self.edge_stack = QStackedWidget()
        
        # Sobel Page
        sobel_widget = QWidget()
        sobel_form = QFormLayout(sobel_widget)
        self.sl_sobel_t = self.create_slider(0, 255, 100, self.update_params)
        sobel_form.addRow("Threshold (thr_var):", self.sl_sobel_t)
        
        # Canny Page
        canny_widget = QWidget()
        canny_form = QFormLayout(canny_widget)
        self.sl_canny_t = self.create_slider(0, 255, 100, self.update_params)
        canny_form.addRow("Primary Threshold:", self.sl_canny_t)
        
        self.edge_stack.addWidget(sobel_widget)
        self.edge_stack.addWidget(canny_widget)
        edge_vbox.addWidget(self.edge_stack)
        
        edge_box.setLayout(edge_vbox)
        control_layout.addWidget(edge_box)
        
        main_layout.addLayout(control_layout, stretch=1)
        self.setLayout(main_layout)

    def create_video_label(self, title):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #aaaaaa; margin-bottom: 5px;")
        
        img_lbl = QLabel()
        img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_lbl.setStyleSheet("background-color: #111111; border: 1px solid #333; border-radius: 4px;")
        img_lbl.setMinimumSize(320, 240)
        
        layout.addWidget(title_lbl)
        layout.addWidget(img_lbl, stretch=1)
        
        # Attach reference dynamically so we can update the image later
        container.img_lbl = img_lbl
        return container

    def create_slider(self, min_val, max_val, default, connect_func):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default)
        slider.valueChanged.connect(connect_func)
        return slider

    def toggle_blur_mode(self):
        if self.thread.blur_mode == "Gaussian":
            self.thread.blur_mode = "Averaging"
            self.btn_toggle_blur.setText("Current Mode: Averaging (Click to Swap)")
            self.blur_stack.setCurrentIndex(1)
        else:
            self.thread.blur_mode = "Gaussian"
            self.btn_toggle_blur.setText("Current Mode: Gaussian Blur (Click to Swap)")
            self.blur_stack.setCurrentIndex(0)
        self.update_params()

    def toggle_edge_mode(self):
        if self.thread.edge_mode == "Sobel":
            self.thread.edge_mode = "Canny"
            self.btn_toggle_edge.setText("Current Mode: Canny Edge (Click to Swap)")
            self.edge_stack.setCurrentIndex(1)
        else:
            self.thread.edge_mode = "Sobel"
            self.btn_toggle_edge.setText("Current Mode: Sobel Filter (Click to Swap)")
            self.edge_stack.setCurrentIndex(0)
        self.update_params()

    def update_params(self):
        self.thread.gauss_kernel = self.sl_gauss_k.value()
        self.thread.gauss_sigma = self.sl_gauss_s.value() / 10.0  # Slider 0-50 translates to 0.0-5.0
        self.thread.avg_kernel = self.sl_avg_k.value()
        self.thread.sobel_thresh = self.sl_sobel_t.value()
        self.thread.canny_thresh = self.sl_canny_t.value()

    def update_image(self, qt_orig, qt_blur, qt_edge):
        # Scale keeping aspect ratio to dynamically fit the window 
        w = self.lbl_original.img_lbl.width()
        h = self.lbl_original.img_lbl.height()
        
        self.lbl_original.img_lbl.setPixmap(QPixmap.fromImage(qt_orig).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))
        self.lbl_blurred.img_lbl.setPixmap(QPixmap.fromImage(qt_blur).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))
        self.lbl_edge.img_lbl.setPixmap(QPixmap.fromImage(qt_edge).scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()