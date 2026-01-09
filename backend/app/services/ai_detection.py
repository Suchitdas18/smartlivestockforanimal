"""AI Detection Service - Mock YOLOv8 implementation."""
import random
import time
from typing import List, Dict, Any, Optional


class AIDetectionService:
    """
    Mock YOLOv8 animal detection service.
    In production, this would load actual YOLOv8 weights and run inference.
    """
    
    # Simulated animal classes that could be detected
    ANIMAL_CLASSES = ["cattle", "goat", "sheep", "pig", "horse", "poultry"]
    
    def __init__(self):
        """Initialize the detection service."""
        self.model_loaded = True
        self.model_name = "yolov8n-livestock"  # Hypothetical fine-tuned model
        self.confidence_threshold = 0.5
    
    def detect_animals(self, image_path: str) -> Dict[str, Any]:
        """
        Detect animals in an image using mock YOLOv8.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detection results with bounding boxes and classifications
        """
        start_time = time.time()
        
        # Simulate processing delay (50-200ms for realistic demo)
        time.sleep(random.uniform(0.05, 0.2))
        
        # Generate mock detections (1-5 animals per image)
        num_detections = random.randint(1, 5)
        detections = []
        
        for i in range(num_detections):
            # Generate random bounding box (normalized coordinates)
            x1 = random.uniform(0.05, 0.6)
            y1 = random.uniform(0.05, 0.6)
            width = random.uniform(0.15, 0.35)
            height = random.uniform(0.2, 0.4)
            
            detection = {
                "bounding_box": {
                    "x1": round(x1, 4),
                    "y1": round(y1, 4),
                    "x2": round(min(x1 + width, 0.95), 4),
                    "y2": round(min(y1 + height, 0.95), 4)
                },
                "species": random.choice(self.ANIMAL_CLASSES),
                "confidence": round(random.uniform(0.65, 0.98), 4),
                "detection_id": f"det_{i}_{int(time.time() * 1000)}"
            }
            detections.append(detection)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "image_path": image_path,
            "detected_animals": detections,
            "total_detected": len(detections),
            "processing_time_ms": round(processing_time, 2),
            "model_version": self.model_name
        }
    
    def detect_single_animal(self, image_path: str, species_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect a single animal with higher confidence (for identification flow).
        
        Args:
            image_path: Path to the image
            species_hint: Optional hint about expected species
            
        Returns:
            Single animal detection result
        """
        start_time = time.time()
        time.sleep(random.uniform(0.03, 0.1))
        
        species = species_hint if species_hint in self.ANIMAL_CLASSES else random.choice(self.ANIMAL_CLASSES)
        
        detection = {
            "bounding_box": {
                "x1": round(random.uniform(0.1, 0.3), 4),
                "y1": round(random.uniform(0.1, 0.2), 4),
                "x2": round(random.uniform(0.7, 0.9), 4),
                "y2": round(random.uniform(0.8, 0.95), 4)
            },
            "species": species,
            "confidence": round(random.uniform(0.85, 0.99), 4),
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "image_path": image_path,
            "detection": detection,
            "processing_time_ms": round(processing_time, 2)
        }
    
    def analyze_video_frame(self, frame_data: bytes, frame_number: int) -> Dict[str, Any]:
        """
        Analyze a single video frame for animal detection.
        
        Args:
            frame_data: Raw frame bytes
            frame_number: Frame index in video
            
        Returns:
            Frame analysis results
        """
        num_detections = random.randint(0, 3)
        detections = []
        
        for i in range(num_detections):
            detections.append({
                "species": random.choice(self.ANIMAL_CLASSES),
                "confidence": round(random.uniform(0.6, 0.95), 4),
                "tracking_id": f"track_{random.randint(1, 10)}"  # For multi-frame tracking
            })
        
        return {
            "frame_number": frame_number,
            "detections": detections,
            "total_detected": len(detections)
        }


# Singleton instance
detection_service = AIDetectionService()
