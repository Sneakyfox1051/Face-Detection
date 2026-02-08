"""
Alert generation system for three types:
1. Stationary (loitering)
2. Restricted Zone violation
3. Unknown Person
"""
from alerts.stationary import check_stationary
from alerts.zone_check import check_restricted_zone, RESTRICTED_ZONES
from app.pipelines.face_matcher import match_face

# Email service - now configured with credentials
try:
    from app.pipelines.email_service import send_email
    EMAIL_ENABLED = True
except ImportError:
    EMAIL_ENABLED = False
    def send_email(subject, message):
        print(f"Email (disabled): {subject} - {message}")
except Exception as e:
    EMAIL_ENABLED = False
    def send_email(subject, message):
        print(f"Email (error): {subject} - {message} - Error: {e}")

def generate_alerts(tracked_people, face_embeddings, db_people, camera_id):
    """
    Generate alerts for three types:
    - Stationary: Person loitering in one place
    - Restricted Zone: Person entering restricted area
    - Unknown Person: Person not recognized in database
    
    Args:
        tracked_people: List of tracked person objects
        face_embeddings: Dictionary mapping track_id to face embedding
        db_people: Database of known people (optional)
        camera_id: Camera identifier
    
    Returns:
        List of alert messages
    """
    alerts = []
    
    # Get restricted zones for this camera
    zones_list = RESTRICTED_ZONES.get(camera_id, [])

    for person in tracked_people:
        tid = person["track_id"]
        bbox = person["bbox"]

        # Alert Type 1: Restricted Zone Violation
        # Check if person's bounding box intersects any restricted zone
        zone = check_restricted_zone(bbox, zones_list)
        if zone:
            msg = f"Restricted Zone Violation ({zone}) - Track {tid}"
            if EMAIL_ENABLED:
                send_email("Restricted Zone Alert", msg)
            alerts.append(msg)

        # Alert Type 2: Stationary/Loitering Detection
        # Check if person has been stationary for extended period
        if check_stationary(tid, bbox):
            msg = f"Person Loitering - Track {tid}"
            if EMAIL_ENABLED:
                send_email("Stationary Person Alert", msg)
            alerts.append(msg)

        # Alert Type 3: Unknown Person Detection
        # Match face embedding against database of known persons
        if tid in face_embeddings:
            pid, distance = match_face(face_embeddings[tid], db_people)
            if pid is None:  # No match found - unknown person
                msg = f"Unknown Person - Track {tid}"
                if EMAIL_ENABLED:
                    send_email("Unknown Person Alert", msg)
                alerts.append(msg)

    return alerts
