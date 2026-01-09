"""Pydantic schemas for API request/response validation."""
from .schemas import (
    # Animal schemas
    AnimalBase,
    AnimalCreate,
    AnimalUpdate,
    AnimalResponse,
    AnimalListResponse,
    
    # Health schemas
    HealthRecordBase,
    HealthRecordCreate,
    HealthRecordResponse,
    HealthAssessmentRequest,
    HealthAssessmentResponse,
    
    # Attendance schemas
    AttendanceBase,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceSummary,
    
    # Alert schemas
    AlertBase,
    AlertCreate,
    AlertResponse,
    
    # Dashboard schemas
    DashboardStats,
    
    # Detection schemas
    DetectionRequest,
    DetectionResponse,
    BoundingBox,
    DetectedAnimal,
    
    # Identification schemas
    IdentificationRequest,
    IdentificationResponse,
    
    # Upload schemas
    UploadResponse,
)

__all__ = [
    "AnimalBase", "AnimalCreate", "AnimalUpdate", "AnimalResponse", "AnimalListResponse",
    "HealthRecordBase", "HealthRecordCreate", "HealthRecordResponse", 
    "HealthAssessmentRequest", "HealthAssessmentResponse",
    "AttendanceBase", "AttendanceCreate", "AttendanceResponse", "AttendanceSummary",
    "AlertBase", "AlertCreate", "AlertResponse",
    "DashboardStats",
    "DetectionRequest", "DetectionResponse", "BoundingBox", "DetectedAnimal",
    "IdentificationRequest", "IdentificationResponse",
    "UploadResponse",
]
