"""Attendance tracking routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models.animal import Animal
from ..models.attendance import Attendance
from ..schemas.schemas import AttendanceCreate, AttendanceResponse
from ..services.attendance_service import AttendanceService

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("/today")
def get_today_attendance(db: Session = Depends(get_db)):
    """Get today's attendance summary."""
    service = AttendanceService(db)
    return service.get_today_attendance()


@router.get("/date/{target_date}")
def get_attendance_by_date(
    target_date: date,
    db: Session = Depends(get_db)
):
    """Get attendance for a specific date."""
    service = AttendanceService(db)
    return service.get_attendance_by_date(target_date)


@router.get("/animal/{animal_id}")
def get_animal_attendance(
    animal_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get attendance history for a specific animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    service = AttendanceService(db)
    records = service.get_animal_attendance_history(animal_id, days)
    
    # Calculate attendance rate
    total_days = min(days, (date.today() - animal.created_at.date()).days + 1)
    attendance_rate = len(records) / total_days * 100 if total_days > 0 else 0
    
    return {
        "animal": {
            "id": animal.id,
            "tag_id": animal.tag_id,
            "name": animal.name
        },
        "period_days": days,
        "total_present": len(records),
        "attendance_rate": round(attendance_rate, 2),
        "records": records
    }


@router.post("/mark", response_model=AttendanceResponse, status_code=201)
def mark_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db)
):
    """
    Manually mark attendance for an animal.
    
    - **animal_id**: ID of the animal
    - **detection_confidence**: Confidence score (0-1)
    - **identification_method**: How animal was identified (automatic, manual, ocr, muzzle)
    - **location_zone**: Optional location zone
    - **image_path**: Optional reference image path
    """
    animal = db.query(Animal).filter(Animal.id == data.animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    service = AttendanceService(db)
    record = service.mark_attendance(
        animal_id=data.animal_id,
        confidence=data.detection_confidence,
        method=data.identification_method,
        location_zone=data.location_zone,
        image_path=data.image_path
    )
    
    return record


@router.get("/stats")
def get_attendance_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get attendance statistics for the past N days."""
    service = AttendanceService(db)
    return service.get_attendance_stats(days)


@router.get("/missing")
def get_missing_animals(
    days: int = Query(1, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get animals missing from attendance in the past N days.
    Returns animals that were not detected for the specified period.
    """
    cutoff_date = date.today() - timedelta(days=days)
    
    # Get animals with recent attendance
    recent_attendance = db.query(Attendance.animal_id).filter(
        Attendance.date >= cutoff_date
    ).distinct().subquery()
    
    # Get animals NOT in recent attendance
    missing_animals = db.query(Animal).filter(
        ~Animal.id.in_(db.query(recent_attendance.c.animal_id))
    ).all()
    
    return {
        "period_days": days,
        "missing_count": len(missing_animals),
        "missing_animals": [
            {
                "id": a.id,
                "tag_id": a.tag_id,
                "name": a.name,
                "species": a.species,
                "last_seen": None  # Would need additional query for actual last seen
            }
            for a in missing_animals
        ]
    }


@router.post("/batch-mark")
def batch_mark_attendance(
    animal_ids: list[int],
    confidence: float = 1.0,
    method: str = "manual",
    db: Session = Depends(get_db)
):
    """Mark attendance for multiple animals at once."""
    service = AttendanceService(db)
    results = []
    
    for animal_id in animal_ids:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if animal:
            record = service.mark_attendance(
                animal_id=animal_id,
                confidence=confidence,
                method=method
            )
            results.append({
                "animal_id": animal_id,
                "tag_id": animal.tag_id,
                "marked": True
            })
        else:
            results.append({
                "animal_id": animal_id,
                "marked": False,
                "error": "Animal not found"
            })
    
    return {
        "processed": len(animal_ids),
        "successful": sum(1 for r in results if r["marked"]),
        "results": results
    }
