# Lab01_ImageFiltering

Welcome to the first assignment of the Computer Vision and Machine Learning lab course!

This project provides a real-time PyQt6 application for image filtering and edge detection using OpenCV. The goal of this lab is to understand the basic principles of Gaussian and averaging filters, Sobel and Canny edge detection, grayscale conversion, thresholding, and the effect of filter parameters through an interactive webcam application.

## 🎯 Assignment Objectives

In this lab, you will complete the implementation of three specific image-processing functions located in `filters.py`:

```python
apply_gaussian_blur(...)
apply_averaging_blur(...)
apply_sobel_edge(...)
```

The `apply_canny_edge(...)` function is already implemented and should be used as a reference.

Students should modify only `filters.py`. Do not modify `main.py`, `gui.py`, `video_thread.py`, or any other project file.

The expected processing pipeline is:

```text
Camera Frame
     ↓
 ┌───────────────┬────────────────────┐
 │               │                    │
 ↓               ↓                    │
Blur Selection   Edge Selection        │
 │               │                    │
 ├─ Gaussian     ├─ Sobel             │
 │               │                    │
 └─ Averaging    └─ Canny             │
 │               │                    │
 ↓               ↓                    │
Blurred View   Edge Detection View     │
 └───────────────┴────────────────────┘
```

## ✨ Features

- Real-time webcam image processing with PyQt6 and OpenCV.
- Three synchronized views: **Original View**, **Blurred View**, and **Edge Detection View**.
- Two blur modes: **Gaussian Blur** and **Averaging Blur**.
- Two edge-detection modes: **Sobel** and **Canny**.
- Live controls for blur kernel size, Gaussian sigma, and edge-detection thresholds.
- Gaussian kernel-size control with odd-sized kernels suitable for OpenCV filtering.
- Sobel and Canny edge outputs displayed in real time.
- Dark-themed graphical interface.
- Dynamic image scaling while preserving the original aspect ratio.
- High-DPI support for modern displays.
- Parallel processing paths for blur and edge detection.

## 🛠️ Setup & Installation

1. Clone the repository and navigate to the project directory.

2. Create a virtual environment (recommended):

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

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python main.py
```

## 🎮 Using the Application

### Blur controls

The application provides two blur modes:

- **Gaussian Blur** — applies Gaussian smoothing using a configurable kernel size and sigma value.
- **Averaging Blur** — applies an averaging filter using a configurable square kernel.

Use the blur mode button to switch between the two methods. Adjust the corresponding parameters with the sliders and observe their effect on the **Blurred View**.

For Gaussian filtering, the kernel size should be an odd positive integer. The sigma slider represents values from `0.0` to `5.0`.

### Edge detection controls

The application provides two edge-detection modes:

- **Sobel** — converts the input image to grayscale, computes the horizontal and vertical gradients, combines them into a gradient magnitude, normalizes the result, and applies a binary threshold.
- **Canny** — uses the provided implementation with the selected threshold as the lower threshold and three times that value as the upper threshold.

Use the edge mode button to switch between Sobel and Canny. Adjust the threshold and observe how it changes the detected edges.

The edge-detection pipeline operates on the **original webcam frame**, independently of the blur pipeline.


## 📂 Repository Structure

```text
cvml-lab01-image-filtering/
├── .gitignore
├── Readme.md
├── requirements.txt
├── main.py
├── gui.py
├── video_thread.py
└── filters.py              # The only file students should modify
```

### Module responsibilities

- `main.py` — application entry point and PyQt6 application initialization.
- `gui.py` — graphical user interface, controls, layout, and display rendering.
- `video_thread.py` — webcam capture, real-time processing, and communication with the GUI.
- `filters.py` — the student implementation of the image filtering and edge-detection algorithms.

## ⚙️ Important Notes

- A webcam accessible as camera index `0` is required by the current implementation.
- The application processes frames continuously in a background Qt thread.
- The **Edge Detection View** is produced from the original frame rather than the blurred frame.
- Do not replace the provided application structure; implement the required algorithms inside the designated functions.
