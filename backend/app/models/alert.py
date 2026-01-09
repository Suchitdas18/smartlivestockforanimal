"""Alert database model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class AlertType(str, enum.Enum):
    HEALTH_CRITICAL = "health_critical"
    HEALTH_ATTENTION = "health_attention"
    MISSING_ANIMAL = "missing_animal"
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    SYSTEM = "system"


class Severity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    """Alert model for notifications about animal health and status."""
    
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=True, index=True)
    
    # Alert details
    alert_type = Column(String(50), default=AlertType.SYSTEM.value)
    severity = Column(String(20), default=Severity.MEDIUM.value)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    resolved = Column(Integer, default=0)  # Boolean as int for SQLite
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Reference
    health_record_id = Column(Integer, nullable=True)
    image_path = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    animal = relationship("Animal", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.alert_type}', severity='{self.severity}')>"
