"""
Smart Livestock AI - Camera Integration for Real-Time Monitoring

This script captures frames from cameras (IP cameras, webcams, or video files),
runs AI detection, identifies animals, marks attendance, and assesses health.

Usage:
    python camera_monitor.py --source webcam
    python camera_monitor.py --source rtsp://192.168.1.100:554/stream
    python camera_monitor.py --source video.mp4

Requirements:
    pip install opencv-python requests schedule pillow numpy
"""

import cv2
import time
import json
import logging
import argparse
import requests
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from queue import Queue
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('camera_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
CAPTURE_INTERVAL_SECONDS = 30  # Capture every 30 seconds
HEALTH_CHECK_INTERVAL_MINUTES = 5  # Health check every 5 minutes
SAVE_CAPTURES = True  # Save captured frames
CAPTURES_DIR = Path("captures")


@dataclass
class DetectedAnimal:
    """Represents a detected animal in a frame."""
    bounding_box: Dict[str, float]
    species: str
    confidence: float
    tag_id: Optional[str] = None
    animal_id: Optional[int] = None
    health_status: Optional[str] = None


@dataclass
class CameraConfig:
    """Camera configuration."""
    source: str  # Can be: webcam, rtsp URL, video file path
    name: str = "Camera 1"
    fps: int = 1  # Frames per second to process
    resize_width: int = 1280
    resize_height: int = 720


class APIClient:
    """Client for interacting with the Smart Livestock AI API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """Check if the API is available."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"API health check failed: {e}")
            return False
    
    def upload_and_analyze(self, image_path: str, animal_id: Optional[int] = None) -> Dict:
        """Upload an image and run AI analysis."""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (Path(image_path).name, f, 'image/jpeg')}
                data = {}
                if animal_id:
                    data['animal_id'] = str(animal_id)
                
                response = self.session.post(
                    f"{self.base_url}/api/upload/analyze-image",
                    files=files,
                    data=data,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Upload and analyze failed: {e}")
            return {}
    
    def mark_attendance(self, animal_id: int, confidence: float = 1.0) -> bool:
        """Mark attendance for an animal."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/attendance/mark",
                json={
                    "animal_id": animal_id,
                    "detection_confidence": confidence,
                    "identification_method": "camera_auto"
                },
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Mark attendance failed: {e}")
            return False
    
    def get_animals(self) -> List[Dict]:
        """Get all registered animals."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/animals?per_page=1000",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            logger.error(f"Get animals failed: {e}")
            return []
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/dashboard/stats",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get dashboard stats failed: {e}")
            return {}


class FrameProcessor:
    """Processes video frames for animal detection and analysis."""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.animals_cache: Dict[str, Dict] = {}  # tag_id -> animal data
        self.last_detection: Dict[int, datetime] = {}  # animal_id -> last seen
        self.frame_count = 0
        self._refresh_animals_cache()
    
    def _refresh_animals_cache(self):
        """Refresh the local cache of registered animals."""
        animals = self.api_client.get_animals()
        self.animals_cache = {a['tag_id']: a for a in animals}
        logger.info(f"Loaded {len(self.animals_cache)} animals into cache")
    
    def save_frame(self, frame: np.ndarray, prefix: str = "capture") -> str:
        """Save a frame to disk."""
        CAPTURES_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}_{self.frame_count}.jpg"
        filepath = CAPTURES_DIR / filename
        cv2.imwrite(str(filepath), frame)
        self.frame_count += 1
        return str(filepath)
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame:
        1. Save the frame
        2. Send to API for detection and analysis
        3. Mark attendance for detected animals
        4. Return results
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "detections": [],
            "attendance_marked": [],
            "health_assessments": [],
            "errors": []
        }
        
        try:
            # Save frame
            image_path = self.save_frame(frame, "monitoring")
            logger.info(f"Saved frame: {image_path}")
            
            # Send for analysis
            analysis = self.api_client.upload_and_analyze(image_path)
            
            if analysis:
                # Process detection results
                if 'detection' in analysis:
                    detection = analysis['detection']
                    result['detections'] = detection.get('detected_animals', [])
                    logger.info(f"Detected {len(result['detections'])} animal(s)")
                
                # Process identification
                if 'identification' in analysis:
                    identification = analysis['identification']
                    if identification.get('identified'):
                        animal_id = identification.get('animal_id')
                        tag_id = identification.get('tag_id')
                        confidence = identification.get('confidence', 0.8)
                        
                        # Mark attendance
                        if animal_id:
                            now = datetime.now()
                            last_seen = self.last_detection.get(animal_id)
                            
                            # Only mark attendance if not seen in last 5 minutes
                            if not last_seen or (now - last_seen) > timedelta(minutes=5):
                                if self.api_client.mark_attendance(animal_id, confidence):
                                    self.last_detection[animal_id] = now
                                    result['attendance_marked'].append({
                                        'animal_id': animal_id,
                                        'tag_id': tag_id,
                                        'confidence': confidence
                                    })
                                    logger.info(f"Marked attendance for {tag_id} (ID: {animal_id})")
                
                # Process health assessment
                if 'health' in analysis:
                    health = analysis['health']
                    result['health_assessments'].append({
                        'status': health.get('status'),
                        'confidence': health.get('confidence'),
                        'recommendations': health.get('recommendations', [])
                    })
                    
                    # Log warnings for unhealthy animals
                    if health.get('status') in ['needs_attention', 'critical']:
                        logger.warning(f"Health alert: {health.get('status')} detected!")
            
        except Exception as e:
            error_msg = f"Error processing frame: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
        
        return result


class CameraMonitor:
    """Main camera monitoring class."""
    
    def __init__(self, config: CameraConfig, api_client: APIClient):
        self.config = config
        self.api_client = api_client
        self.processor = FrameProcessor(api_client)
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        self.stats = {
            'frames_processed': 0,
            'animals_detected': 0,
            'attendance_marked': 0,
            'start_time': None
        }
    
    def _get_video_source(self) -> int | str:
        """Get the video source based on configuration."""
        if self.config.source.lower() == 'webcam':
            return 0  # Default webcam
        elif self.config.source.startswith('rtsp://'):
            return self.config.source  # RTSP stream
        elif self.config.source.isdigit():
            return int(self.config.source)  # Camera index
        else:
            return self.config.source  # File path
    
    def connect(self) -> bool:
        """Connect to the camera."""
        try:
            source = self._get_video_source()
            logger.info(f"Connecting to camera: {source}")
            
            self.cap = cv2.VideoCapture(source)
            
            if not self.cap.isOpened():
                logger.error("Failed to open camera")
                return False
            
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resize_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resize_height)
            
            logger.info(f"Connected to camera: {self.config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Camera connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the camera."""
        if self.cap:
            self.cap.release()
            self.cap = None
            logger.info("Disconnected from camera")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from the camera."""
        if not self.cap or not self.cap.isOpened():
            if not self.connect():
                return None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture frame")
            return None
        
        return frame
    
    def process_once(self):
        """Capture and process a single frame."""
        frame = self.capture_frame()
        if frame is None:
            return
        
        result = self.processor.process_frame(frame)
        
        # Update stats
        self.stats['frames_processed'] += 1
        self.stats['animals_detected'] += len(result.get('detections', []))
        self.stats['attendance_marked'] += len(result.get('attendance_marked', []))
        
        # Log summary
        logger.info(
            f"Frame processed - "
            f"Detected: {len(result.get('detections', []))}, "
            f"Attendance: {len(result.get('attendance_marked', []))}"
        )
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring."""
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"Starting camera monitoring (interval: {interval_seconds}s)")
        
        # Schedule periodic captures
        schedule.every(interval_seconds).seconds.do(self.process_once)
        
        # Process first frame immediately
        self.process_once()
        
        # Run scheduler
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False
        self.disconnect()
        schedule.clear()
        
        # Print final stats
        runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
        logger.info(f"""
        === Monitoring Stopped ===
        Runtime: {runtime}
        Frames Processed: {self.stats['frames_processed']}
        Animals Detected: {self.stats['animals_detected']}
        Attendance Marked: {self.stats['attendance_marked']}
        """)


class LiveViewMonitor(CameraMonitor):
    """Camera monitor with live view display."""
    
    def start_monitoring_with_display(self, interval_seconds: int = 30):
        """Start monitoring with live video display."""
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"Starting camera monitoring with live display")
        
        last_process_time = datetime.min
        
        while self.running:
            frame = self.capture_frame()
            if frame is None:
                time.sleep(1)
                continue
            
            # Process frame at specified interval
            now = datetime.now()
            if (now - last_process_time).total_seconds() >= interval_seconds:
                # Run processing in background
                threading.Thread(
                    target=self._process_frame_async, 
                    args=(frame.copy(),)
                ).start()
                last_process_time = now
            
            # Add overlay info
            self._draw_overlay(frame)
            
            # Display frame
            cv2.imshow(f"Smart Livestock AI - {self.config.name}", frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        self.stop_monitoring()
    
    def _process_frame_async(self, frame: np.ndarray):
        """Process frame in background thread."""
        result = self.processor.process_frame(frame)
        self.stats['frames_processed'] += 1
        self.stats['animals_detected'] += len(result.get('detections', []))
        self.stats['attendance_marked'] += len(result.get('attendance_marked', []))
    
    def _draw_overlay(self, frame: np.ndarray):
        """Draw status overlay on frame."""
        # Background for text
        cv2.rectangle(frame, (10, 10), (350, 100), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (350, 100), (45, 106, 79), 2)  # Green border
        
        # Title
        cv2.putText(frame, "Smart Livestock AI", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (45, 106, 79), 2)
        
        # Stats
        cv2.putText(frame, f"Frames: {self.stats['frames_processed']}", (20, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Detected: {self.stats['animals_detected']}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Attendance: {self.stats['attendance_marked']}", (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (frame.shape[1] - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Smart Livestock AI - Camera Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python camera_monitor.py --source webcam
  python camera_monitor.py --source 0      # First camera
  python camera_monitor.py --source rtsp://192.168.1.100:554/stream
  python camera_monitor.py --source video.mp4 --interval 5
  python camera_monitor.py --source webcam --live

The monitor will:
  1. Capture frames at the specified interval
  2. Send frames to the AI for animal detection
  3. Identify animals by ear tags or QR codes
  4. Automatically mark attendance
  5. Assess health and create alerts if needed
        """
    )
    
    parser.add_argument(
        '--source', 
        type=str, 
        default='webcam',
        help='Camera source: webcam, camera index (0,1,...), RTSP URL, or video file'
    )
    parser.add_argument(
        '--name',
        type=str,
        default='Barn Camera',
        help='Camera name for logging'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Seconds between captures (default: 30)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000',
        help='Backend API URL'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Show live video feed with overlay'
    )
    
    args = parser.parse_args()
    
    # Initialize
    api_client = APIClient(args.api_url)
    
    # Check API connection
    logger.info(f"Connecting to API: {args.api_url}")
    if not api_client.health_check():
        logger.error("Cannot connect to API. Make sure the backend is running.")
        logger.error(f"Start it with: python run.py")
        return 1
    
    logger.info("API connection successful")
    
    # Get current stats
    stats = api_client.get_dashboard_stats()
    if stats:
        logger.info(f"System has {stats.get('total_animals', 0)} animals registered")
    
    # Create camera config
    config = CameraConfig(
        source=args.source,
        name=args.name
    )
    
    # Create monitor
    if args.live:
        monitor = LiveViewMonitor(config, api_client)
    else:
        monitor = CameraMonitor(config, api_client)
    
    # Connect to camera
    if not monitor.connect():
        logger.error("Failed to connect to camera")
        return 1
    
    try:
        logger.info("=" * 50)
        logger.info("SMART LIVESTOCK AI - CAMERA MONITOR")
        logger.info("=" * 50)
        logger.info(f"Camera: {args.name}")
        logger.info(f"Source: {args.source}")
        logger.info(f"Interval: {args.interval} seconds")
        logger.info(f"API: {args.api_url}")
        logger.info("=" * 50)
        logger.info("Press Ctrl+C to stop" + (" or 'q' in the window" if args.live else ""))
        logger.info("=" * 50)
        
        if args.live:
            monitor.start_monitoring_with_display(args.interval)
        else:
            monitor.start_monitoring(args.interval)
            
    except KeyboardInterrupt:
        logger.info("\nStopping camera monitor...")
        monitor.stop_monitoring()
    
    return 0


if __name__ == "__main__":
    exit(main())
