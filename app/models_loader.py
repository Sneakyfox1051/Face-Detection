"""
Model Loader Module

Centralized model loading utility for the surveillance pipeline.
Loads all required and optional models, handling errors gracefully.
"""
import torch
from app.models.zeroDce import zerodce_enhance
from app.models.yolo import load_yolo
from app.models.deepsort import load_deepsort
from app.models.mask2former import load_mask2former
from app.models.resnet import load_resnet
from app.models.mtcnn import load_mtcnn
from app.models.gan_sr import load_srgan
from app.models.facenet import load_facenet


def load_all_models():
    """
    Load all models required for the surveillance pipeline.
    
    Required models (will raise exception if not available):
    - YOLO: Object detection
    - DeepSORT: Multi-object tracking
    - Mask2Former: Semantic segmentation
    - ResNet: Scene feature extraction
    - MTCNN: Face detection
    - FaceNet: Face embedding generation
    
    Optional models (can be None if not available):
    - Zero-DCE: Low-light enhancement
    - GAN: Face super-resolution
    
    Returns:
        dict: Dictionary containing all loaded models with keys:
            - "yolo": YOLOv8 model
            - "deepsort": DeepSORT tracker
            - "mask2former": Tuple of (model, processor)
            - "resnet": ResNet model
            - "mtcnn": MTCNN face detector
            - "facenet": FaceNet model
            - "gan": GAN model (optional, may be None)
            - "zerodce": Zero-DCE model reference (optional)
            - "device": Device string ("cuda" or "cpu")
    
    Raises:
        Exception: If any required model fails to load
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading models on device: {device}")
    print("=" * 60)

    models = {}
    
    # Required models (will raise exception if not available)
    try:
        models["yolo"] = load_yolo()
    except Exception as e:
        print(f"ERROR: Failed to load YOLO: {e}")
        raise
    
    try:
        models["deepsort"] = load_deepsort()
    except Exception as e:
        print(f"ERROR: Failed to load DeepSORT: {e}")
        raise
    
    try:
        models["mask2former"] = load_mask2former()
    except Exception as e:
        print(f"ERROR: Failed to load Mask2Former: {e}")
        raise
    
    try:
        models["resnet"] = load_resnet()
    except Exception as e:
        print(f"ERROR: Failed to load ResNet: {e}")
        raise
    
    try:
        models["mtcnn"] = load_mtcnn(device)
    except Exception as e:
        print(f"ERROR: Failed to load MTCNN: {e}")
        raise
    
    try:
        models["facenet"] = load_facenet()
    except Exception as e:
        print(f"ERROR: Failed to load FaceNet: {e}")
        raise
    
    # Optional models (can be None)
    models["gan"] = load_srgan(device)  # May return None
    models["zerodce"] = None  # Zero-DCE is loaded globally in zeroDce.py
    
    models["device"] = device
    
    print("=" * 60)
    print("All required models loaded successfully")
    return models

