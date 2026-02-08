"""
Detailed camera test to diagnose issues.
"""
import cv2
import time

def test_camera_detailed(index):
    """Test camera with detailed diagnostics."""
    print(f"\n{'='*60}")
    print(f"Testing Camera {index}")
    print(f"{'='*60}")
    
    # Try different backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Any Available")
    ]
    
    for backend_id, backend_name in backends:
        print(f"\nTrying {backend_name} backend...")
        try:
            cap = cv2.VideoCapture(index, backend_id)
            
            if not cap.isOpened():
                print(f"  [X] Cannot open with {backend_name}")
                continue
            
            print(f"  [OK] Opened with {backend_name}")
            
            # Get camera properties
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"  Properties: {int(width)}x{int(height)} @ {fps} FPS")
            
            # Wait for initialization
            time.sleep(0.5)
            
            # Try to read frames
            success_count = 0
            for i in range(10):
                ret, frame = cap.read()
                if ret and frame is not None and frame.size > 0:
                    success_count += 1
                    if i == 0:
                        print(f"  [OK] Successfully read frame! Shape: {frame.shape}")
                time.sleep(0.1)
            
            if success_count > 0:
                print(f"  [OK] Camera {index} is WORKING with {backend_name}!")
                print(f"  Successfully read {success_count}/10 frames")
                cap.release()
                return True, backend_id, backend_name
            else:
                print(f"  [X] Cannot read frames from camera {index}")
            
            cap.release()
            
        except Exception as e:
            print(f"  [X] Error with {backend_name}: {e}")
            continue
    
    return False, None, None

if __name__ == "__main__":
    print("Camera Diagnostic Test")
    print("="*60)
    
    # Test first 3 camera indices
    working_cameras = []
    for i in range(3):
        success, backend_id, backend_name = test_camera_detailed(i)
        if success:
            working_cameras.append((i, backend_id, backend_name))
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if working_cameras:
        print(f"\n[OK] Found {len(working_cameras)} working camera(s):")
        for idx, backend_id, backend_name in working_cameras:
            print(f"  Camera {idx} - Backend: {backend_name} (ID: {backend_id})")
        print(f"\nUse: python run_pipeline.py --source {working_cameras[0][0]}")
    else:
        print("\n[X] No working cameras found!")
        print("\nTroubleshooting:")
        print("1. Close all applications using the camera:")
        print("   - Zoom, Teams, Skype, Discord")
        print("   - Camera app, Windows Camera")
        print("   - Any browser tabs with camera access")
        print("\n2. Check Windows Camera Permissions:")
        print("   - Settings → Privacy → Camera")
        print("   - Enable 'Allow apps to access your camera'")
        print("   - Enable 'Allow desktop apps to access your camera'")
        print("\n3. Restart the camera service:")
        print("   - Open Command Prompt as Administrator")
        print("   - Run: net stop wcamsvc")
        print("   - Wait 5 seconds")
        print("   - Run: net start wcamsvc")
        print("\n4. Try using a video file instead:")
        print("   python run_pipeline.py --source video.mp4")
