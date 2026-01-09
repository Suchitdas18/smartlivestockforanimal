"""Health assessment routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models.animal import Animal
from ..models.health_record import HealthRecord
from ..models.alert import Alert
from ..schemas.schemas import (
    HealthRecordCreate,
    HealthRecordResponse,
    HealthAssessmentRequest,
    HealthAssessmentResponse,
    HealthStatusEnum
)
from ..services.health_classifier import health_classifier

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.post("/assess", response_model=HealthAssessmentResponse)
def assess_health(request: HealthAssessmentRequest, db: Session = Depends(get_db)):
    """
    Assess animal health from an image using AI.
    
    - **image_path**: Path to the uploaded image
    - **animal_id**: Optional animal ID to link the assessment
    
    Returns health status classification with confidence scores.
    """
    # Run AI health classification
    result = health_classifier.classify_health(
        image_path=request.image_path,
        animal_id=request.animal_id
    )
    
    # If animal_id provided, create health record and update animal
    health_record_id = None
    if request.animal_id:
        animal = db.query(Animal).filter(Animal.id == request.animal_id).first()
        if animal:
            # Create health record
            health_record = HealthRecord(
                animal_id=request.animal_id,
                status=result["status"],
                confidence=result["confidence"],
                posture_score=result["posture_score"],
                coat_condition_score=result["coat_condition_score"],
                mobility_score=result["mobility_score"],
                alertness_score=result["alertness_score"],
                findings=result["findings"],
                image_path=request.image_path,
                analysis_type="image"
            )
            db.add(health_record)
            db.commit()
            db.refresh(health_record)
            health_record_id = health_record.id
            
            # Update animal's current health status
            animal.current_health_status = result["status"]
            animal.last_health_check = datetime.utcnow()
            db.commit()
            
            # Create alert if unhealthy
            if result["status"] in ["critical", "needs_attention"]:
                severity = "critical" if result["status"] == "critical" else "medium"
                alert_type = "health_critical" if result["status"] == "critical" else "health_attention"
                
                alert = Alert(
                    animal_id=request.animal_id,
                    alert_type=alert_type,
                    severity=severity,
                    title=f"Health Alert: {animal.tag_id}",
                    message=f"Animal {animal.tag_id} has been classified as '{result['status']}' with {result['confidence']*100:.1f}% confidence.",
                    health_record_id=health_record_id,
                    image_path=request.image_path
                )
                db.add(alert)
                db.commit()
    
    return HealthAssessmentResponse(
        status=HealthStatusEnum(result["status"]),
        confidence=result["confidence"],
        posture_score=result["posture_score"],
        coat_condition_score=result["coat_condition_score"],
        mobility_score=result["mobility_score"],
        alertness_score=result["alertness_score"],
        findings=result["findings"],
        recommendations=result["recommendations"],
        animal_id=request.animal_id,
        health_record_id=health_record_id
    )


@router.get("/records/{animal_id}")
def get_health_records(
    animal_id: int,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get health records for a specific animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    records = db.query(HealthRecord).filter(
        HealthRecord.animal_id == animal_id
    ).order_by(HealthRecord.created_at.desc()).limit(limit).all()
    
    return {
        "animal_id": animal_id,
        "animal_tag": animal.tag_id,
        "current_status": animal.current_health_status,
        "records": records,
        "total_records": len(records)
    }


@router.post("/records", response_model=HealthRecordResponse, status_code=201)
def create_health_record(record: HealthRecordCreate, db: Session = Depends(get_db)):
    """Create a manual health record."""
    animal = db.query(Animal).filter(Animal.id == record.animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    health_record = HealthRecord(
        animal_id=record.animal_id,
        status=record.status.value,
        confidence=record.confidence,
        posture_score=record.posture_score,
        coat_condition_score=record.coat_condition_score,
        mobility_score=record.mobility_score,
        alertness_score=record.alertness_score,
        findings=record.findings,
        symptoms=record.symptoms,
        notes=record.notes,
        image_path=record.image_path,
        analysis_type="manual"
    )
    
    db.add(health_record)
    
    # Update animal's health status
    animal.current_health_status = record.status.value
    animal.last_health_check = datetime.utcnow()
    
    db.commit()
    db.refresh(health_record)
    
    return health_record


@router.get("/record/{record_id}", response_model=HealthRecordResponse)
def get_health_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific health record."""
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record


@router.put("/record/{record_id}/verify")
def verify_health_record(
    record_id: int,
    vet_notes: Optional[str] = None,
    vet_diagnosis: Optional[str] = None,
    verified_by: str = "veterinarian",
    db: Session = Depends(get_db)
):
    """Verify a health record (veterinarian confirmation)."""
    record = db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Health record not found")
    
    record.vet_verified = 1
    record.vet_notes = vet_notes
    record.vet_diagnosis = vet_diagnosis
    
    db.commit()
    db.refresh(record)
    
    return {
        "message": "Health record verified",
        "record": record
    }


@router.get("/summary")
def get_health_summary(db: Session = Depends(get_db)):
    """Get overall health summary of all animals."""
    from sqlalchemy import func
    
    total = db.query(Animal).count()
    
    # Count by health status
    status_counts = db.query(
        Animal.current_health_status,
        func.count(Animal.id)
    ).group_by(Animal.current_health_status).all()
    
    status_dict = dict(status_counts)
    
    # Get recent critical cases
    critical_animals = db.query(Animal).filter(
        Animal.current_health_status == "critical"
    ).limit(5).all()
    
    # Get recent health checks
    recent_checks = db.query(HealthRecord).order_by(
        HealthRecord.created_at.desc()
    ).limit(10).all()
    
    return {
        "total_animals": total,
        "health_distribution": {
            "healthy": status_dict.get("healthy", 0),
            "needs_attention": status_dict.get("needs_attention", 0),
            "critical": status_dict.get("critical", 0),
            "unknown": status_dict.get("unknown", 0)
        },
        "critical_animals": critical_animals,
        "recent_health_checks": recent_checks
    }
