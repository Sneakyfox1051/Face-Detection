"""
Database Models and Configuration

Defines SQLAlchemy models for the surveillance database.
Automatically creates tables on import if they don't exist.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

# Database configuration - Use environment variable if available (for Render deployment)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///surveillance.db")
# Handle SQLite connection args only for SQLite databases
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class Person(Base):
    """
    Person model for storing registered individuals.
    
    Attributes:
        id: Primary key
        name: Person's name
        embedding: Face embedding (stored as pickled numpy array string)
        created_at: Timestamp when person was registered
    """
    __tablename__ = "persons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    embedding = Column(String)  # Pickled numpy array as string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Alert(Base):
    """
    Alert model for storing generated alerts.
    
    Attributes:
        id: Primary key
        camera_id: Camera identifier that generated the alert
        track_id: Track ID of the person/object that triggered the alert
        alert_type: Type of alert (STATIONARY, RESTRICTED_ZONE, UNKNOWN_PERSON)
        description: Human-readable alert description
        created_at: Timestamp when alert was generated
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, nullable=False)
    track_id = Column(Integer, nullable=True)
    alert_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


# Create all tables if they don't exist
Base.metadata.create_all(bind=engine)
