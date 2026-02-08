"""
Restricted Zone Detection Module

Defines restricted zones and checks if detected objects intersect with them.
Uses Shapely for geometric intersection calculations.
"""
from shapely.geometry import Polygon, box as shapely_box

# Configuration: Define restricted zones for each camera
# Format: Dictionary mapping camera_id to list of zone definitions
# Each zone has:
#   - "name": Human-readable zone name
#   - "coords": List of (x, y) tuples defining polygon vertices
RESTRICTED_ZONES = {
    "CAM_01": [
        {
            "name": "No Entry",
            "coords": [(0, 0), (400, 0), (400, 300), (0, 300)]  # Example zone
        }
    ]
    # Add more cameras and zones as needed:
    # "CAM_02": [
    #     {"name": "Restricted Area", "coords": [(x1, y1), (x2, y2), ...]}
    # ]
}

def check_restricted_zone(bbox, zones_list):
    """
    Check if a bounding box intersects with any restricted zone.
    
    Args:
        bbox: Bounding box as [x1, y1, x2, y2] or (x1, y1, x2, y2)
        zones_list: List of zone dictionaries with 'name' and 'coords' keys
    
    Returns:
        Zone name if intersection found, None otherwise
    """
    if not zones_list:
        return None
    
    x1, y1, x2, y2 = bbox
    person_box = shapely_box(x1, y1, x2, y2)
    
    for zone in zones_list:
        zone_polygon = Polygon(zone["coords"])
        if person_box.intersects(zone_polygon):
            return zone["name"]
    
    return None
