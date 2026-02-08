def load_yolo():
    """
    Load YOLOv8 model for object detection.
    """
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")  # fast + realtime
        print("YOLOv8 model loaded successfully")
        return model
    except ImportError:
        raise ImportError("ultralytics not installed. Install with: pip install ultralytics")
    except Exception as e:
        raise Exception(f"Error loading YOLO: {e}")
