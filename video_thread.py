import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
from filters import apply_gaussian_blur, apply_averaging_blur, apply_sobel_edge, apply_canny_edge

class VideoThread(QThread):
    # Signal emitted with 3 QImages: (Original, Blurred, Edge)
    update_frames = pyqtSignal(QImage, QImage, QImage)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        
        # State variables updated via UI sliders and buttons
        self.blur_mode = "Gaussian"
        self.edge_mode = "Sobel"
        
        self.gauss_kernel = 5
        self.gauss_sigma = 1.0
        self.avg_kernel = 5
        
        self.sobel_thresh = 100
        self.canny_thresh = 100

    def run(self):
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                continue

            # 1. Get original frame
            original = frame.copy()

            # 2. Apply Blur
            if self.blur_mode == "Gaussian":
                blurred = apply_gaussian_blur(original, self.gauss_kernel, self.gauss_sigma)
            else:
                blurred = apply_averaging_blur(original, self.avg_kernel)

            # 3. Apply Edge Detection 
            # Note: Applied to the original frame to keep the processing pipelines parallel.
            # You can easily change this to process 'blurred' if you prefer smoother edges.
            if self.edge_mode == "Sobel":
                edge = apply_sobel_edge(original, self.sobel_thresh)
            else:
                edge = apply_canny_edge(original, self.canny_thresh)

            # Convert frames to Qt Format for UI rendering
            qt_original = self.convert_cv_qt(original)
            qt_blurred = self.convert_cv_qt(blurred)
            qt_edge = self.convert_cv_qt(edge)

            self.update_frames.emit(qt_original, qt_blurred, qt_edge)
            
        cap.release()

    def convert_cv_qt(self, cv_img):
        """Convert an opencv image (BGR or Gray) to QPixmap"""
        if len(cv_img.shape) == 3:
            rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_img.shape
            bytes_per_line = ch * w
            return QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        else:
            h, w = cv_img.shape
            bytes_per_line = w
            return QImage(cv_img.data, w, h, bytes_per_line, QImage.Format.Format_Grayscale8)

    def stop(self):
        self._run_flag = False
        self.wait()