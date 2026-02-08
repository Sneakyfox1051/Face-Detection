import torch

def load_srgan(device="cpu"):
    """
    Load RealESRGAN model for face enhancement (optional).
    Returns None if not available.
    """
    try:
        from realesrgan import RealESRGAN
        import os
        
        model_path = "RealESRGAN_x4.pth"
        if os.path.exists(model_path):
            model = RealESRGAN(device, scale=4)
            model.load_weights(model_path)
            print("RealESRGAN model loaded successfully")
            return model
        else:
            print(f"Warning: RealESRGAN model file not found at {model_path}. Face enhancement will be disabled.")
            return None
    except ImportError:
        print("Warning: RealESRGAN module not available. Face enhancement will be disabled.")
        return None
    except Exception as e:
        print(f"Warning: Error loading RealESRGAN model: {e}. Face enhancement will be disabled.")
        return None
