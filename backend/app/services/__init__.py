"""Services package."""
from .ai_detection import AIDetectionService
from .health_classifier import HealthClassifierService
from .ocr_service import OCRService
from .attendance_service import AttendanceService

__all__ = ["AIDetectionService", "HealthClassifierService", "OCRService", "AttendanceService"]
