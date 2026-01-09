"""Attendance Service for tracking animal presence."""
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..models.animal import Animal
from ..models.attendance import Attendance


class AttendanceService:
    """Service for managing animal attendance records."""
    
    def __init__(self, db: Session):
        """Initialize attendance service with database session."""
        self.db = db
    
    def mark_attendance(
        self,
        animal_id: int,
        confidence: float = 1.0,
        method: str = "automatic",
        location_zone: Optional[str] = None,
        image_path: Optional[str] = None
    ) -> Attendance:
        """
        Mark attendance for an animal.
        
        Args:
            animal_id: ID of the animal
            confidence: Detection confidence score
            method: Identification method used
            location_zone: Optional location zone
            image_path: Optional reference image
            
        Returns:
            Created attendance record
        """
        today = date.today()
        
        # Check if attendance already marked today
        existing = self.db.query(Attendance).filter(
            and_(
                Attendance.animal_id == animal_id,
                Attendance.date == today
            )
        ).first()
        
        if existing:
            # Update existing record with higher confidence if applicable
            if confidence > existing.detection_confidence:
                existing.detection_confidence = confidence
                existing.detected_at = datetime.utcnow()
                if image_path:
                    existing.image_path = image_path
                self.db.commit()
            return existing
        
        # Create new attendance record
        attendance = Attendance(
            animal_id=animal_id,
            date=today,
            detected_at=datetime.utcnow(),
            detection_confidence=confidence,
            identification_method=method,
            location_zone=location_zone,
            image_path=image_path
        )
        
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        
        return attendance
    
    def get_today_attendance(self) -> Dict[str, Any]:
        """Get attendance summary for today."""
        today = date.today()
        
        total_animals = self.db.query(Animal).count()
        
        attendance_records = self.db.query(Attendance).filter(
            Attendance.date == today
        ).all()
        
        detected_count = len(attendance_records)
        
        # Get animals not detected today
        detected_ids = [a.animal_id for a in attendance_records]
        missing_animals = self.db.query(Animal).filter(
            ~Animal.id.in_(detected_ids) if detected_ids else True
        ).all()
        
        return {
            "date": today.isoformat(),
            "total_animals": total_animals,
            "detected_count": detected_count,
            "missing_count": total_animals - detected_count,
            "attendance_rate": round(detected_count / total_animals * 100, 2) if total_animals > 0 else 0,
            "attendance_records": attendance_records,
            "missing_animals": missing_animals
        }
    
    def get_animal_attendance_history(
        self,
        animal_id: int,
        days: int = 30
    ) -> List[Attendance]:
        """
        Get attendance history for a specific animal.
        
        Args:
            animal_id: ID of the animal
            days: Number of days to look back
            
        Returns:
            List of attendance records
        """
        start_date = date.today() - timedelta(days=days)
        
        return self.db.query(Attendance).filter(
            and_(
                Attendance.animal_id == animal_id,
                Attendance.date >= start_date
            )
        ).order_by(Attendance.date.desc()).all()
    
    def get_attendance_by_date(self, target_date: date) -> Dict[str, Any]:
        """Get attendance for a specific date."""
        total_animals = self.db.query(Animal).count()
        
        attendance_records = self.db.query(Attendance).filter(
            Attendance.date == target_date
        ).all()
        
        detected_count = len(attendance_records)
        
        return {
            "date": target_date.isoformat(),
            "total_animals": total_animals,
            "detected_count": detected_count,
            "attendance_rate": round(detected_count / total_animals * 100, 2) if total_animals > 0 else 0,
            "records": attendance_records
        }
    
    def get_attendance_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get attendance statistics for the past N days."""
        daily_stats = []
        
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            stats = self.get_attendance_by_date(target_date)
            daily_stats.append({
                "date": stats["date"],
                "detected": stats["detected_count"],
                "total": stats["total_animals"],
                "rate": stats["attendance_rate"]
            })
        
        # Calculate averages
        avg_rate = sum(s["rate"] for s in daily_stats) / len(daily_stats) if daily_stats else 0
        
        return {
            "period_days": days,
            "daily_stats": daily_stats,
            "average_attendance_rate": round(avg_rate, 2)
        }
    
    def auto_mark_from_detection(
        self,
        detections: List[Dict[str, Any]],
        image_path: Optional[str] = None
    ) -> List[Attendance]:
        """
        Automatically mark attendance from detection results.
        
        Args:
            detections: List of detection results with animal IDs
            image_path: Source image path
            
        Returns:
            List of created/updated attendance records
        """
        records = []
        
        for detection in detections:
            if detection.get("animal_id"):
                record = self.mark_attendance(
                    animal_id=detection["animal_id"],
                    confidence=detection.get("confidence", 0.5),
                    method="automatic",
                    image_path=image_path
                )
                records.append(record)
        
        return records
