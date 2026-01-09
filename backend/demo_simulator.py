"""
Smart Livestock AI - Demo Camera Simulator

This script simulates camera input by:
1. Generating mock animal detections
2. Randomly marking attendance
3. Creating health assessments

Use this for testing and demonstration when real cameras are not available.

Usage:
    python demo_simulator.py
    python demo_simulator.py --interval 10 --duration 60
"""

import time
import random
import requests
import argparse
import logging
from datetime import datetime
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


class DemoSimulator:
    """Simulates camera detections for demo purposes."""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.session = requests.Session()
        self.animals: List[Dict] = []
    
    def check_api(self) -> bool:
        """Check if API is available."""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def load_animals(self) -> bool:
        """Load registered animals from API."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/animals?per_page=100",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            self.animals = data.get('items', [])
            logger.info(f"Loaded {len(self.animals)} animals")
            return True
        except Exception as e:
            logger.error(f"Failed to load animals: {e}")
            return False
    
    def simulate_detection(self, animal: Dict) -> Dict:
        """Simulate detecting an animal."""
        return {
            'animal_id': animal['id'],
            'tag_id': animal['tag_id'],
            'species': animal['species'],
            'confidence': random.uniform(0.85, 0.99)
        }
    
    def mark_attendance(self, animal_id: int, confidence: float) -> bool:
        """Mark attendance for an animal."""
        try:
            response = self.session.post(
                f"{self.api_url}/api/attendance/mark",
                json={
                    "animal_id": animal_id,
                    "detection_confidence": confidence,
                    "identification_method": "camera_simulation"
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to mark attendance: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get current dashboard stats."""
        try:
            response = self.session.get(
                f"{self.api_url}/api/dashboard/stats",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except:
            return {}
    
    def run_simulation_cycle(self):
        """Run one simulation cycle."""
        if not self.animals:
            return
        
        # Randomly select some animals to "detect"
        num_detections = random.randint(1, min(5, len(self.animals)))
        detected = random.sample(self.animals, num_detections)
        
        print("\n" + "=" * 60)
        print(f"📸 CAMERA CAPTURE - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        for animal in detected:
            detection = self.simulate_detection(animal)
            
            # Mark attendance
            if self.mark_attendance(detection['animal_id'], detection['confidence']):
                status_emoji = "🐄" if animal['species'] == 'cattle' else "🐐" if animal['species'] == 'goat' else "🐑"
                print(f"  {status_emoji} Detected: {detection['tag_id']}")
                print(f"     Species: {detection['species']}")
                print(f"     Confidence: {detection['confidence']:.1%}")
                print(f"     ✅ Attendance marked")
            else:
                print(f"  ⚠️ {detection['tag_id']} - Already marked today")
        
        # Show current stats
        stats = self.get_stats()
        if stats:
            print("\n📊 Current Stats:")
            print(f"   Total Animals: {stats.get('total_animals', 0)}")
            print(f"   Today's Attendance: {stats.get('todays_attendance', 0)}/{stats.get('total_animals', 0)}")
            print(f"   Attendance Rate: {stats.get('attendance_rate', 0)}%")


def main():
    parser = argparse.ArgumentParser(
        description='Demo Camera Simulator for Smart Livestock AI'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Seconds between simulated captures (default: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=0,
        help='Total duration in seconds, 0 = run forever (default: 0)'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000',
        help='Backend API URL'
    )
    
    args = parser.parse_args()
    
    simulator = DemoSimulator(args.api_url)
    
    # Check API
    print("\n🔌 Connecting to API...")
    if not simulator.check_api():
        print("❌ Cannot connect to API!")
        print(f"   Make sure the backend is running at {args.api_url}")
        print("   Start it with: cd backend && python run.py")
        return 1
    print("✅ API connected!")
    
    # Load animals
    print("\n🐄 Loading registered animals...")
    if not simulator.load_animals():
        print("❌ Failed to load animals!")
        return 1
    
    if len(simulator.animals) == 0:
        print("⚠️ No animals registered!")
        print("   First, seed demo data: POST /api/dashboard/seed-demo-data")
        return 1
    
    print(f"✅ Loaded {len(simulator.animals)} animals")
    
    # Run simulation
    print("\n" + "=" * 60)
    print("🎬 STARTING CAMERA SIMULATION")
    print("=" * 60)
    print(f"   Interval: Every {args.interval} seconds")
    print(f"   Duration: {'Forever' if args.duration == 0 else f'{args.duration} seconds'}")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        while True:
            simulator.run_simulation_cycle()
            
            # Check duration
            if args.duration > 0:
                elapsed = time.time() - start_time
                if elapsed >= args.duration:
                    print(f"\n⏱️ Duration reached ({args.duration}s). Stopping.")
                    break
            
            # Wait
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation stopped by user")
    
    # Final stats
    stats = simulator.get_stats()
    if stats:
        print("\n" + "=" * 60)
        print("📊 FINAL STATISTICS")
        print("=" * 60)
        print(f"   Total Animals: {stats.get('total_animals', 0)}")
        print(f"   Healthy: {stats.get('health_distribution', {}).get('healthy', 0)}")
        print(f"   Needs Attention: {stats.get('health_distribution', {}).get('needs_attention', 0)}")
        print(f"   Today's Attendance: {stats.get('todays_attendance', 0)}")
        print(f"   Attendance Rate: {stats.get('attendance_rate', 0)}%")
        print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
