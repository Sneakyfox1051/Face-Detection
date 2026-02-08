"""
FAISS Index Module

Manages FAISS index for efficient face embedding similarity search.
Uses L2 distance for matching face embeddings.
"""
import faiss
import numpy as np
import os

# Configuration
DIM = 512  # Face embedding dimension (FaceNet default)
INDEX_FILE = "faces.index"  # FAISS index file path

# Initialize or load FAISS index
if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
else:
    # Create new index with L2 distance metric
    index = faiss.IndexFlatL2(DIM)
    faiss.write_index(index, INDEX_FILE)


def add_embedding(embedding):
    """
    Add a face embedding to the FAISS index.
    
    Args:
        embedding: Face embedding vector (numpy array or list)
    
    Returns:
        int: Embedding ID (index in FAISS)
    """
    embedding = np.array(embedding).astype("float32")
    embedding = embedding.reshape(1, -1)
    index.add(embedding)
    faiss.write_index(index, INDEX_FILE)
    return index.ntotal - 1  # Return embedding ID


def search_embedding(embedding, threshold=0.8):
    """
    Search for matching face embedding in FAISS index.
    
    Args:
        embedding: Face embedding vector to search for
        threshold: Maximum L2 distance for a match (default: 0.8)
    
    Returns:
        tuple: (embedding_id, distance) if match found, (None, None) otherwise
    """
    embedding = np.array(embedding).astype("float32").reshape(1, -1)
    distances, indices = index.search(embedding, 1)
    
    if distances[0][0] < threshold:
        return indices[0][0], distances[0][0]
    
    return None, None
