"""
Database Writer Module

Handles all database write operations for the surveillance system.
Provides functions to save alerts, detections, and retrieve stored data.
"""
from utils.db import SessionLocal, Alert, Person
from datetime import datetime

def save_alert(camera_id, track_id, alert_type, description):
    """
    Save an alert to the database.
    
    Args:
        camera_id: Camera identifier
        track_id: Track ID of the person (can be None)
        alert_type: Type of alert (STATIONARY, RESTRICTED_ZONE, UNKNOWN_PERSON)
        description: Alert description message
    """
    try:
        db = SessionLocal()
        alert = Alert(
            camera_id=str(camera_id),
            track_id=track_id,
            alert_type=alert_type,
            description=description,
            created_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)
        db.close()
        print(f"Alert saved to database: {alert_type} - {description}")
        return alert.id
    except Exception as e:
        print(f"Error saving alert to database: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return None

def save_detection(camera_id, person_id, det):
    """
    Save a detection to the database.
    
    Args:
        camera_id: Camera identifier
        person_id: Person ID if recognized (can be None)
        det: Detection dictionary with track_id, bbox, class, confidence, etc.
    """
    try:
        # For now, we'll just log detections
        # You can extend this to save to a Detection table if needed
        print(f"Detection: Track {det.get('track_id')}, Class: {det.get('class')}, Person ID: {person_id}")
        return True
    except Exception as e:
        print(f"Error saving detection: {e}")
        return False

def get_alerts(camera_id=None, limit=100):
    """
    Retrieve alerts from database.
    
    Args:
        camera_id: Filter by camera ID (optional)
        limit: Maximum number of alerts to retrieve
    
    Returns:
        List of alert objects
    """
    try:
        db = SessionLocal()
        query = db.query(Alert)
        
        if camera_id:
            query = query.filter(Alert.camera_id == str(camera_id))
        
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        db.close()
        return alerts
    except Exception as e:
        print(f"Error retrieving alerts: {e}")
        return []
