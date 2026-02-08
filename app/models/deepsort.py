def load_deepsort():
    """
    Load DeepSORT tracker.
    """
    try:
        from deep_sort_realtime.deepsort_tracker import DeepSort
        tracker = DeepSort(
            max_age=30,                # frames to keep track alive
            n_init=3,                  # frames before confirming track
            max_iou_distance=0.7,
            max_cosine_distance=0.4,
            embedder="mobilenet",      # pretrained ReID model
            half=True,
            bgr=True
        )
        print("DeepSORT tracker loaded successfully")
        return tracker
    except ImportError as e:
        raise ImportError(f"deep_sort_realtime not installed or incorrect import. Error: {e}. Install with: pip install deep-sort-realtime")
    except Exception as e:
        raise Exception(f"Error loading DeepSORT: {e}")


    
