"""Services package."""
from .ai_detection import AIDetectionService, detection_service
from .health_classifier import HealthClassificationService, health_classifier
from .ocr_service import OCRService
from .attendance_service import AttendanceService

__all__ = [
    "AIDetectionService", 
    "HealthClassificationService", 
    "OCRService", 
    "AttendanceService",
    "detection_service",
    "health_classifier"
]

