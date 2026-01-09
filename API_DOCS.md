# Smart Livestock AI - API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 🏠 Root
```bash
# Get API info
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health
```

---

### 🐄 Animals

#### List all animals
```bash
curl "http://localhost:8000/api/animals?page=1&per_page=20"
```

#### Get single animal
```bash
curl "http://localhost:8000/api/animals/1"
```

#### Create animal
```bash
curl -X POST "http://localhost:8000/api/animals" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_id": "COW-001",
    "name": "Bessie",
    "species": "cattle",
    "breed": "Holstein",
    "age_months": 24,
    "gender": "female",
    "weight_kg": 450
  }'
```

#### Update animal
```bash
curl -X PUT "http://localhost:8000/api/animals/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bessie Updated",
    "weight_kg": 460
  }'
```

#### Delete animal
```bash
curl -X DELETE "http://localhost:8000/api/animals/1"
```

---

### 💓 Health

#### Assess health from image
```bash
curl -X POST "http://localhost:8000/api/health/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "uploads/images/cow.jpg",
    "animal_id": 1
  }'
```

#### Get health records for animal
```bash
curl "http://localhost:8000/api/health/records/1"
```

#### Get health summary
```bash
curl "http://localhost:8000/api/health/summary"
```

---

### 📅 Attendance

#### Get today's attendance
```bash
curl "http://localhost:8000/api/attendance/today"
```

#### Mark attendance
```bash
curl -X POST "http://localhost:8000/api/attendance/mark" \
  -H "Content-Type: application/json" \
  -d '{
    "animal_id": 1,
    "detection_confidence": 0.95,
    "identification_method": "manual"
  }'
```

#### Get attendance stats
```bash
curl "http://localhost:8000/api/attendance/stats?days=7"
```

#### Get missing animals
```bash
curl "http://localhost:8000/api/attendance/missing?days=1"
```

---

### 📤 Upload

#### Upload image
```bash
curl -X POST "http://localhost:8000/api/upload/image" \
  -F "file=@cow.jpg"
```

#### Upload and analyze
```bash
curl -X POST "http://localhost:8000/api/upload/analyze-image" \
  -F "file=@cow.jpg" \
  -F "animal_id=1"
```

---

### 🔍 Detection

#### Detect animals in image
```bash
curl -X POST "http://localhost:8000/api/detect/animals" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "uploads/images/cow.jpg"
  }'
```

#### Identify animal
```bash
curl -X POST "http://localhost:8000/api/detect/identify" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "uploads/images/cow.jpg",
    "use_ocr": true,
    "use_muzzle": false
  }'
```

---

### 📊 Dashboard

#### Get dashboard stats
```bash
curl "http://localhost:8000/api/dashboard/stats"
```

#### Get quick stats
```bash
curl "http://localhost:8000/api/dashboard/quick-stats"
```

#### Get alerts
```bash
curl "http://localhost:8000/api/dashboard/alerts?resolved=false&limit=20"
```

#### Resolve alert
```bash
curl -X PUT "http://localhost:8000/api/dashboard/alerts/1/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution_notes": "Animal treated and healthy"
  }'
```

#### Seed demo data
```bash
curl -X POST "http://localhost:8000/api/dashboard/seed-demo-data"
```

#### Get health trends
```bash
curl "http://localhost:8000/api/dashboard/trends/health?days=7"
```

#### Get attendance trends
```bash
curl "http://localhost:8000/api/dashboard/trends/attendance?days=7"
```

---

## Response Examples

### Animal Response
```json
{
  "id": 1,
  "tag_id": "COW-001",
  "name": "Bessie",
  "species": "cattle",
  "breed": "Holstein",
  "age_months": 24,
  "gender": "female",
  "weight_kg": 450,
  "current_health_status": "healthy",
  "last_health_check": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Health Assessment Response
```json
{
  "status": "healthy",
  "confidence": 0.92,
  "posture_score": 0.88,
  "coat_condition_score": 0.95,
  "mobility_score": 0.90,
  "alertness_score": 0.87,
  "findings": {
    "overall_score": 0.90,
    "detected_symptoms": ["good_posture", "shiny_coat"]
  },
  "recommendations": [
    "Continue regular health monitoring",
    "Maintain current care routine"
  ]
}
```

### Detection Response
```json
{
  "image_path": "uploads/images/cow.jpg",
  "detected_animals": [
    {
      "bounding_box": {
        "x1": 0.1,
        "y1": 0.2,
        "x2": 0.8,
        "y2": 0.9
      },
      "species": "cattle",
      "confidence": 0.95
    }
  ],
  "total_detected": 1,
  "processing_time_ms": 45.5
}
```
