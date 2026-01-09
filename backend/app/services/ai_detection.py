"""
Real AI Detection Service using YOLOv8.

This service uses the Ultralytics YOLOv8 model for actual animal detection.
If the model fails to load, it falls back to mock detection for demo purposes.
"""

import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import YOLOv8
YOLO_AVAILABLE = False
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    logger.info("YOLOv8 (ultralytics) loaded successfully")
except ImportError:
    logger.warning("ultralytics not installed. Using mock detection. Install with: pip install ultralytics")

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL not installed. Some features may be limited.")


class AIDetectionService:
    """
    YOLOv8-based animal detection service.
    
    Supports:
    - Pre-trained COCO model (detects: cow, horse, sheep, dog, cat, bird)
    - Custom fine-tuned livestock model (if available)
    
    Falls back to mock detection if models are unavailable.
    """
    
    # Map COCO classes to our livestock categories
    COCO_TO_LIVESTOCK = {
        'cow': 'cattle',
        'horse': 'horse', 
        'sheep': 'sheep',
        'dog': 'other',  # Could be farm dog
        'cat': 'other',
        'bird': 'poultry',
        'elephant': 'other',  # For demo/testing
    }
    
    # Classes we care about from COCO (class IDs)
    LIVESTOCK_COCO_IDS = [16, 17, 18, 19, 20, 21]  # bird, cat, dog, horse, sheep, cow
    
    ANIMAL_CLASSES = ["cattle", "goat", "sheep", "pig", "horse", "poultry"]
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the detection service.
        
        Args:
            model_path: Path to custom model weights. If None, uses pre-trained YOLOv8.
        """
        self.model = None
        self.model_loaded = False
        self.model_name = "mock"
        self.confidence_threshold = 0.5
        self.use_mock = True
        
        if YOLO_AVAILABLE:
            try:
                # Try custom model first, then fall back to pre-trained
                if model_path and Path(model_path).exists():
                    self.model = YOLO(model_path)
                    self.model_name = f"custom-{Path(model_path).stem}"
                    logger.info(f"Loaded custom model: {model_path}")
                else:
                    # Use pre-trained YOLOv8 nano (fastest, good for demo)
                    self.model = YOLO('yolov8n.pt')
                    self.model_name = "yolov8n-coco"
                    logger.info("Loaded pre-trained YOLOv8 nano model")
                
                self.model_loaded = True
                self.use_mock = False
                
            except Exception as e:
                logger.error(f"Failed to load YOLO model: {e}")
                logger.info("Falling back to mock detection")
                self.use_mock = True
        else:
            logger.info("YOLOv8 not available, using mock detection")
    
    def detect_animals(self, image_path: str) -> Dict[str, Any]:
        """
        Detect animals in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Detection results with bounding boxes and classifications
        """
        start_time = time.time()
        
        if self.use_mock:
            return self._mock_detect(image_path, start_time)
        
        try:
            # Run YOLO inference
            results = self.model(image_path, conf=self.confidence_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                    
                for i, box in enumerate(boxes):
                    # Get class name
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    
                    # Map to livestock category
                    if cls_name in self.COCO_TO_LIVESTOCK:
                        species = self.COCO_TO_LIVESTOCK[cls_name]
                    elif cls_name in self.ANIMAL_CLASSES:
                        species = cls_name
                    else:
                        continue  # Skip non-animal detections
                    
                    # Get bounding box (normalized coordinates)
                    bbox = box.xyxyn[0].tolist()  # [x1, y1, x2, y2] normalized
                    confidence = float(box.conf[0])
                    
                    detection = {
                        "bounding_box": {
                            "x1": round(bbox[0], 4),
                            "y1": round(bbox[1], 4),
                            "x2": round(bbox[2], 4),
                            "y2": round(bbox[3], 4)
                        },
                        "species": species,
                        "confidence": round(confidence, 4),
                        "original_class": cls_name,
                        "detection_id": f"det_{i}_{int(time.time() * 1000)}"
                    }
                    detections.append(detection)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                "image_path": image_path,
                "detected_animals": detections,
                "total_detected": len(detections),
                "processing_time_ms": round(processing_time, 2),
                "model_version": self.model_name,
                "using_real_ai": True
            }
            
        except Exception as e:
            logger.error(f"YOLO detection failed: {e}")
            return self._mock_detect(image_path, start_time)
    
    def detect_single_animal(self, image_path: str, species_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect a single animal with higher confidence.
        
        Args:
            image_path: Path to the image
            species_hint: Optional hint about expected species
            
        Returns:
            Single animal detection result
        """
        start_time = time.time()
        
        if self.use_mock:
            return self._mock_detect_single(image_path, species_hint, start_time)
        
        try:
            results = self.model(image_path, conf=0.3, verbose=False)
            
            best_detection = None
            best_confidence = 0
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    # Check if it's an animal we care about
                    if cls_name in self.COCO_TO_LIVESTOCK or cls_name in self.ANIMAL_CLASSES:
                        if confidence > best_confidence:
                            species = self.COCO_TO_LIVESTOCK.get(cls_name, cls_name)
                            bbox = box.xyxyn[0].tolist()
                            
                            best_detection = {
                                "bounding_box": {
                                    "x1": round(bbox[0], 4),
                                    "y1": round(bbox[1], 4),
                                    "x2": round(bbox[2], 4),
                                    "y2": round(bbox[3], 4)
                                },
                                "species": species,
                                "confidence": round(confidence, 4),
                            }
                            best_confidence = confidence
            
            processing_time = (time.time() - start_time) * 1000
            
            if best_detection:
                return {
                    "image_path": image_path,
                    "detection": best_detection,
                    "processing_time_ms": round(processing_time, 2),
                    "using_real_ai": True
                }
            else:
                # No detection found, return mock
                return self._mock_detect_single(image_path, species_hint, start_time)
                
        except Exception as e:
            logger.error(f"Single detection failed: {e}")
            return self._mock_detect_single(image_path, species_hint, start_time)
    
    def _mock_detect(self, image_path: str, start_time: float) -> Dict[str, Any]:
        """Fallback mock detection."""
        import random
        time.sleep(random.uniform(0.05, 0.2))
        
        num_detections = random.randint(1, 5)
        detections = []
        
        for i in range(num_detections):
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
            "model_version": "mock",
            "using_real_ai": False
        }
    
    def _mock_detect_single(self, image_path: str, species_hint: Optional[str], start_time: float) -> Dict[str, Any]:
        """Fallback mock single detection."""
        import random
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
            "processing_time_ms": round(processing_time, 2),
            "using_real_ai": False
        }
    
    def analyze_video_frame(self, frame_data: bytes, frame_number: int) -> Dict[str, Any]:
        """Analyze a video frame (mock for now)."""
        import random
        
        num_detections = random.randint(0, 3)
        detections = []
        
        for i in range(num_detections):
            detections.append({
                "species": random.choice(self.ANIMAL_CLASSES),
                "confidence": round(random.uniform(0.6, 0.95), 4),
                "tracking_id": f"track_{random.randint(1, 10)}"
            })
        
        return {
            "frame_number": frame_number,
            "detections": detections,
            "total_detected": len(detections)
        }


# Singleton instance
detection_service = AIDetectionService()
