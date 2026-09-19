# Lab01_ImageFiltering

Welcome to the first assignment of the Computer Vision and Machine Learning lab course! 

This project provides a real-time, hardware-accelerated GUI built with PyQt6 that processes your webcam feed. Your objective for this lab is to implement fundamental image filtering and edge detection algorithms using OpenCV.

## 🎯 Assignment Objectives

In this lab, you will complete the implementation of three specific image processing functions located in `filters.py`. 

Currently, these functions return the raw, unmodified webcam frame so that the application runs without crashing. Once you successfully implement the logic, the GUI will update in real-time to reflect your changes.

*Note: The `apply_canny_edge` function is already implemented for you as a reference.*

## 🛠️ Setup & Installation

1. **Clone the repository** and navigate to the project directory.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python main.py
   ```

## 🎮 Using the Application

* The application displays three video streams side-by-side: **Original View**, **Blurred View**, and **Edge Detection View**.
* Use the control panel at the bottom to adjust kernel sizes, sigma values, and thresholds in real-time.
* Click the toggle buttons to switch between different filtering modes (e.g., Gaussian vs. Averaging, Sobel vs. Canny).