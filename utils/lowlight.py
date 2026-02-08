"""
Low-light Detection Utility

Determines if a frame is in low-light conditions based on average brightness.
Used to conditionally enable Zero-DCE enhancement.
"""
import cv2
import numpy as np


def is_low_light(frame, brightness_thresh=60):
    """
    Returns True if frame is low-light.
    
    Args:
        frame: BGR frame (OpenCV format)
        brightness_thresh: Brightness threshold (default 60)
    
    Returns:
        True if frame is low-light, False otherwise
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)

    return mean_brightness < brightness_thresh