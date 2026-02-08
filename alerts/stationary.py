"""
Stationary/Loitering Detection Module

Detects when a tracked person remains in approximately the same location
for an extended period, indicating potential loitering behavior.
"""
import time

# Configuration: Time threshold for stationary detection (in seconds)
STATIONARY_TIME = 60  # Person must be stationary for 60 seconds to trigger alert

# Global memory to track positions and timestamps for each track_id
stationary_memory = {}


def check_stationary(track_id, bbox):
    """
    Check if a tracked person is stationary (loitering).
    
    Args:
        track_id: Unique track ID from DeepSORT
        bbox: Bounding box as [x1, y1, x2, y2]
    
    Returns:
        True if person has been stationary for STATIONARY_TIME seconds, False otherwise
    """
    # Calculate center point of bounding box
    cx = (bbox[0] + bbox[2]) // 2
    cy = (bbox[1] + bbox[3]) // 2
    now = time.time()

    # Initialize tracking for new track_id
    if track_id not in stationary_memory:
        stationary_memory[track_id] = {"pos": (cx, cy), "time": now}
        return False

    # Get previous position
    px, py = stationary_memory[track_id]["pos"]
    
    # Check if person moved (threshold: 10 pixels)
    if abs(cx - px) + abs(cy - py) < 10:
        # Person hasn't moved much - check if stationary time exceeded
        elapsed = now - stationary_memory[track_id]["time"]
        if elapsed > STATIONARY_TIME:
            return True
    
    # Update position and time
    stationary_memory[track_id] = {"pos": (cx, cy), "time": now}
    return False


def reset_stationary_memory():
    """Clear stationary tracking memory (useful for testing or reset)."""
    global stationary_memory
    stationary_memory = {}
