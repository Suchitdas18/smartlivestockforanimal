"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .config import settings
from .database import init_db
from .routes import (
    animals_router,
    health_router,
    attendance_router,
    upload_router,
    dashboard_router,
    detection_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🐄 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Ensure upload directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "videos"), exist_ok=True)
    print("✅ Upload directories ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Smart Livestock AI")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🐄 **Smart Livestock AI** - AI-powered livestock health monitoring and identification system.
    
    ## Features
    
    * **Animal Detection** - Detect animals in images using YOLOv8
    * **Health Assessment** - CNN-based health classification (Healthy / Needs Attention / Critical)
    * **Animal Identification** - OCR for ear tags and QR codes
    * **Attendance Tracking** - Automatic daily attendance
    * **Alerts** - Health alerts and notifications
    * **Dashboard** - Comprehensive analytics
    
    ## Quick Start
    
    1. Seed demo data: `POST /api/dashboard/seed-demo-data`
    2. View dashboard: `GET /api/dashboard/stats`
    3. Upload image: `POST /api/upload/analyze-image`
    
    Built for farmers and veterinarians. Optimized for rural environments.
    """,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(animals_router)
app.include_router(health_router)
app.include_router(attendance_router)
app.include_router(upload_router)
app.include_router(dashboard_router)
app.include_router(detection_router)


@app.get("/", tags=["Root"])
def root():
    """Root endpoint - API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "animals": "/api/animals",
            "health": "/api/health",
            "attendance": "/api/attendance",
            "upload": "/api/upload",
            "detection": "/api/detect",
            "dashboard": "/api/dashboard"
        }
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.APP_NAME}


@app.get("/api", tags=["Root"])
def api_info():
    """API information endpoint."""
    return {
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/animals", "description": "Animal management"},
            {"path": "/api/health", "description": "Health assessment"},
            {"path": "/api/attendance", "description": "Attendance tracking"},
            {"path": "/api/upload", "description": "File uploads"},
            {"path": "/api/detect", "description": "AI detection"},
            {"path": "/api/dashboard", "description": "Dashboard & stats"}
        ]
    }
