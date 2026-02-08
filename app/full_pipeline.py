"""
Main Pipeline following the exact flow:
Frame → Zero-DCE → YOLO → DeepSORT (OUTPUT 1) → Mask2Former → ResNet (OUTPUT 2) 
→ Face Pipeline (if person) → Alerts
"""
import cv2
import torch
import numpy as np
from utils.lowlight import is_low_light
from app.models.zeroDce import zerodce_enhance
from app.pipelines.detect_n_track import detect_and_track
from app.pipelines.scene_understanding import run_scene_models
from app.pipelines.face_pipeline import process_faces
from alerts.alerts import generate_alerts


def process_frame(frame, models, camera_id="CAM_01", frame_count=0, db_people=None):
    """
    Process a single frame through the complete pipeline.
    
    Args:
        frame: Input BGR frame (OpenCV format)
        models: Dictionary of loaded models
        camera_id: Camera identifier
        frame_count: Current frame number
        db_people: Database of known people for face matching
    
    Returns:
        output_frame: Frame with visualizations (OUTPUT 1 - shown after DeepSORT)
        scene_features: Scene understanding features (OUTPUT 2)
        alerts: List of generated alerts
    """
    device = models.get("device", "cpu")
    alerts = []
    scene_features = None
    
    # ==========================================
    # 1️⃣ Frame Input
    # ==========================================
    original_frame = frame.copy()
    
    # ==========================================
    # 2️⃣ Zero-DCE (low-light enhancement)
    # ==========================================
    if is_low_light(frame):
        frame = zerodce_enhance(frame)
    
    # ==========================================
    # 3️⃣ YOLO (detect objects)
    # ==========================================
    yolo = models["yolo"]
    deepsort = models["deepsort"]
    
    # ==========================================
    # 4️⃣ DeepSORT (track IDs) ← 🔴 OUTPUT SHOWN HERE (REAL-TIME)
    # ==========================================
    tracked_objects = detect_and_track(frame, yolo, deepsort)
    
    # Visualize tracked objects (OUTPUT 1 - Real-time display)
    output_frame = frame.copy()
    for obj in tracked_objects:
        x1, y1, x2, y2 = map(int, obj["bbox"])
        track_id = obj["track_id"]
        class_name = obj["class"]
        conf = obj.get("confidence", 0.0)
        
        # Draw bounding box
        color = (0, 255, 0) if class_name == "person" else (255, 0, 0)
        cv2.rectangle(output_frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label with track ID
        label = f'{class_name}:{track_id}'
        if conf > 0:
            label += f' ({conf:.2f})'
        cv2.putText(output_frame, label, (x1, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # ==========================================
    # 5️⃣ Mask2Former (scene / zone semantics)
    # 6️⃣ ResNet (scene / object context features)
    # ==========================================
    # Run heavy models every 15 frames for performance
    if frame_count % 15 == 0:
        mask2former_model, mask2former_processor = models["mask2former"]
        resnet = models["resnet"]
        
        scene_features = run_scene_models(
            frame, 
            mask2former_model, 
            mask2former_processor,
            resnet, 
            device
        )
        
        # Display scene info on frame
        scene_text = f'Scene Features: {len(scene_features.get("scene_features", []))} dims'
        cv2.putText(output_frame, scene_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # ==========================================
    # 7️⃣ Face Pipeline (ONLY if class == person)
    # ==========================================
    face_embeddings = {}
    person_objects = [obj for obj in tracked_objects if obj["class"] == "person"]
    
    if person_objects:
        mtcnn = models["mtcnn"]
        gan = models.get("gan", None)
        facenet = models["facenet"]
        
        face_embeddings = process_faces(
            frame,
            person_objects,
            mtcnn,
            gan,
            facenet,
            device
        )
        
        # Display face IDs on frame
        y_offset = 60
        for track_id, emb in face_embeddings.items():
            cv2.putText(output_frame, f'FaceID: {track_id}',
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, (0, 0, 255), 2)
            y_offset += 25
    
    # ==========================================
    # 8️⃣ Generate Alerts (3 types: stationary, restricted, unknown person)
    # ==========================================
    if db_people is None:
        # Try to get db_people if available
        try:
            from app.pipelines.face_matcher import get_db_people
            db_people = get_db_people()
        except:
            db_people = {}
    
    alerts = generate_alerts(
        person_objects,
        face_embeddings,
        db_people,
        camera_id
    )
    
    # Display alerts on frame
    if alerts:
        alert_y = max(100, output_frame.shape[0] - len(alerts) * 30 - 20)
        for i, alert in enumerate(alerts[:3]):  # Show max 3 alerts
            # Truncate long alerts for display
            alert_text = alert[:60] if len(alert) > 60 else alert
            cv2.putText(output_frame, alert_text, (10, alert_y + i * 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    return output_frame, scene_features, alerts


def full_pipeline(frame, camera_id="CAM_01", models=None, frame_count=0, db_people=None):
    """
    Wrapper function for compatibility with existing code.
    Returns detections and alerts format.
    
    Note: This function processes the frame twice (once for output, once for detections).
    For better performance, use process_frame() directly.
    """
    if models is None:
        from app.models_loader import load_all_models
        models = load_all_models()
    
    # Process frame to get face embeddings
    output_frame, scene_features, alerts = process_frame(
        frame, models, camera_id, frame_count, db_people
    )
    
    # Get tracked objects (we need to run detection again to get current state)
    # In a real implementation, you might want to cache this
    tracked_objects = detect_and_track(
        frame, 
        models["yolo"], 
        models["deepsort"]
    )
    
    # Get face embeddings by processing faces again
    # (In production, you'd want to cache this from process_frame)
    person_objects = [obj for obj in tracked_objects if obj["class"] == "person"]
    face_embeddings = {}
    if person_objects:
        device = models.get("device", "cpu")
        face_embeddings = process_faces(
            frame,
            person_objects,
            models["mtcnn"],
            models.get("gan", None),
            models["facenet"],
            device
        )
    
    # Convert tracked objects to detections format
    detections = []
    for obj in tracked_objects:
        det = {
            "track_id": obj["track_id"],
            "bbox": obj["bbox"],
            "class": obj["class"],
            "confidence": obj.get("confidence", 0.0)
        }
        
        # Add face embedding if available
        if obj["class"] == "person" and obj["track_id"] in face_embeddings:
            det["embedding"] = face_embeddings[obj["track_id"]]
        
        detections.append(det)
    
    return detections, alerts
