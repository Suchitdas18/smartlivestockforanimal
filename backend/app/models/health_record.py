"""Health Record database model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthRecord(Base):
    """Health record model for tracking animal health over time."""
    
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False, index=True)
    
    # Health Assessment
    status = Column(String(20), default=HealthStatus.UNKNOWN.value)
    confidence = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # AI Analysis Results
    posture_score = Column(Float, nullable=True)  # Body posture analysis
    coat_condition_score = Column(Float, nullable=True)  # Coat/skin condition
    mobility_score = Column(Float, nullable=True)  # Movement analysis
    alertness_score = Column(Float, nullable=True)  # Behavioral alertness
    
    # Detailed findings
    findings = Column(JSON, nullable=True)  # Detailed AI findings
    symptoms = Column(Text, nullable=True)  # Observed symptoms
    notes = Column(Text, nullable=True)  # Manual notes
    
    # Source information
    image_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    analysis_type = Column(String(50), default="image")  # image, video, manual
    
    # Veterinarian input
    vet_verified = Column(Integer, default=0)  # Boolean as int for SQLite
    vet_notes = Column(Text, nullable=True)
    vet_diagnosis = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    animal = relationship("Animal", back_populates="health_records")
    
    def __repr__(self):
        return f"<HealthRecord(id={self.id}, animal_id={self.animal_id}, status='{self.status}')>"
