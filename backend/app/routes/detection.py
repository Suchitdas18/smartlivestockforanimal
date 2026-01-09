"""Animal detection and identification routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models.animal import Animal
from ..services.ai_detection import detection_service
from ..services.ocr_service import ocr_service
from ..services.attendance_service import AttendanceService
from ..schemas.schemas import (
    DetectionRequest,
    DetectionResponse,
    IdentificationRequest,
    IdentificationResponse,
    DetectedAnimal,
    BoundingBox
)

router = APIRouter(prefix="/api/detect", tags=["Detection"])


@router.post("/animals", response_model=DetectionResponse)
def detect_animals(request: DetectionRequest, db: Session = Depends(get_db)):
    """
    Detect animals in an image using YOLOv8.
    
    Returns bounding boxes and species classification for each detected animal.
    """
    result = detection_service.detect_animals(request.image_path)
    
    # Try to match detected animals with database records
    detected_animals = []
    for detection in result["detected_animals"]:
        detected_animal = DetectedAnimal(
            bounding_box=BoundingBox(**detection["bounding_box"]),
            species=detection["species"],
            confidence=detection["confidence"],
            animal_id=None,
            tag_id=None
        )
        detected_animals.append(detected_animal)
    
    return DetectionResponse(
        image_path=result["image_path"],
        detected_animals=detected_animals,
        total_detected=result["total_detected"],
        processing_time_ms=result["processing_time_ms"]
    )


@router.post("/identify", response_model=IdentificationResponse)
def identify_animal(request: IdentificationRequest, db: Session = Depends(get_db)):
    """
    Identify an animal from an image.
    
    Methods:
    - OCR: Read ear tag or QR code
    - Muzzle print: Match against stored muzzle prints (optional)
    
    Returns animal ID if found in database, or tag_id for new registration.
    """
    result = ocr_service.identify_animal(
        image_path=request.image_path,
        use_ocr=request.use_ocr,
        use_muzzle=request.use_muzzle
    )
    
    # Try to find animal in database
    animal_id = None
    if result.get("tag_id"):
        animal = db.query(Animal).filter(Animal.tag_id == result["tag_id"]).first()
        if animal:
            animal_id = animal.id
    
    return IdentificationResponse(
        identified=result.get("identified", False),
        method=result.get("method", "unknown"),
        tag_id=result.get("tag_id"),
        animal_id=animal_id,
        confidence=result.get("confidence", 0.0),
        needs_manual_review=result.get("needs_manual_review", True),
        ocr_text=result.get("ocr_text")
    )


@router.post("/identify-and-attend")
def identify_and_mark_attendance(
    request: IdentificationRequest,
    db: Session = Depends(get_db)
):
    """
    Identify an animal and automatically mark attendance.
    
    This combines identification and attendance marking in one call.
    """
    # Identify the animal
    id_result = ocr_service.identify_animal(
        image_path=request.image_path,
        use_ocr=request.use_ocr,
        use_muzzle=request.use_muzzle
    )
    
    attendance_marked = False
    animal_data = None
    
    if id_result.get("identified") and id_result.get("tag_id"):
        # Find animal in database
        animal = db.query(Animal).filter(Animal.tag_id == id_result["tag_id"]).first()
        
        if animal:
            # Mark attendance
            attendance_service = AttendanceService(db)
            attendance = attendance_service.mark_attendance(
                animal_id=animal.id,
                confidence=id_result.get("confidence", 0.5),
                method=id_result.get("method", "ocr"),
                image_path=request.image_path
            )
            attendance_marked = True
            animal_data = {
                "id": animal.id,
                "tag_id": animal.tag_id,
                "name": animal.name,
                "species": animal.species,
                "current_health_status": animal.current_health_status
            }
    
    return {
        "identification": id_result,
        "attendance_marked": attendance_marked,
        "animal": animal_data
    }


@router.post("/batch-detect")
def batch_detect_animals(
    image_paths: list[str],
    mark_attendance: bool = False,
    db: Session = Depends(get_db)
):
    """
    Detect animals in multiple images.
    
    Optionally marks attendance for identified animals.
    """
    results = []
    total_detected = 0
    
    for image_path in image_paths:
        # Detect animals
        detection = detection_service.detect_animals(image_path)
        total_detected += detection["total_detected"]
        
        # Try to identify each detection
        identifications = []
        if detection["total_detected"] > 0:
            id_result = ocr_service.identify_animal(image_path, use_ocr=True)
            if id_result.get("identified"):
                identifications.append(id_result)
                
                # Mark attendance if requested
                if mark_attendance and id_result.get("tag_id"):
                    animal = db.query(Animal).filter(
                        Animal.tag_id == id_result["tag_id"]
                    ).first()
                    if animal:
                        attendance_service = AttendanceService(db)
                        attendance_service.mark_attendance(
                            animal_id=animal.id,
                            confidence=id_result.get("confidence", 0.5),
                            method="batch_detection",
                            image_path=image_path
                        )
        
        results.append({
            "image_path": image_path,
            "detection": detection,
            "identifications": identifications
        })
    
    return {
        "processed_images": len(image_paths),
        "total_animals_detected": total_detected,
        "results": results
    }


@router.post("/read-tag")
def read_ear_tag(image_path: str, db: Session = Depends(get_db)):
    """
    Read ear tag from an image using OCR.
    
    Returns the extracted text and confidence score.
    """
    result = ocr_service.read_ear_tag(image_path)
    
    # Try to find matching animal
    animal_data = None
    if result.get("success") and result.get("text"):
        animal = db.query(Animal).filter(Animal.tag_id == result["text"]).first()
        if animal:
            animal_data = {
                "id": animal.id,
                "tag_id": animal.tag_id,
                "name": animal.name,
                "species": animal.species
            }
    
    return {
        **result,
        "animal": animal_data
    }


@router.post("/read-qr")
def read_qr_code(image_path: str, db: Session = Depends(get_db)):
    """
    Read QR code from an image.
    
    Returns the decoded data and any matching animal information.
    """
    result = ocr_service.read_qr_code(image_path)
    
    # Try to find matching animal from QR data
    animal_data = None
    if result.get("success") and result.get("data"):
        qr_data = result["data"]
        # Try tag_id from QR data
        if qr_data.get("tag_id"):
            animal = db.query(Animal).filter(
                Animal.tag_id == qr_data["tag_id"]
            ).first()
            if animal:
                animal_data = {
                    "id": animal.id,
                    "tag_id": animal.tag_id,
                    "name": animal.name,
                    "species": animal.species
                }
    
    return {
        **result,
        "animal": animal_data
    }
