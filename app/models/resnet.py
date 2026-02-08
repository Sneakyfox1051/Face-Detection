import torch
from torchvision import models

def load_resnet():
    """
    Load ResNet-50 model for scene feature extraction.
    Works with multiple torch/torchvision versions.
    """
    try:
        import torchvision
        from torchvision import models
        
        # Try different APIs based on torchvision version
        try:
            # New API (torchvision >= 0.13)
            if hasattr(models, 'ResNet50_Weights'):
                weights = models.ResNet50_Weights.DEFAULT
                model = models.resnet50(weights=weights)
            else:
                # Old API (torchvision < 0.13)
                model = models.resnet50(pretrained=True)
        except (AttributeError, TypeError) as e:
            # Fallback to old API
            try:
                model = models.resnet50(pretrained=True)
            except Exception:
                # Last resort: create model without pretrained weights
                model = models.resnet50()
                print("Warning: ResNet loaded without pretrained weights")
        
        model.eval()
        # Remove final classification layer to get features
        # Keep all layers except the last FC layer
        model = torch.nn.Sequential(*list(model.children())[:-1])
        print("ResNet-50 model loaded successfully")
        return model
    except Exception as e:
        print(f"Warning: Error loading ResNet model: {e}")
        raise
