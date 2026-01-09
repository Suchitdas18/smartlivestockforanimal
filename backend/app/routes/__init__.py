"""API Routes package."""
from .animals import router as animals_router
from .health import router as health_router
from .attendance import router as attendance_router
from .upload import router as upload_router
from .dashboard import router as dashboard_router
from .detection import router as detection_router

__all__ = [
    "animals_router",
    "health_router", 
    "attendance_router",
    "upload_router",
    "dashboard_router",
    "detection_router"
]
