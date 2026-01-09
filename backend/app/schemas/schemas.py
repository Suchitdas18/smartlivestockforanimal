"""Pydantic schemas for API validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============== Enums ==============

class SpeciesEnum(str, Enum):
    CATTLE = "cattle"
    GOAT = "goat"
    SHEEP = "sheep"
    PIG = "pig"
    HORSE = "horse"
    POULTRY = "poultry"
    OTHER = "other"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class HealthStatusEnum(str, Enum):
    HEALTHY = "healthy"
    NEEDS_ATTENTION = "needs_attention"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class AlertTypeEnum(str, Enum):
    HEALTH_CRITICAL = "health_critical"
    HEALTH_ATTENTION = "health_attention"
    MISSING_ANIMAL = "missing_animal"
    UNUSUAL_BEHAVIOR = "unusual_behavior"
    SYSTEM = "system"


class SeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============== Animal Schemas ==============

class AnimalBase(BaseModel):
    """Base animal schema."""
    tag_id: str = Field(..., min_length=1, max_length=50)
    name: Optional[str] = None
    species: SpeciesEnum = SpeciesEnum.CATTLE
    breed: Optional[str] = None
    age_months: Optional[int] = Field(None, ge=0)
    gender: GenderEnum = GenderEnum.UNKNOWN
    weight_kg: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class AnimalCreate(AnimalBase):
    """Schema for creating an animal."""
    ear_tag_number: Optional[str] = None
    qr_code: Optional[str] = None


class AnimalUpdate(BaseModel):
    """Schema for updating an animal."""
    name: Optional[str] = None
    species: Optional[SpeciesEnum] = None
    breed: Optional[str] = None
    age_months: Optional[int] = Field(None, ge=0)
    gender: Optional[GenderEnum] = None
    weight_kg: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    ear_tag_number: Optional[str] = None
    qr_code: Optional[str] = None


class AnimalResponse(AnimalBase):
    """Schema for animal response."""
    id: int
    ear_tag_number: Optional[str] = None
    qr_code: Optional[str] = None
    image_path: Optional[str] = None
    current_health_status: str = "unknown"
    last_health_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnimalListResponse(BaseModel):
    """Schema for paginated animal list."""
    items: List[AnimalResponse]
    total: int
    page: int
    per_page: int


# ============== Health Record Schemas ==============

class HealthRecordBase(BaseModel):
    """Base health record schema."""
    status: HealthStatusEnum = HealthStatusEnum.UNKNOWN
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    symptoms: Optional[str] = None
    notes: Optional[str] = None


class HealthRecordCreate(HealthRecordBase):
    """Schema for creating a health record."""
    animal_id: int
    posture_score: Optional[float] = None
    coat_condition_score: Optional[float] = None
    mobility_score: Optional[float] = None
    alertness_score: Optional[float] = None
    findings: Optional[Dict[str, Any]] = None
    image_path: Optional[str] = None


class HealthRecordResponse(HealthRecordBase):
    """Schema for health record response."""
    id: int
    animal_id: int
    posture_score: Optional[float] = None
    coat_condition_score: Optional[float] = None
    mobility_score: Optional[float] = None
    alertness_score: Optional[float] = None
    findings: Optional[Dict[str, Any]] = None
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    analysis_type: str
    vet_verified: bool = False
    vet_notes: Optional[str] = None
    vet_diagnosis: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class HealthAssessmentRequest(BaseModel):
    """Request schema for health assessment."""
    image_path: str
    animal_id: Optional[int] = None


class HealthAssessmentResponse(BaseModel):
    """Response schema for health assessment."""
    status: HealthStatusEnum
    confidence: float
    posture_score: float
    coat_condition_score: float
    mobility_score: float
    alertness_score: float
    findings: Dict[str, Any]
    recommendations: List[str]
    animal_id: Optional[int] = None
    health_record_id: Optional[int] = None


# ============== Attendance Schemas ==============

class AttendanceBase(BaseModel):
    """Base attendance schema."""
    animal_id: int
    date: date
    detection_confidence: float = Field(0.0, ge=0.0, le=1.0)


class AttendanceCreate(BaseModel):
    """Schema for creating attendance."""
    animal_id: int
    detection_confidence: float = Field(0.0, ge=0.0, le=1.0)
    identification_method: str = "automatic"
    location_zone: Optional[str] = None
    image_path: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response."""
    id: int
    detected_at: datetime
    identification_method: str
    location_zone: Optional[str] = None
    image_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Summary of attendance for a date."""
    date: date
    total_animals: int
    animals_detected: int
    attendance_rate: float
    missing_animals: List[AnimalResponse]


# ============== Alert Schemas ==============

class AlertBase(BaseModel):
    """Base alert schema."""
    alert_type: AlertTypeEnum
    severity: SeverityEnum
    title: str
    message: str


class AlertCreate(AlertBase):
    """Schema for creating an alert."""
    animal_id: Optional[int] = None
    health_record_id: Optional[int] = None
    image_path: Optional[str] = None


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    animal_id: Optional[int] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    animal: Optional[AnimalResponse] = None
    
    class Config:
        from_attributes = True


# ============== Dashboard Schemas ==============

class HealthDistribution(BaseModel):
    """Health status distribution."""
    healthy: int
    needs_attention: int
    critical: int
    unknown: int


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_animals: int
    health_distribution: HealthDistribution
    todays_attendance: int
    attendance_rate: float
    recent_alerts: List[AlertResponse]
    animals_needing_attention: List[AnimalResponse]
    recent_health_checks: int
    species_distribution: Dict[str, int]


# ============== Detection Schemas ==============

class BoundingBox(BaseModel):
    """Bounding box for detected object."""
    x1: float
    y1: float
    x2: float
    y2: float


class DetectedAnimal(BaseModel):
    """Detected animal in an image."""
    bounding_box: BoundingBox
    species: str
    confidence: float
    animal_id: Optional[int] = None
    tag_id: Optional[str] = None


class DetectionRequest(BaseModel):
    """Request for animal detection."""
    image_path: str


class DetectionResponse(BaseModel):
    """Response from animal detection."""
    image_path: str
    detected_animals: List[DetectedAnimal]
    total_detected: int
    processing_time_ms: float


# ============== Identification Schemas ==============

class IdentificationRequest(BaseModel):
    """Request for animal identification."""
    image_path: str
    use_ocr: bool = True
    use_muzzle: bool = False


class IdentificationResponse(BaseModel):
    """Response from animal identification."""
    identified: bool
    method: str  # ocr, muzzle, manual
    tag_id: Optional[str] = None
    animal_id: Optional[int] = None
    confidence: float
    needs_manual_review: bool
    ocr_text: Optional[str] = None


# ============== Upload Schemas ==============

class UploadResponse(BaseModel):
    """Response from file upload."""
    filename: str
    file_path: str
    file_type: str
    file_size: int
    upload_time: datetime
