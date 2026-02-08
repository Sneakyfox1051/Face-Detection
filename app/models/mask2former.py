def load_mask2former():
    """
    Load Mask2Former model for semantic segmentation.
    """
    try:
        from transformers import Mask2FormerForUniversalSegmentation, AutoImageProcessor
        print("Loading Mask2Former model (this may take a while on first run)...")
        processor = AutoImageProcessor.from_pretrained(
            "facebook/mask2former-swin-large-coco-panoptic"
        )
        model = Mask2FormerForUniversalSegmentation.from_pretrained(
            "facebook/mask2former-swin-large-coco-panoptic"
        )
        model.eval()
        print("Mask2Former model loaded successfully")
        return model, processor
    except ImportError:
        raise ImportError("transformers not installed. Install with: pip install transformers")
    except Exception as e:
        raise Exception(f"Error loading Mask2Former: {e}")
