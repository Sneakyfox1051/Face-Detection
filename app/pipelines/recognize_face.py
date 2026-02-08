"""
Face Recognition Module

Recognizes faces by matching embeddings against database.
Note: This module uses direct SQLite queries and may need updates
to match current database schema.
"""
import sqlite3
from app.pipelines.faiss_index import search_embedding


def recognize_face(embedding):
    """
    Recognize a face by matching embedding against database.
    
    Args:
        embedding: Face embedding vector
    
    Returns:
        str: Person name if recognized, "Unknown" otherwise
    """
    result = search_embedding(embedding)
    if result[0] is None:
        return "Unknown"

    embedding_id, distance = result

    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT persons.name
        FROM face_logs
        JOIN persons ON face_logs.person_id = persons.id
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else "Unknown"
