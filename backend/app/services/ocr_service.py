"""OCR Service for ear tag and QR code identification."""
import random
import string
import time
from typing import Dict, Any, Optional, Tuple


class OCRService:
    """
    Mock OCR service for reading ear tags and QR codes.
    In production, this would use Tesseract or similar OCR engine.
    """
    
    # Common ear tag formats
    TAG_FORMATS = [
        "{letters}{numbers}",           # AB1234
        "{letters}-{numbers}",          # AB-1234
        "{country}{numbers}",           # IN1234567
        "TAG-{numbers}",                # TAG-00123
        "{letters}{numbers}{letters}",  # AB123CD
    ]
    
    def __init__(self):
        """Initialize the OCR service."""
        self.confidence_threshold = 0.6
        self.engine = "tesseract-mock"
    
    def read_ear_tag(self, image_path: str, region: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Read ear tag from an image.
        
        Args:
            image_path: Path to the image
            region: Optional bounding box region to focus on
            
        Returns:
            OCR results with extracted text
        """
        start_time = time.time()
        
        # Simulate OCR processing time
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate OCR success/failure
        success_rate = 0.85
        success = random.random() < success_rate
        
        if success:
            # Generate a realistic tag ID
            tag_id = self._generate_tag_id()
            confidence = round(random.uniform(0.7, 0.98), 3)
            
            result = {
                "success": True,
                "text": tag_id,
                "confidence": confidence,
                "tag_type": "ear_tag",
                "bounding_box": region or self._generate_text_region(),
                "needs_manual_review": confidence < self.confidence_threshold
            }
        else:
            result = {
                "success": False,
                "text": None,
                "confidence": 0.0,
                "error": random.choice([
                    "Tag not visible in image",
                    "Image too blurry",
                    "Low contrast",
                    "Partial occlusion"
                ]),
                "needs_manual_review": True
            }
        
        processing_time = (time.time() - start_time) * 1000
        result["processing_time_ms"] = round(processing_time, 2)
        
        return result
    
    def read_qr_code(self, image_path: str) -> Dict[str, Any]:
        """
        Read QR code from an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            QR code reading results
        """
        start_time = time.time()
        time.sleep(random.uniform(0.05, 0.15))
        
        # QR codes have higher success rate when present
        success_rate = 0.9
        success = random.random() < success_rate
        
        if success:
            # Generate mock QR content
            qr_data = {
                "animal_id": f"ANIMAL-{random.randint(10000, 99999)}",
                "tag_id": self._generate_tag_id(),
                "farm_id": f"FARM-{random.randint(100, 999)}",
                "registration_date": "2024-01-15"
            }
            
            result = {
                "success": True,
                "qr_type": "livestock_id",
                "data": qr_data,
                "raw_text": str(qr_data),
                "confidence": round(random.uniform(0.9, 0.99), 3)
            }
        else:
            result = {
                "success": False,
                "qr_type": None,
                "data": None,
                "error": "No QR code detected in image"
            }
        
        processing_time = (time.time() - start_time) * 1000
        result["processing_time_ms"] = round(processing_time, 2)
        
        return result
    
    def identify_animal(self, image_path: str, use_ocr: bool = True, use_muzzle: bool = False) -> Dict[str, Any]:
        """
        Attempt to identify an animal using available methods.
        
        Args:
            image_path: Path to the image
            use_ocr: Whether to try OCR identification
            use_muzzle: Whether to try muzzle print matching
            
        Returns:
            Identification results
        """
        results = {
            "identified": False,
            "methods_tried": [],
            "best_match": None,
            "confidence": 0.0
        }
        
        # Try OCR first
        if use_ocr:
            results["methods_tried"].append("ocr")
            
            # Try ear tag
            ear_tag_result = self.read_ear_tag(image_path)
            if ear_tag_result["success"]:
                results["identified"] = True
                results["method"] = "ocr_ear_tag"
                results["tag_id"] = ear_tag_result["text"]
                results["confidence"] = ear_tag_result["confidence"]
                results["ocr_text"] = ear_tag_result["text"]
                results["needs_manual_review"] = ear_tag_result["needs_manual_review"]
                return results
            
            # Try QR code
            qr_result = self.read_qr_code(image_path)
            if qr_result["success"]:
                results["identified"] = True
                results["method"] = "ocr_qr_code"
                results["tag_id"] = qr_result["data"]["tag_id"]
                results["confidence"] = qr_result["confidence"]
                results["qr_data"] = qr_result["data"]
                results["needs_manual_review"] = False
                return results
        
        # Try muzzle recognition (stub)
        if use_muzzle:
            results["methods_tried"].append("muzzle_print")
            muzzle_result = self._mock_muzzle_recognition(image_path)
            if muzzle_result["matched"]:
                results["identified"] = True
                results["method"] = "muzzle_print"
                results["muzzle_hash"] = muzzle_result["hash"]
                results["confidence"] = muzzle_result["confidence"]
                results["animal_id"] = muzzle_result.get("animal_id")
                results["needs_manual_review"] = muzzle_result["confidence"] < 0.8
                return results
        
        # No identification possible
        results["needs_manual_review"] = True
        results["error"] = "Could not identify animal using available methods"
        return results
    
    def _generate_tag_id(self) -> str:
        """Generate a realistic ear tag ID."""
        format_type = random.choice([1, 2, 3, 4])
        
        if format_type == 1:
            return f"{''.join(random.choices(string.ascii_uppercase, k=2))}{random.randint(1000, 9999)}"
        elif format_type == 2:
            return f"{''.join(random.choices(string.ascii_uppercase, k=2))}-{random.randint(1000, 9999)}"
        elif format_type == 3:
            return f"IN{random.randint(1000000, 9999999)}"
        else:
            return f"TAG-{random.randint(10000, 99999)}"
    
    def _generate_text_region(self) -> Dict[str, float]:
        """Generate a mock text bounding box region."""
        x1 = round(random.uniform(0.1, 0.4), 4)
        y1 = round(random.uniform(0.1, 0.3), 4)
        return {
            "x1": x1,
            "y1": y1,
            "x2": round(x1 + random.uniform(0.1, 0.3), 4),
            "y2": round(y1 + random.uniform(0.05, 0.15), 4)
        }
    
    def _mock_muzzle_recognition(self, image_path: str) -> Dict[str, Any]:
        """
        Mock muzzle print recognition.
        In production, this would compare against stored muzzle prints.
        """
        time.sleep(random.uniform(0.2, 0.5))
        
        matched = random.random() < 0.7
        
        if matched:
            return {
                "matched": True,
                "hash": f"muzzle_{''.join(random.choices(string.hexdigits.lower(), k=32))}",
                "confidence": round(random.uniform(0.75, 0.95), 3),
                "animal_id": random.randint(1, 100)
            }
        else:
            return {
                "matched": False,
                "error": "No matching muzzle print found in database"
            }


# Singleton instance
ocr_service = OCRService()
