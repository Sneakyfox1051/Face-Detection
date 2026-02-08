"""
Video Processor Module

Provides video processing functions for streaming and file processing.
Compatible with FastAPI streaming or standalone use.
"""
import cv2
from app.full_pipeline import full_pipeline
from app.pipelines.face_matcher import match_face, get_db_people

# Optional database imports (can be disabled if not using database)
try:
    from utils.db import SessionLocal, Camera
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Warning: Database not available - alerts will not be saved to DB")

# Optional db_writer imports
try:
    from app.pipelines.db_writer import save_detection, save_alert
    DB_WRITER_AVAILABLE = True
except:
    DB_WRITER_AVAILABLE = False
    print("Warning: DB writer not available - detections will not be saved")


def mjpeg_generator(video_source=0, camera_id="CAM_01", models=None):
    """
    MJPEG generator for video streaming.
    
    Args:
        video_source: Video source (0 for webcam, or path to video file)
        camera_id: Camera identifier
        models: Pre-loaded models (optional, will load if None)
    
    Yields:
        JPEG-encoded frames for streaming
    """
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise RuntimeError(f"ERROR: Cannot open video source {video_source}")
    
    print("Processing started...")
    
    # Load models if not provided
    if models is None:
        from app.models_loader import load_all_models
        models = load_all_models()
    
    # Get camera DB ID if database is available
    camera_db_id = 1
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
            if camera:
                camera_db_id = camera.id
            db.close()
        except:
            pass
    
    frame_count = 0
    db_people = get_db_people()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame through pipeline
            detections, alerts = full_pipeline(
                frame, 
                camera_id=camera_id,
                models=models,
                frame_count=frame_count,
                db_people=db_people
            )

            # Save detections to database (if available)
            if DB_WRITER_AVAILABLE:
                for det in detections:
                    person_id = None
                    if "embedding" in det:
                        person_id, _ = match_face(det["embedding"], db_people)
                    
                    try:
                        save_detection(
                            camera_id=camera_db_id,
                            person_id=person_id,
                            det=det
                        )
                    except Exception as e:
                        print(f"Error saving detection: {e}")

            # Save alerts to database (if available)
            if DB_WRITER_AVAILABLE and alerts:
                for alert in alerts:
                    alert_type = None
                    if "Unknown" in alert or "Unknown person" in alert:
                        alert_type = "UNKNOWN_PERSON"
                    elif "Restricted Zone" in alert:
                        alert_type = "RESTRICTED_ZONE"
                    elif "Loitering" in alert or "loitering" in alert or "Stationary" in alert:
                        alert_type = "STATIONARY"
                    
                    if alert_type:
                        try:
                            save_alert(camera_db_id, None, alert_type, alert)
                        except Exception as e:
                            print(f"Error saving alert: {e}")

            # Encode frame as JPEG for streaming
            _, jpeg = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + jpeg.tobytes()
                + b"\r\n"
            )
            
            frame_count += 1

    finally:
        cap.release()
        print("Processing stopped")


def process_video_file(video_path, camera_id="CAM_01", display=True):
    """
    Process a video file through the pipeline.
    
    Args:
        video_path: Path to video file
        camera_id: Camera identifier
        display: Whether to display output frames
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"ERROR: Cannot open video file: {video_path}")
    
    print(f"Processing video: {video_path}")
    
    from app.models_loader import load_all_models
    from app.full_pipeline import process_frame
    
    models = load_all_models()
    frame_count = 0
    db_people = get_db_people()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Process frame
            output_frame, scene_features, alerts = process_frame(
                frame,
                models,
                camera_id=camera_id,
                frame_count=frame_count,
                db_people=db_people
            )

            # Display if requested
            if display:
                cv2.imshow("Surveillance - Real-time Output", output_frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            # Print alerts
            if alerts:
                print(f"Frame {frame_count}: {alerts}")

            frame_count += 1

    finally:
        cap.release()
        if display:
            cv2.destroyAllWindows()
        print("Video processing complete")
