"""
Face Processing Pipeline

Implements the complete face processing chain:
MTCNN (face detection) → Crop face → GAN (face enhancement) → FaceNet (embeddings)

This pipeline processes only person-class objects and generates face embeddings
for identity matching.
"""
import torch
import cv2
import numpy as np


def process_faces(frame, tracked_objects, mtcnn, gan, facenet, device):
    """
    Process faces for person objects:
    MTCNN (face detect) → Crop face → GAN (face enhancement) → FaceNet (embeddings → identity)
    
    Args:
        frame: BGR frame
        tracked_objects: List of tracked objects (filtered for person class)
        mtcnn: MTCNN face detector
        gan: GAN face enhancer (optional)
        facenet: FaceNet model for embeddings
        device: Device to run on
    
    Returns:
        Dictionary mapping track_id to face embedding
    """
    embeddings = {}
    facenet.eval()
    
    if gan:
        gan.eval()

    for obj in tracked_objects:
        if obj["class"] != "person":
            continue

        track_id = obj["track_id"]
        x1, y1, x2, y2 = map(int, obj["bbox"])
        
        # Ensure valid coordinates
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)
        
        if x2 <= x1 or y2 <= y1:
            continue
        
        person_crop = frame[y1:y2, x1:x2]
        
        if person_crop.size == 0:
            continue

        # MTCNN face detection
        try:
            # MTCNN expects RGB PIL Image or numpy array
            person_rgb = cv2.cvtColor(person_crop, cv2.COLOR_BGR2RGB)
            faces, probs = mtcnn.detect(person_rgb)
            
            if faces is None or len(faces) == 0:
                continue
            
            # Get the face with highest probability
            best_face_idx = np.argmax(probs) if len(probs) > 0 else 0
            face_box = faces[best_face_idx]
            
            # Extract face region
            fx1, fy1, fx2, fy2 = map(int, face_box)
            fx1 = max(0, fx1)
            fy1 = max(0, fy1)
            fx2 = min(person_crop.shape[1], fx2)
            fy2 = min(person_crop.shape[0], fy2)
            
            if fx2 <= fx1 or fy2 <= fy1:
                continue
            
            face_crop = person_rgb[fy1:fy2, fx1:fx2]
            
            # MTCNN extract (returns tensor)
            face_tensor = mtcnn.extract(face_crop, save_path=None)
            
            if face_tensor is None:
                continue
            
            # Ensure tensor is on correct device
            if isinstance(face_tensor, torch.Tensor):
                face_tensor = face_tensor.unsqueeze(0).to(device)
            else:
                face_tensor = torch.from_numpy(face_tensor).unsqueeze(0).to(device)
            
            # GAN enhancement (optional)
            with torch.no_grad():
                if gan is not None:
                    try:
                        if hasattr(gan, 'enhance'):
                            enhanced = gan.enhance(face_tensor)
                        elif hasattr(gan, '__call__'):
                            enhanced = gan(face_tensor)
                        else:
                            enhanced = face_tensor
                    except Exception as e:
                        # If GAN fails, use original
                        enhanced = face_tensor
                else:
                    enhanced = face_tensor
                
                # FaceNet embeddings
                emb = facenet(enhanced)
                if isinstance(emb, torch.Tensor):
                    emb = emb.detach().cpu().numpy().flatten()
                else:
                    emb = np.array(emb).flatten()
                
                embeddings[track_id] = emb
                
        except Exception as e:
            print(f"Error processing face for track {track_id}: {e}")
            continue

    return embeddings
