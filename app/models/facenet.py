def load_facenet():
    """
    Load FaceNet model for face embeddings.
    """
    try:
        from facenet_pytorch import InceptionResnetV1
        model = InceptionResnetV1(pretrained="vggface2").eval()
        print("FaceNet model loaded successfully")
        return model
    except ImportError:
        raise ImportError("facenet_pytorch not installed. Install with: pip install facenet-pytorch")
    except Exception as e:
        raise Exception(f"Error loading FaceNet: {e}")
