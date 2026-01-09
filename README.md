# 🐄 Smart Livestock AI

An AI-powered livestock health monitoring and animal identification system for farmers and veterinarians, optimized for rural environments.

## 🚀 Features

- **Image & Video Upload**: Upload livestock images/videos with format validation
- **Animal Detection (AI)**: YOLOv8-based detection with bounding boxes
- **Animal Identification**: OCR for ear tags/QR codes + optional muzzle recognition
- **Health Assessment**: CNN-based classification (Healthy/Needs Attention/Critical)
- **Attendance Tracking**: Automatic daily attendance per animal
- **Dashboard**: Real-time analytics and alerts
- **Alert System**: Notifications for unhealthy animals
- **Offline-Ready**: Designed for rural environments with poor connectivity

## 🏗️ Tech Stack

### Frontend
- Next.js 14 (TypeScript)
- Tailwind CSS
- Mobile-first responsive design

### Backend
- FastAPI (Python 3.10+)
- SQLAlchemy ORM
- PostgreSQL

### AI/ML
- YOLOv8 for animal detection
- CNN for health classification
- Tesseract OCR for tag reading

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Start server
python run.py
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:3000

## 📹 Camera Integration (Real-Time Monitoring)

### Option 1: Demo Simulator (No Hardware)
```bash
cd backend
python demo_simulator.py --interval 10
```

### Option 2: Webcam
```bash
cd backend
pip install opencv-python schedule
python camera_monitor.py --source webcam --live
```

### Option 3: IP Camera (RTSP)
```bash
python camera_monitor.py --source rtsp://192.168.1.100:554/stream --interval 30
```

### Option 4: Video File
```bash
python camera_monitor.py --source barn_footage.mp4 --interval 5
```

The camera monitor will:
- Capture frames at specified intervals
- Detect animals using AI
- Identify them by ear tags/QR codes
- Mark attendance automatically
- Assess health and create alerts

## 📡 API Endpoints

### Animals
- `GET /api/animals` - List all animals
- `POST /api/animals` - Create new animal
- `GET /api/animals/{id}` - Get animal details
- `PUT /api/animals/{id}` - Update animal
- `DELETE /api/animals/{id}` - Delete animal

### Health
- `POST /api/health/assess` - Assess health from image
- `GET /api/health/records/{animal_id}` - Get health history
- `POST /api/health/records` - Create health record

### Upload
- `POST /api/upload/image` - Upload image for analysis
- `POST /api/upload/video` - Upload video for analysis

### Detection
- `POST /api/detect/animals` - Detect animals in image
- `POST /api/detect/identify` - Identify animal via OCR/muzzle

### Attendance
- `GET /api/attendance/today` - Today's attendance
- `GET /api/attendance/animal/{id}` - Animal attendance history
- `POST /api/attendance/mark` - Mark attendance

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/alerts` - Recent alerts

## 🧪 Sample API Calls

### Upload and Analyze Image
```bash
curl -X POST "http://localhost:8000/api/upload/image" \
  -F "file=@cow.jpg"
```

### Get Dashboard Stats
```bash
curl "http://localhost:8000/api/dashboard/stats"
```

### Register New Animal
```bash
curl -X POST "http://localhost:8000/api/animals" \
  -H "Content-Type: application/json" \
  -d '{"tag_id": "COW-001", "species": "cattle", "breed": "Holstein"}'
```

## 📊 Database Schema

### Animals Table
- id, tag_id, species, breed, age, gender, created_at, updated_at

### Health Records Table
- id, animal_id, status, confidence, notes, image_path, created_at

### Attendance Table
- id, animal_id, date, detected_at, confidence

### Alerts Table
- id, animal_id, alert_type, severity, message, resolved, created_at

## 🎯 Hackathon Demo

This project is hackathon-ready with:
- Mock AI models that simulate realistic inference
- Sample data generation
- Beautiful, responsive UI
- Real-time updates

## 📄 License

MIT License - Feel free to use for your projects!

## 👥 Contributors

Built with ❤️ for the farming community
