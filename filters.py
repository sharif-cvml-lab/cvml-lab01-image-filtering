import cv2
import numpy as np

def apply_gaussian_blur(frame, kernel_size, sigma):
    """
    TODO: Implement Gaussian Blur.
    1. Ensure the kernel_size is an odd number and at least 1.
    2. Use cv2.GaussianBlur() to apply the filter.
    3. Return the blurred image.
    """
    # Replace the line below with your implementation
    return frame


def apply_averaging_blur(frame, kernel_size):
    """
    TODO: Implement Averaging Blur.
    1. Ensure the kernel_size (k) is at least 1.
    2. Create a k x k averaging kernel using np.ones().
    3. Use cv2.filter2D() to apply the filter.
    4. Return the blurred image.
    """
    # Replace the line below with your implementation
    return frame


def apply_sobel_edge(frame, thr_var):
    """
    TODO: Implement Sobel Edge Detection.
    1. Convert the input frame to grayscale.
    2. Calculate the Sobel gradients in the X and Y directions (using cv2.CV_64F).
    3. Compute the total gradient magnitude.
    4. Normalize the magnitude to an 8-bit range (0-255).
    5. Apply a binary threshold using the provided 'thr_var'.
    6. Return the resulting binary edge image.
    """
    # Replace the line below with your implementation
    return frame


def apply_canny_edge(frame, threshold):
    """
    Canny Edge Detection (Already Implemented).
    Uses the provided parameter as the lower bound and scales it for the upper bound.
    """
    # Convert to grayscale 
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
    
    # Canny conventionally uses two thresholds. 
    lower_bound = threshold
    upper_bound = threshold * 3
    
    return cv2.Canny(img, lower_bound, upper_bound)