"""
Face Matching Module

Matches face embeddings against a database of known persons using FAISS.
Returns person ID if match found, None if person is unknown.
"""
import numpy as np
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from app.pipelines.faiss_index import search_embedding

def match_face(embedding, db_people=None, threshold=0.8):
    """
    Match a face embedding against the database.
    
    Args:
        embedding: Face embedding vector (numpy array or list)
        db_people: Optional dictionary of known people (for compatibility)
        threshold: Distance threshold for matching
    
    Returns:
        (person_id, distance) tuple, or (None, None) if no match
    """
    try:
        # Convert embedding to numpy array
        if isinstance(embedding, list):
            embedding = np.array(embedding, dtype=np.float32)
        elif TORCH_AVAILABLE and isinstance(embedding, torch.Tensor):
            embedding = embedding.cpu().numpy().astype(np.float32)
        else:
            embedding = np.array(embedding, dtype=np.float32)
        
        # Flatten if needed
        embedding = embedding.flatten()
        
        # Search in FAISS index
        embedding_id, distance = search_embedding(embedding, threshold=threshold)
        
        if embedding_id is not None:
            return embedding_id, distance
        else:
            return None, None
            
    except Exception as e:
        print(f"Error in face matching: {e}")
        return None, None


def get_db_people():
    """
    Get database of known people.
    This is a placeholder - should be implemented based on your database schema.
    
    Returns:
        Dictionary of known people (for compatibility with existing code)
    """
    # TODO: Implement actual database query
    # For now, return empty dict
    return {}
