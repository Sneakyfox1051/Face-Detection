def load_mtcnn(device="cpu"):
    """
    Load MTCNN face detector.
    """
    try:
        from facenet_pytorch import MTCNN
        mtcnn = MTCNN(
            image_size=160,
            margin=20,
            keep_all=False,
            device=device
        )
        print("MTCNN model loaded successfully")
        return mtcnn
    except ImportError:
        raise ImportError("facenet_pytorch not installed. Install with: pip install facenet-pytorch")
    except Exception as e:
        raise Exception(f"Error loading MTCNN: {e}")
