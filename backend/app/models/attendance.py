"""Attendance database model."""
from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, date
from ..database import Base


class Attendance(Base):
    """Attendance record for daily animal tracking."""
    
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, index=True)
    
    # Attendance data
    date = Column(Date, default=date.today, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Detection confidence
    detection_confidence = Column(Float, default=0.0)
    identification_method = Column(String(50), default="automatic")  # automatic, manual, ocr, muzzle
    
    # Location (optional, for future GPS integration)
    location_zone = Column(String(100), nullable=True)
    
    # Image reference
    image_path = Column(String(500), nullable=True)
    
    # Relationships
    animal = relationship("Animal", back_populates="attendance_records")
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, animal_id={self.animal_id}, date={self.date})>"
