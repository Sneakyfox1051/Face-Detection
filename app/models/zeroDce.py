import torch
import cv2
import numpy as np
import os

# -----------------------------
# Global model (load ONCE)
# -----------------------------
_device = "cuda" if torch.cuda.is_available() else "cpu"
_zerodce_model = None
_zerodce_available = False
_zerodce_initialized = False


def _initialize_zerodce():
    """Lazy initialization of Zero-DCE model."""
    global _zerodce_model, _zerodce_available, _zerodce_initialized
    
    if _zerodce_initialized:
        return
    
    _zerodce_initialized = True
    
    # Try to load Zero-DCE model (optional)
    try:
        from ZeroDCE.model import enhance_net_nopool
        
        model_path = "Zero-DCE/pretrained/Zero_DCE.pth"
        if os.path.exists(model_path):
            _zerodce_model = enhance_net_nopool().to(_device)
            _zerodce_model.load_state_dict(
                torch.load(model_path, map_location=_device)
            )
            _zerodce_model.eval()
            _zerodce_available = True
            print("Zero-DCE model loaded successfully")
        else:
            print(f"Warning: Zero-DCE model file not found at {model_path}. Low-light enhancement will be disabled.")
    except ImportError:
        # Zero-DCE module not available - this is OK, it's optional
        pass
    except Exception as e:
        print(f"Warning: Error loading Zero-DCE model: {e}. Low-light enhancement will be disabled.")


@torch.no_grad()
def zerodce_enhance(frame):
    """
    Enhance low-light image using Zero-DCE.
    
    Args:
        frame: OpenCV BGR image
    
    Returns:
        enhanced BGR image (or original if Zero-DCE not available)
    """
    # Lazy initialization
    _initialize_zerodce()
    
    if not _zerodce_available or _zerodce_model is None:
        # Return original frame if Zero-DCE not available
        return frame

    try:
        # BGR → RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Normalize
        img = img.astype(np.float32) / 255.0

        # HWC → CHW → Tensor
        img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
        img = img.to(_device)

        # Zero-DCE forward
        enhanced, _ = _zerodce_model(img)

        # Tensor → image
        enhanced = enhanced.squeeze(0).permute(1, 2, 0)
        enhanced = enhanced.clamp(0, 1).cpu().numpy()
        enhanced = (enhanced * 255).astype(np.uint8)

        # RGB → BGR
        return cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Warning: Error in Zero-DCE enhancement: {e}. Returning original frame.")
        return frame
