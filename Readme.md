# Lab01_ImageFiltering

Welcome to the first assignment of the Computer Vision and Machine Learning Lab course.

This project provides an interactive PyQt6 application for real-time and offline image filtering and edge detection using OpenCV. You will study Gaussian and averaging filters, Sobel and Canny edge detection, grayscale conversion, image thresholding, and the effect of processing parameters through a live visual interface.

## 🎯 Assignment Objectives

In this lab, you will implement three image-processing functions in `filters.py`:

```python
apply_gaussian_blur(...)
apply_averaging_blur(...)
apply_sobel_edge(...)
```

`apply_canny_edge(...)` is already implemented and should be used as a reference.

Students should modify **only `filters.py`**. Do not modify `main.py`, `gui.py`, `video_thread.py`, `config.py`, or other project files.



## 🧠 Processing Pipeline

```text
Input Source
    │
    ├── Webcam
    └── Offline Image / Video
    │
    ▼
+-------------------+
|       Frame       |
+-------------------+
      │       │
      │       └───────────────────────┐
      ▼                               ▼
 Blur Selection                 Edge Selection
 │                              │
 ├── Gaussian                   ├── Sobel
 └── Averaging                  └── Canny
 │                              │
 ▼                              ▼
Blurred View              Edge Detection View
```



## ✨ Features

- Real-time webcam processing with PyQt6 and OpenCV.
- Offline image and video input through **Browse** and **Upload**.
- Three synchronized views: **Original View**, **Blurred View**, and **Edge Detection View**.
- Gaussian Blur and Averaging Blur modes.
- Sobel and Canny edge-detection modes.
- Interactive kernel, sigma, and threshold controls.
- Visible numeric values for every slider.
- Odd-kernel handling for Gaussian filtering.
- Modern dark-themed interface with responsive scaling.
- Explicit camera/file error messages instead of silent failure.
- Live FPS display.
- Settings automatically restored between sessions and saved as parameters change.
- **Reset** button for returning to the default lab configuration.
- **Restart** button for reopening the current camera or replaying an offline video.
- Pause/Resume control for both webcam and file sources.
- Keyboard shortcuts for common actions.
- Safe processing fallbacks so an incomplete student implementation does not crash the application.

## 🛠️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/sharif-cvml-lab/cvml-lab01-image-filtering.git
cd cvml-lab01-image-filtering
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

## 🎮 Using the Application

### Webcam

The application starts with the selected webcam. Use **Camera index** when your computer has more than one camera. If a camera cannot be opened, the application remains usable and shows an explicit status message instead of crashing.

Use:

- **Webcam** to switch back to camera input.
- **Pause / Resume** to freeze or continue processing.
- **Restart** to reopen the current source.

### Offline Images and Videos

1. Click **Browse**.
2. Select an image or video file.
3. Click **Upload** to load it into the processing pipeline.

Images remain available for interactive parameter changes. Videos are played in real time and can be restarted from the beginning.

### Blur controls

Switch between:

- **Gaussian Blur** — controlled by kernel size and sigma.
- **Averaging Blur** — controlled by kernel size.

Gaussian kernel sizes should be positive odd numbers. The interface protects the application from invalid even sizes while the student implementation is incomplete.

### Edge controls

Switch between:

- **Sobel** — use the threshold slider in your implementation.
- **Canny** — use the primary threshold slider. The reference implementation uses the chosen threshold as the lower bound and three times that value as the upper bound.

### Parameter interaction

Changing a parameter immediately affects the processed views. Numeric values are shown next to all sliders so the selected configuration is always visible.

### Settings and reset

The application saves the current camera and filtering parameters automatically. The status area reports the settings state. Click **Reset** to return all parameters to their default values.

## 📂 Repository Structure

```text
cvml-lab01-image-filtering/
├── .gitignore
├── Readme.md
├── requirements.txt
├── main.py
├── gui.py
├── video_thread.py
├── config.py
└── filters.py              # The only file students should modify
```

### Module Responsibilities

- `main.py` — application entry point.
- `gui.py` — PyQt6 interface, controls, persistence, source selection, and rendering.
- `video_thread.py` — camera/file capture, real-time processing loop, FPS calculation, and safe error handling.
- `config.py` — shared constants and default parameters.
- `filters.py` — student implementation of the image-filtering algorithms.

## ⌨️ Keyboard Shortcuts

- `Space` — Pause / Resume.
- `R` — Reset parameters.
- `Q` — Quit.

