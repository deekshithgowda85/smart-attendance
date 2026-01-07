# ML Face Recognition Service

This is the **local-only** ML service for face detection and recognition. It handles all ML operations using OpenCV and face_recognition library.

## ⚠️ Important Notes

- **This service is NOT meant to be deployed**
- Runs only on local machine with camera access
- Contains heavy dependencies (OpenCV, dlib, face_recognition)
- Provides minimal HTTP API for face operations

## 🚀 Setup

### 1. Install Dependencies

```bash
cd ml-face-service
pip install -r requirements.txt
```

**Note**: Installing `face-recognition` may take several minutes as it compiles dlib from source.

**Requirements:**
- CMake
- Build tools (gcc/g++)

**For Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
```

**For macOS:**
```bash
brew install cmake
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults should work for local development).

### 3. Run the Service

```bash
# From ml-face-service directory
python -m app.main

# Or using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

The ML service will start on `http://localhost:8001`

## 📡 API Endpoints

### Register Face (File Upload)
```http
POST /api/face/register-face
Content-Type: multipart/form-data

file: <image file>
student_id: "user_object_id"
```

### Register Face (Base64)
```http
POST /api/face/register-face-base64
Content-Type: application/json

{
  "student_id": "user_object_id",
  "image_base64": "data:image/jpeg;base64,..."
}
```

### Recognize Faces
```http
POST /api/face/recognize-face
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,...",
  "student_ids": ["id1", "id2"]  // optional filter
}
```

**Response:**
```json
{
  "faces": [
    {
      "student_id": "user_id",
      "confidence": 0.95,
      "distance": 0.42,
      "status": "present",
      "box": {"top": 100, "right": 300, "bottom": 400, "left": 100}
    }
  ],
  "count": 1
}
```

### Health Check
```http
GET /api/face/health
```

### Delete Student Embeddings
```http
DELETE /api/face/embeddings/{student_id}
```

## 💾 Storage

Face embeddings are stored locally in `./storage/embeddings/` as JSON files:
- One file per student: `{student_id}.json`
- Contains array of 128-dimensional embeddings
- Multiple embeddings per student allowed (different angles/lighting)

## 🔧 Configuration

Edit `.env` file:

```env
# Server
ML_SERVICE_HOST=0.0.0.0
ML_SERVICE_PORT=8001

# Face Recognition
MIN_FACE_AREA_RATIO=0.05     # Minimum face size (5% of image)
NUM_JITTERS=5                # Embedding quality (higher = better but slower)
CONFIDENCE_THRESHOLD=0.50    # Distance threshold for "present"
UNCERTAIN_THRESHOLD=0.60     # Distance threshold for "uncertain"

# Storage
EMBEDDINGS_STORAGE_PATH=./storage/embeddings
```

## 🏗️ Architecture

```
ml-face-service/
├── app/
│   ├── api/
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── utils/
│   │   ├── face_encode.py     # Single face embedding extraction
│   │   ├── face_detect.py     # Multi-face detection
│   │   └── match_utils.py     # Face matching logic
│   ├── storage/
│   │   └── embeddings.py      # Local storage manager
│   └── main.py                # Application entry point
├── storage/
│   └── embeddings/            # JSON files with embeddings
├── requirements.txt           # ML dependencies
├── .env.example
└── README.md
```

## 🔗 Communication with Backend API

The backend API communicates with this service via HTTP:

1. **Face Registration**: Backend sends image to ML service, ML service returns embedding
2. **Face Recognition**: Backend sends image and student IDs, ML service returns matches

See backend API documentation for integration details.

## ⚠️ Troubleshooting

### dlib installation fails
- Ensure CMake is installed
- Install build tools (gcc, g++, make)
- Try: `pip install dlib` separately first

### "No face detected" error
- Ensure good lighting
- Face should be clearly visible
- Face should cover at least 5% of image

### Low recognition accuracy
- Register multiple images per student (different angles)
- Ensure good image quality
- Adjust thresholds in `.env`

## 📊 Performance

- Face detection: ~0.5-2s per image (CPU)
- Face matching: ~0.1s for 100 students
- Scales well for small-medium deployments (<500 students)

For larger deployments (>500 students), consider:
- Using GPU acceleration
- Implementing database instead of file storage
- Caching frequently accessed embeddings
