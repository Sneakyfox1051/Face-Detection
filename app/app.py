"""
FastAPI application for surveillance pipeline web interface.
Modified for Render deployment (no webcam access - uses uploaded video files).
"""
from fastapi import FastAPI, Request, UploadFile, File, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import cv2
import threading
import os
import tempfile

from app.full_pipeline import process_frame
from app.models_loader import load_all_models
from app.pipelines.db_writer import get_alerts
from utils.db import SessionLocal, Alert, Person

app = FastAPI(title="Surveillance System", description="AI-powered surveillance system with object detection, tracking, and face recognition")
templates = Jinja2Templates(directory="templates")

# Store uploaded video path (for Render deployment)
current_video_path = None
latest_analytics = {}
lock = threading.Lock()

# Load models once at startup
print("Loading models for FastAPI app...")
try:
    models = load_all_models()
    print("Models loaded!")
except Exception as e:
    print(f"Warning: Could not load models: {e}")
    models = None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file for processing."""
    global current_video_path
    
    # Save uploaded file temporarily
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    current_video_path = file_path
    return {"status": "uploaded", "filename": file.filename, "message": "Video uploaded successfully. Processing will start on video feed."}


def video_generator():
    """Video generator for streaming from uploaded file (Render-compatible)."""
    global current_video_path
    
    if current_video_path is None or not os.path.exists(current_video_path):
        # Return a placeholder frame
        import numpy as np
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(placeholder, "Please upload a video file", (50, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(placeholder, "Use the upload button above", (50, 250),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        _, buffer = cv2.imencode(".jpg", placeholder)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )
        return
    
    cap = cv2.VideoCapture(current_video_path)
    frame_count = 0
    
    if not cap.isOpened():
        import numpy as np
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "Error opening video file", (50, 200),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(error_frame, "Please upload a valid video", (50, 250),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)
        _, buffer = cv2.imencode(".jpg", error_frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                # Loop video or break
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
                continue

            if models is None:
                # If models not loaded, just return original frame with message
                output_frame = frame.copy()
                cv2.putText(output_frame, "Models loading...", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Process frame through pipeline
                output_frame, scene_features, alerts = process_frame(
                    frame,
                    models,
                    camera_id="CAM_01",
                    frame_count=frame_count,
                    db_people=None
                )

                # Update analytics
                with lock:
                    global latest_analytics
                    latest_analytics = {
                        "frame_count": frame_count,
                        "alerts": alerts,
                        "scene_features_available": scene_features is not None,
                        "alerts_count": len(alerts)
                    }

            # Encode frame as JPEG
            _, buffer = cv2.imencode(".jpg", output_frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                buffer.tobytes() +
                b"\r\n"
            )
            
            frame_count += 1
            
            # Limit frame rate for performance (30 FPS)
            import time
            time.sleep(0.033)

    finally:
        cap.release()


@app.get("/video_feed")
def video_feed():
    """Stream video feed with real-time processing."""
    return StreamingResponse(
        video_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/analytics")
def get_analytics():
    """Get latest analytics data."""
    with lock:
        return JSONResponse(latest_analytics)


@app.get("/database", response_class=HTMLResponse)
def database_viewer(request: Request):
    """Database viewer page."""
    return templates.TemplateResponse("database.html", {"request": request})


@app.get("/api/alerts")
def get_alerts_api(camera_id: str = Query(None), limit: int = Query(100)):
    """Get alerts from database as JSON."""
    alerts = get_alerts(camera_id=camera_id, limit=limit)
    return JSONResponse([
        {
            "id": alert.id,
            "camera_id": alert.camera_id,
            "track_id": alert.track_id,
            "alert_type": alert.alert_type,
            "description": alert.description,
            "created_at": alert.created_at.isoformat() if alert.created_at else None
        }
        for alert in alerts
    ])


@app.get("/api/persons")
def get_persons_api():
    """Get registered persons from database."""
    try:
        db = SessionLocal()
        persons = db.query(Person).order_by(Person.created_at.desc()).all()
        db.close()
        return JSONResponse([
            {
                "id": person.id,
                "name": person.name,
                "created_at": person.created_at.isoformat() if person.created_at else None
            }
            for person in persons
        ])
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/stats")
def get_stats():
    """Get database statistics."""
    try:
        db = SessionLocal()
        total_alerts = db.query(Alert).count()
        total_persons = db.query(Person).count()
        
        # Count by alert type
        stationary = db.query(Alert).filter(Alert.alert_type == "STATIONARY").count()
        restricted = db.query(Alert).filter(Alert.alert_type == "RESTRICTED_ZONE").count()
        unknown = db.query(Alert).filter(Alert.alert_type == "UNKNOWN_PERSON").count()
        
        db.close()
        
        return JSONResponse({
            "total_alerts": total_alerts,
            "total_persons": total_persons,
            "alerts_by_type": {
                "stationary": stationary,
                "restricted_zone": restricted,
                "unknown_person": unknown
            }
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/health")
def health_check():
    """Health check endpoint for Render."""
    return {
        "status": "healthy",
        "models_loaded": models is not None,
        "video_uploaded": current_video_path is not None and os.path.exists(current_video_path) if current_video_path else False
    }
