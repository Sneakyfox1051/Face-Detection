"""
Detection and Tracking Pipeline

Combines YOLOv8 object detection with DeepSORT multi-object tracking.
This is the core detection and tracking module that processes each frame.
"""
import cv2
import numpy as np


def detect_and_track(frame, yolo, tracker):
    """
    Detect objects with YOLO and track with DeepSORT.
    
    Args:
        frame: Input BGR frame
        yolo: YOLO model
        tracker: DeepSORT tracker
    
    Returns:
        List of tracked objects with track_id, bbox, class, and confidence
    """
    results = yolo(frame, conf=0.4)[0]

    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cls = yolo.names[int(box.cls[0])]
        conf = float(box.conf[0])
        # DeepSORT expects [x, y, w, h] format
        detections.append(([x1, y1, x2 - x1, y2 - y1], conf, cls))

    tracks = tracker.update_tracks(detections, frame=frame)

    tracked_objects = []
    for t in tracks:
        if not t.is_confirmed():
            continue
        
        # Get detection class from track
        det_class = t.get_det_class() if hasattr(t, 'get_det_class') else "unknown"
        
        # Get confidence if available
        confidence = t.confidence if hasattr(t, 'confidence') else 0.0
        
        tracked_objects.append({
            "track_id": t.track_id,
            "bbox": t.to_ltrb(),  # Returns [x1, y1, x2, y2]
            "class": det_class,
            "confidence": confidence
        })

    return tracked_objects
