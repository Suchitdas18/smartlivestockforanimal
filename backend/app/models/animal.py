"""Animal database model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class Species(str, enum.Enum):
    CATTLE = "cattle"
    GOAT = "goat"
    SHEEP = "sheep"
    PIG = "pig"
    HORSE = "horse"
    POULTRY = "poultry"
    OTHER = "other"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class Animal(Base):
    """Animal model representing a livestock animal."""
    
    __tablename__ = "animals"
    
    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    species = Column(String(20), default=Species.CATTLE.value)
    breed = Column(String(100), nullable=True)
    age_months = Column(Integer, nullable=True)
    gender = Column(String(10), default=Gender.UNKNOWN.value)
    weight_kg = Column(Float, nullable=True)
    
    # Identification
    muzzle_print_hash = Column(String(256), nullable=True)  # For muzzle recognition
    qr_code = Column(String(100), nullable=True)
    ear_tag_number = Column(String(50), nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    
    # Health status (cached from latest health record)
    current_health_status = Column(String(20), default="unknown")
    last_health_check = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    health_records = relationship("HealthRecord", back_populates="animal", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="animal", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="animal", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Animal(id={self.id}, tag_id='{self.tag_id}', species='{self.species}')>"
