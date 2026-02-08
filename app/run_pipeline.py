"""
Main runner for the surveillance pipeline.
Follows the exact flow:
Frame → Zero-DCE → YOLO → DeepSORT (OUTPUT 1) → Mask2Former → ResNet (OUTPUT 2) 
→ Face Pipeline (if person) → Alerts
"""
import cv2
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models_loader import load_all_models
from app.full_pipeline import process_frame

def main(video_source=0, camera_id="CAM_01"):
    """
    Main function to run the surveillance pipeline.
    
    Args:
        video_source: Video source (0 for webcam, or path to video file)
        camera_id: Camera identifier
    """
    print("Starting Surveillance Pipeline...")
    print("=" * 60)
    print("Pipeline Flow:")
    print("  Frame -> Zero-DCE -> YOLO -> DeepSORT (OUTPUT 1)")
    print("  -> Mask2Former -> ResNet (OUTPUT 2)")
    print("  -> Face Pipeline (if person) -> Alerts")
    print("=" * 60)
    
    # Load all models
    print("\nLoading models...")
    models = load_all_models()
    print("Models loaded\n")
    
    # Open video source with better error handling
    print(f"\nAttempting to open video source: {video_source}")
    
    # Try different backends for webcam (DirectShow first - most reliable on Windows)
    if isinstance(video_source, int):
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),  # Most reliable on Windows
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Any Available")
        ]
        
        cap = None
        working_backend_name = None
        import time
        
        for backend_id, backend_name in backends:
            try:
                test_cap = cv2.VideoCapture(video_source, backend_id)
                if test_cap.isOpened():
                    # Wait for camera to initialize
                    time.sleep(0.5)
                    
                    # Try reading multiple frames (first few might be empty)
                    success = False
                    for attempt in range(10):
                        ret, test_frame = test_cap.read()
                        if ret and test_frame is not None and test_frame.size > 0:
                            success = True
                            break
                        time.sleep(0.1)
                    
                    if success:
                        cap = test_cap
                        working_backend_name = backend_name
                        print(f"Successfully opened camera {video_source} with {backend_name} backend")
                        break
                    else:
                        test_cap.release()
                        print(f"Camera opened with {backend_name} but cannot read frames, trying next backend...")
            except Exception as e:
                if 'test_cap' in locals() and test_cap is not None:
                    try:
                        test_cap.release()
                    except:
                        pass
                continue
        
        if cap is None or not cap.isOpened():
            print(f"\nERROR: Cannot open camera {video_source}")
            print("\nTroubleshooting tips:")
            print("1. Make sure no other application is using the camera")
            print("2. Check camera permissions in Windows Settings")
            print("3. Try a different camera index: --source 1 or --source 2")
            print("4. Or use a video file: --source path/to/video.mp4")
            print("\nTrying alternative camera indices...")
            
            # Try other camera indices
            for alt_idx in [1, 2, 3]:
                try:
                    test_cap = cv2.VideoCapture(alt_idx, cv2.CAP_DSHOW)
                    if test_cap.isOpened():
                        ret, _ = test_cap.read()
                        if ret:
                            print(f"Found working camera at index {alt_idx}")
                            print(f"Try running with: --source {alt_idx}")
                        test_cap.release()
                except:
                    pass
            
            sys.exit(1)
    else:
        # Video file
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"ERROR: Cannot open video file: {video_source}")
            print("Please check the file path and make sure the file exists.")
            sys.exit(1)
        print(f"Video file opened: {video_source}")
    
    # Set camera properties for better performance
    if isinstance(video_source, int):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Wait a moment for camera to fully initialize
    import time
    time.sleep(0.5)
    
    print("Press 'q' to quit, 'ESC' to exit\n")
    
    frame_count = 0
    consecutive_failures = 0
    max_failures = 30
    
    print("Starting processing...\n")
    
    # Suppress OpenCV warnings for cleaner output
    import warnings
    import os
    os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret or frame is None or frame.size == 0:
                consecutive_failures += 1
                
                # Try to grab frame differently if normal read fails
                if consecutive_failures == 5:
                    print("Warning: Having trouble reading frames, trying alternative method...")
                    # Try grabbing without retrieving
                    if cap.grab():
                        ret, frame = cap.retrieve()
                        if ret and frame is not None and frame.size > 0:
                            consecutive_failures = 0
                            print("Successfully reading frames now!")
                
                if consecutive_failures >= max_failures:
                    print(f"\nERROR: Failed to read {max_failures} consecutive frames")
                    print("Camera may be disconnected or in use by another application.")
                    print("\nTroubleshooting:")
                    print("1. Close ALL applications using the camera:")
                    print("   - Zoom, Teams, Skype, Discord")
                    print("   - Windows Camera app")
                    print("   - Browser tabs with camera access")
                    print("2. Check Windows camera permissions")
                    print("3. Restart camera service (run as admin):")
                    print("   net stop wcamsvc")
                    print("   net start wcamsvc")
                    print("4. Try a different camera: --source 1")
                    print("5. Or use a video file: --source video.mp4")
                    break
                
                # Small delay before retry
                time.sleep(0.1)
                continue
            
            # Reset failure counter on success
            consecutive_failures = 0
            
            # Process frame through pipeline
            output_frame, scene_features, alerts = process_frame(
                frame,
                models,
                camera_id=camera_id,
                frame_count=frame_count,
                db_people=None
            )
            
            # 🔴 OUTPUT 1: Display real-time output after DeepSORT
            cv2.imshow("Surveillance - Real-time Output (After DeepSORT)", output_frame)
            
            # Save alerts to database and print to console
            if alerts:
                print(f"\nFrame {frame_count} - Alerts:")
                try:
                    from app.pipelines.db_writer import save_alert
                    
                    for alert_msg in alerts:
                        print(f"   {alert_msg}")
                        
                        # Determine alert type and save to database
                        alert_type = None
                        if "Unknown" in alert_msg or "Unknown person" in alert_msg:
                            alert_type = "UNKNOWN_PERSON"
                        elif "Restricted Zone" in alert_msg:
                            alert_type = "RESTRICTED_ZONE"
                        elif "Loitering" in alert_msg or "Stationary" in alert_msg:
                            alert_type = "STATIONARY"
                        
                        if alert_type:
                            # Extract track_id from alert message if possible
                            track_id = None
                            if "Track" in alert_msg:
                                try:
                                    track_id = int(alert_msg.split("Track")[-1].strip())
                                except:
                                    pass
                            
                            save_alert(camera_id, track_id, alert_type, alert_msg)
                except Exception as e:
                    print(f"Warning: Could not save alerts to database: {e}")
            
            # Print scene features info (every 15 frames)
            if scene_features and frame_count % 15 == 0:
                print(f"\nFrame {frame_count} - Scene Understanding:")
                if "scene_features" in scene_features:
                    feat_shape = scene_features["scene_features"].shape if hasattr(scene_features["scene_features"], 'shape') else "N/A"
                    print(f"   ResNet Features: {feat_shape}")
                if "mask2former_output" in scene_features:
                    print(f"   Mask2Former: Segmentation completed")
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\n🛑 Stopping pipeline...")
                break
            
            frame_count += 1
            
            # Print progress every 100 frames
            if frame_count % 100 == 0:
                print(f"Processed {frame_count} frames...")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Pipeline stopped. Cleanup complete.")


if __name__ == "__main__":
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
