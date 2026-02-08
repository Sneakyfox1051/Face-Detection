"""
Main runner for the surveillance pipeline (run from project root).
Follows the exact flow:
Frame → Zero-DCE → YOLO → DeepSORT (OUTPUT 1) → Mask2Former → ResNet (OUTPUT 2) 
→ Face Pipeline (if person) → Alerts

Usage:
    python run_pipeline.py --source 0 --camera-id CAM_01
"""
import sys
import os

# Ensure we're running from project root
if __name__ == "__main__":
    from app.run_pipeline import main
    import argparse
    
    parser = argparse.ArgumentParser(description="Surveillance Pipeline Runner")
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Video source (0 for webcam, or path to video file)"
    )
    parser.add_argument(
        "--camera-id",
        type=str,
        default="CAM_01",
        help="Camera identifier"
    )
    
    args = parser.parse_args()
    
    # Convert source to int if it's a number (webcam)
    try:
        video_source = int(args.source)
    except ValueError:
        video_source = args.source
    
    main(video_source=video_source, camera_id=args.camera_id)
