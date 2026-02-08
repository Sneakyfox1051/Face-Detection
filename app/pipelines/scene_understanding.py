"""
Scene Understanding Pipeline

Runs Mask2Former for semantic segmentation and ResNet for scene feature extraction.
This module provides scene understanding capabilities for zone detection and context analysis.
"""
import torch
import cv2
import numpy as np
from PIL import Image


def run_scene_models(frame, mask2former_model, mask2former_processor, resnet, device):
    """
    Run Mask2Former for scene/zone semantics and ResNet for context features.
    
    Args:
        frame: BGR frame (OpenCV format)
        mask2former_model: Mask2Former model (optional, can be None)
        mask2former_processor: Mask2Former processor (optional, can be None)
        resnet: ResNet model
        device: Device to run on
    
    Returns:
        Dictionary with scene_features and segmentation (if available)
    """
    with torch.no_grad():
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)
        
        # Process with Mask2Former (if available)
        mask2former_outputs = None
        if mask2former_model is not None and mask2former_processor is not None:
            try:
                inputs = mask2former_processor(images=pil_image, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}
                # Mask2Former forward pass
                mask2former_outputs = mask2former_model(**inputs)
            except Exception as e:
                print(f"Warning: Mask2Former processing failed: {e}")
                mask2former_outputs = None
        
        # ResNet for scene features
        # Preprocess for ResNet
        img_tensor = torch.from_numpy(rgb_frame).permute(2, 0, 1).unsqueeze(0).float()
        img_tensor = img_tensor / 255.0
        img_tensor = img_tensor.to(device)
        
        # ResNet forward pass
        scene_features = resnet(img_tensor)
        
        # Extract features (before final classification layer)
        if hasattr(scene_features, 'flatten'):
            scene_features = scene_features.flatten(start_dim=1)
        else:
            scene_features = scene_features.view(scene_features.size(0), -1)
        
        scene_features = scene_features.cpu().numpy()

    result = {
        "scene_features": scene_features
    }
    
    if mask2former_outputs is not None:
        result["segmentation"] = mask2former_outputs
        result["mask2former_output"] = mask2former_outputs
    
    return result
