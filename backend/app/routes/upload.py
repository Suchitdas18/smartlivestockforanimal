"""File upload routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime

from ..database import get_db
from ..utils.file_handler import file_handler
from ..schemas.schemas import UploadResponse

router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    subfolder: str = None
):
    """
    Upload an image file.
    
    Supported formats: JPEG, PNG, WebP
    Max size: 50MB
    """
    result = await file_handler.save_upload(file, "image", subfolder)
    
    return UploadResponse(
        filename=result["filename"],
        file_path=result["file_path"],
        file_type=result["file_type"],
        file_size=result["file_size"],
        upload_time=result["upload_time"]
    )


@router.post("/video", response_model=UploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    subfolder: str = None
):
    """
    Upload a video file.
    
    Supported formats: MP4, MPEG, MOV, AVI
    Max size: 50MB
    """
    result = await file_handler.save_upload(file, "video", subfolder)
    
    return UploadResponse(
        filename=result["filename"],
        file_path=result["file_path"],
        file_type=result["file_type"],
        file_size=result["file_size"],
        upload_time=result["upload_time"]
    )


@router.post("/analyze-image")
async def upload_and_analyze_image(
    file: UploadFile = File(...),
    animal_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Upload an image and run full analysis pipeline.
    
    This combines:
    1. File upload
    2. Animal detection
    3. Animal identification (OCR)
    4. Health assessment
    5. Attendance marking
    """
    from ..services.ai_detection import detection_service
    from ..services.health_classifier import health_classifier
    from ..services.ocr_service import ocr_service
    from ..services.attendance_service import AttendanceService
    from ..models.animal import Animal
    
    # Upload the file
    result = await file_handler.save_upload(file, "image")
    image_path = result["file_path"]
    
    # Run detection
    detection_result = detection_service.detect_animals(image_path)
    
    # Run health classification
    health_result = health_classifier.classify_health(image_path, animal_id)
    
    # Try to identify animal
    identification_result = ocr_service.identify_animal(image_path, use_ocr=True)
    
    # If animal identified or provided, mark attendance
    attendance_marked = False
    resolved_animal_id = animal_id
    
    if identification_result.get("identified") and identification_result.get("tag_id"):
        # Try to find animal by tag
        animal = db.query(Animal).filter(
            Animal.tag_id == identification_result["tag_id"]
        ).first()
        if animal:
            resolved_animal_id = animal.id
    
    if resolved_animal_id:
        attendance_service = AttendanceService(db)
        attendance_service.mark_attendance(
            animal_id=resolved_animal_id,
            confidence=identification_result.get("confidence", 0.5),
            method=identification_result.get("method", "automatic"),
            image_path=image_path
        )
        attendance_marked = True
    
    return {
        "upload": {
            "filename": result["filename"],
            "file_path": image_path,
            "file_size": result["file_size"]
        },
        "detection": detection_result,
        "health": health_result,
        "identification": identification_result,
        "attendance_marked": attendance_marked,
        "resolved_animal_id": resolved_animal_id
    }


@router.get("/file/{file_type}/{filename}")
async def get_file(file_type: str, filename: str):
    """Retrieve an uploaded file."""
    if file_type not in ["images", "videos"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = file_handler.upload_dir / file_type / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@router.get("/list/{file_type}")
async def list_files(file_type: str = "image"):
    """List uploaded files."""
    if file_type not in ["image", "video"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Use 'image' or 'video'")
    
    files = file_handler.list_files(file_type)
    
    return {
        "file_type": file_type,
        "count": len(files),
        "files": files
    }


@router.delete("/file/{file_type}/{filename}")
async def delete_file(file_type: str, filename: str):
    """Delete an uploaded file."""
    if file_type not in ["images", "videos"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    file_path = str(file_handler.upload_dir / file_type / filename)
    
    if file_handler.delete_file(file_path):
        return {"message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found or could not be deleted")
