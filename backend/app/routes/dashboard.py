"""Dashboard routes for statistics and alerts."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Optional

from ..database import get_db
from ..models.animal import Animal
from ..models.health_record import HealthRecord
from ..models.attendance import Attendance
from ..models.alert import Alert
from ..schemas.schemas import DashboardStats, HealthDistribution, AlertResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard statistics.
    
    Includes:
    - Total animal count
    - Health distribution
    - Today's attendance
    - Recent alerts
    - Animals needing attention
    """
    # Total animals
    total_animals = db.query(Animal).count()
    
    # Health distribution
    health_counts = db.query(
        Animal.current_health_status,
        func.count(Animal.id)
    ).group_by(Animal.current_health_status).all()
    
    health_dict = dict(health_counts)
    health_distribution = HealthDistribution(
        healthy=health_dict.get("healthy", 0),
        needs_attention=health_dict.get("needs_attention", 0),
        critical=health_dict.get("critical", 0),
        unknown=health_dict.get("unknown", 0)
    )
    
    # Today's attendance
    today = date.today()
    todays_attendance = db.query(Attendance).filter(
        Attendance.date == today
    ).count()
    
    attendance_rate = (todays_attendance / total_animals * 100) if total_animals > 0 else 0
    
    # Recent alerts (unresolved)
    recent_alerts = db.query(Alert).filter(
        Alert.resolved == 0
    ).order_by(Alert.created_at.desc()).limit(10).all()
    
    # Animals needing attention
    attention_animals = db.query(Animal).filter(
        Animal.current_health_status.in_(["critical", "needs_attention"])
    ).limit(10).all()
    
    # Recent health checks (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_health_checks = db.query(HealthRecord).filter(
        HealthRecord.created_at >= yesterday
    ).count()
    
    # Species distribution
    species_counts = db.query(
        Animal.species,
        func.count(Animal.id)
    ).group_by(Animal.species).all()
    
    species_distribution = dict(species_counts)
    
    return DashboardStats(
        total_animals=total_animals,
        health_distribution=health_distribution,
        todays_attendance=todays_attendance,
        attendance_rate=round(attendance_rate, 2),
        recent_alerts=recent_alerts,
        animals_needing_attention=attention_animals,
        recent_health_checks=recent_health_checks,
        species_distribution=species_distribution
    )


@router.get("/alerts")
def get_alerts(
    resolved: Optional[bool] = None,
    severity: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get alerts with optional filters."""
    query = db.query(Alert)
    
    if resolved is not None:
        query = query.filter(Alert.resolved == (1 if resolved else 0))
    if severity:
        query = query.filter(Alert.severity == severity)
    
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return {
        "alerts": alerts,
        "total": len(alerts)
    }


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Include animal info if available
    animal = None
    if alert.animal_id:
        animal = db.query(Animal).filter(Animal.id == alert.animal_id).first()
    
    return {
        "alert": alert,
        "animal": animal
    }


@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    resolution_notes: str = None,
    resolved_by: str = "system",
    db: Session = Depends(get_db)
):
    """Mark an alert as resolved."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.resolved = 1
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = resolved_by
    alert.resolution_notes = resolution_notes
    
    db.commit()
    db.refresh(alert)
    
    return {"message": "Alert resolved", "alert": alert}


@router.get("/trends/health")
def get_health_trends(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get health trends over time."""
    trends = []
    
    for i in range(days):
        target_date = date.today() - timedelta(days=i)
        target_datetime = datetime.combine(target_date, datetime.min.time())
        next_datetime = datetime.combine(target_date + timedelta(days=1), datetime.min.time())
        
        # Get health records for this date
        records = db.query(
            HealthRecord.status,
            func.count(HealthRecord.id)
        ).filter(
            HealthRecord.created_at >= target_datetime,
            HealthRecord.created_at < next_datetime
        ).group_by(HealthRecord.status).all()
        
        record_dict = dict(records)
        
        trends.append({
            "date": target_date.isoformat(),
            "healthy": record_dict.get("healthy", 0),
            "needs_attention": record_dict.get("needs_attention", 0),
            "critical": record_dict.get("critical", 0),
            "total_checks": sum(record_dict.values())
        })
    
    return {
        "period_days": days,
        "trends": trends
    }


@router.get("/trends/attendance")
def get_attendance_trends(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get attendance trends over time."""
    total_animals = db.query(Animal).count()
    trends = []
    
    for i in range(days):
        target_date = date.today() - timedelta(days=i)
        
        attendance_count = db.query(Attendance).filter(
            Attendance.date == target_date
        ).count()
        
        rate = (attendance_count / total_animals * 100) if total_animals > 0 else 0
        
        trends.append({
            "date": target_date.isoformat(),
            "present": attendance_count,
            "total": total_animals,
            "rate": round(rate, 2)
        })
    
    return {
        "period_days": days,
        "trends": trends
    }


@router.get("/quick-stats")
def get_quick_stats(db: Session = Depends(get_db)):
    """Get quick statistics for dashboard widgets."""
    today = date.today()
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    # Basic counts
    total_animals = db.query(Animal).count()
    critical_count = db.query(Animal).filter(Animal.current_health_status == "critical").count()
    attention_count = db.query(Animal).filter(Animal.current_health_status == "needs_attention").count()
    healthy_count = db.query(Animal).filter(Animal.current_health_status == "healthy").count()
    
    # Today's attendance
    todays_attendance = db.query(Attendance).filter(Attendance.date == today).count()
    
    # Unresolved alerts
    unresolved_alerts = db.query(Alert).filter(Alert.resolved == 0).count()
    
    # Recent health checks
    recent_checks = db.query(HealthRecord).filter(
        HealthRecord.created_at >= yesterday
    ).count()
    
    return {
        "total_animals": total_animals,
        "critical": critical_count,
        "needs_attention": attention_count,
        "healthy": healthy_count,
        "todays_attendance": todays_attendance,
        "attendance_rate": round((todays_attendance / total_animals * 100) if total_animals > 0 else 0, 1),
        "unresolved_alerts": unresolved_alerts,
        "recent_health_checks": recent_checks
    }


@router.post("/seed-demo-data")
def seed_demo_data(db: Session = Depends(get_db)):
    """
    Seed demo data for hackathon demonstration.
    Creates sample animals, health records, attendance, and alerts.
    """
    import random
    
    # Check if data already exists
    if db.query(Animal).count() > 0:
        return {"message": "Demo data already exists", "seeded": False}
    
    # Sample data
    species_breeds = {
        "cattle": ["Holstein", "Angus", "Hereford", "Jersey", "Brahman"],
        "goat": ["Boer", "Nubian", "Alpine", "Saanen"],
        "sheep": ["Merino", "Suffolk", "Dorper", "Texel"],
        "pig": ["Yorkshire", "Duroc", "Berkshire", "Hampshire"]
    }
    
    animals = []
    
    # Create 20 sample animals
    for i in range(20):
        species = random.choice(list(species_breeds.keys()))
        breed = random.choice(species_breeds[species])
        health_status = random.choices(
            ["healthy", "needs_attention", "critical", "unknown"],
            weights=[60, 20, 5, 15]
        )[0]
        
        animal = Animal(
            tag_id=f"{species.upper()[:2]}-{1000 + i}",
            name=f"{species.capitalize()} {i + 1}",
            species=species,
            breed=breed,
            age_months=random.randint(6, 72),
            gender=random.choice(["male", "female"]),
            weight_kg=random.uniform(50, 500),
            current_health_status=health_status,
            notes=f"Sample {species} for demo"
        )
        db.add(animal)
        animals.append(animal)
    
    db.commit()
    
    # Create health records
    for animal in animals:
        db.refresh(animal)
        
        # Create 1-3 health records per animal
        for _ in range(random.randint(1, 3)):
            record = HealthRecord(
                animal_id=animal.id,
                status=animal.current_health_status,
                confidence=random.uniform(0.7, 0.99),
                posture_score=random.uniform(0.5, 1.0),
                coat_condition_score=random.uniform(0.5, 1.0),
                mobility_score=random.uniform(0.5, 1.0),
                alertness_score=random.uniform(0.5, 1.0),
                analysis_type="demo",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            db.add(record)
    
    # Create attendance for last 7 days
    for animal in animals:
        for days_ago in range(7):
            if random.random() > 0.1:  # 90% attendance rate
                attendance = Attendance(
                    animal_id=animal.id,
                    date=date.today() - timedelta(days=days_ago),
                    detection_confidence=random.uniform(0.8, 0.99),
                    identification_method="demo"
                )
                db.add(attendance)
    
    # Create alerts for unhealthy animals
    for animal in animals:
        if animal.current_health_status == "critical":
            alert = Alert(
                animal_id=animal.id,
                alert_type="health_critical",
                severity="critical",
                title=f"Critical: {animal.tag_id}",
                message=f"Animal {animal.tag_id} requires immediate attention"
            )
            db.add(alert)
        elif animal.current_health_status == "needs_attention":
            alert = Alert(
                animal_id=animal.id,
                alert_type="health_attention",
                severity="medium",
                title=f"Attention: {animal.tag_id}",
                message=f"Animal {animal.tag_id} needs veterinary review"
            )
            db.add(alert)
    
    db.commit()
    
    return {
        "message": "Demo data seeded successfully",
        "seeded": True,
        "animals_created": len(animals)
    }
