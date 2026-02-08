"""
Face Registration Module

Registers a new person's face in the database and FAISS index.
Note: This module uses direct SQLite queries and may need updates
to match current database schema.
"""
import sqlite3
from datetime import datetime
from app.pipelines.faiss_index import add_embedding


def register_face(name, embedding, camera_id="cam_1"):
    """
    Register a new person's face in the system.
    
    Args:
        name: Person's name
        embedding: Face embedding vector
        camera_id: Camera identifier where face was captured
    
    Returns:
        None
    """
    conn = sqlite3.connect("surveillance.db")
    cursor = conn.cursor()

    # Insert person
    cursor.execute("INSERT INTO persons(name) VALUES (?)", (name,))
    person_id = cursor.lastrowid

    # Add embedding to FAISS
    embedding_id = add_embedding(embedding)

    # Log face
    cursor.execute("""
        INSERT INTO face_logs(person_id, timestamp, camera_id)
        VALUES (?, ?, ?)
    """, (person_id, datetime.now().isoformat(), camera_id))

    conn.commit()
    conn.close()

    print(f"Registered {name} with embedding ID {embedding_id}")
