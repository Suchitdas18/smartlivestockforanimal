"""Animal management routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.animal import Animal
from ..schemas.schemas import (
    AnimalCreate,
    AnimalUpdate,
    AnimalResponse,
    AnimalListResponse
)

router = APIRouter(prefix="/api/animals", tags=["Animals"])


@router.get("", response_model=AnimalListResponse)
def list_animals(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    species: Optional[str] = None,
    health_status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all animals with pagination and filters.
    
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)
    - **species**: Filter by species
    - **health_status**: Filter by health status
    - **search**: Search by tag_id or name
    """
    query = db.query(Animal)
    
    # Apply filters
    if species:
        query = query.filter(Animal.species == species)
    if health_status:
        query = query.filter(Animal.current_health_status == health_status)
    if search:
        query = query.filter(
            (Animal.tag_id.ilike(f"%{search}%")) |
            (Animal.name.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    animals = query.order_by(Animal.created_at.desc()).offset(offset).limit(per_page).all()
    
    return AnimalListResponse(
        items=animals,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    """Get a specific animal by ID."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@router.get("/tag/{tag_id}", response_model=AnimalResponse)
def get_animal_by_tag(tag_id: str, db: Session = Depends(get_db)):
    """Get a specific animal by tag ID."""
    animal = db.query(Animal).filter(Animal.tag_id == tag_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    return animal


@router.post("", response_model=AnimalResponse, status_code=201)
def create_animal(animal_data: AnimalCreate, db: Session = Depends(get_db)):
    """
    Create a new animal.
    
    Required fields:
    - **tag_id**: Unique identifier (ear tag number)
    
    Optional fields:
    - **name**: Animal's name
    - **species**: Species type (cattle, goat, sheep, pig, horse, poultry, other)
    - **breed**: Breed name
    - **age_months**: Age in months
    - **gender**: male, female, or unknown
    - **weight_kg**: Weight in kilograms
    - **notes**: Additional notes
    """
    # Check if tag_id already exists
    existing = db.query(Animal).filter(Animal.tag_id == animal_data.tag_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Animal with this tag_id already exists")
    
    # Create animal
    animal = Animal(
        tag_id=animal_data.tag_id,
        name=animal_data.name,
        species=animal_data.species.value,
        breed=animal_data.breed,
        age_months=animal_data.age_months,
        gender=animal_data.gender.value,
        weight_kg=animal_data.weight_kg,
        notes=animal_data.notes,
        ear_tag_number=animal_data.ear_tag_number,
        qr_code=animal_data.qr_code,
        current_health_status="unknown"
    )
    
    db.add(animal)
    db.commit()
    db.refresh(animal)
    
    return animal


@router.put("/{animal_id}", response_model=AnimalResponse)
def update_animal(
    animal_id: int,
    animal_data: AnimalUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    # Update fields that are provided
    update_data = animal_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, 'value'):  # Handle enums
                setattr(animal, field, value.value)
            else:
                setattr(animal, field, value)
    
    animal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(animal)
    
    return animal


@router.delete("/{animal_id}", status_code=204)
def delete_animal(animal_id: int, db: Session = Depends(get_db)):
    """Delete an animal."""
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    db.delete(animal)
    db.commit()
    
    return None


@router.get("/{animal_id}/health-history")
def get_animal_health_history(
    animal_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get health history for an animal."""
    from ..models.health_record import HealthRecord
    
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    records = db.query(HealthRecord).filter(
        HealthRecord.animal_id == animal_id
    ).order_by(HealthRecord.created_at.desc()).limit(limit).all()
    
    return {
        "animal": animal,
        "health_records": records
    }


@router.get("/{animal_id}/attendance-history")
def get_animal_attendance_history(
    animal_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get attendance history for an animal."""
    from ..services.attendance_service import AttendanceService
    
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    
    attendance_service = AttendanceService(db)
    records = attendance_service.get_animal_attendance_history(animal_id, days)
    
    return {
        "animal": animal,
        "attendance_records": records,
        "period_days": days
    }
