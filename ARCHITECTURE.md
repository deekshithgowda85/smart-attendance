# Architecture Overview - Smart Attendance System

## 🏗️ New Modular Architecture

The Smart Attendance System has been refactored into **two independent services**:

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                     (React + Vite)                           │
│                   http://localhost:5173                      │
└───────────────┬─────────────────────────┬───────────────────┘
                │                         │
                │ HTTP                    │ HTTP
                ▼                         ▼
┌───────────────────────────┐   ┌──────────────────────────────┐
│    BACKEND API            │   │   ML FACE SERVICE            │
│    (Deployable)           │◄──┤   (Local Only)               │
│  http://localhost:8000    │   │  http://localhost:8001       │
│                           │   │                              │
│  ✅ Authentication        │   │  🤖 Face Detection           │
│  ✅ Student CRUD          │   │  🤖 Face Embeddings          │
│  ✅ Attendance Records    │   │  🤖 Face Matching            │
│  ✅ Reports               │   │  💾 Local Storage            │
│  ✅ Dashboard             │   │                              │
│  ❌ NO ML Dependencies    │   │  ✅ OpenCV, dlib             │
│                           │   │  ✅ face_recognition         │
└─────────┬─────────────────┘   └──────────────────────────────┘
          │
          ▼
    ┌──────────┐
    │ MongoDB  │
    │ Database │
    └──────────┘
```

## 📂 Directory Structure

```
smart-attendance/
├── backend-api/              ✅ DEPLOYABLE Backend
│   ├── app/
│   │   ├── api/routes/       # REST API endpoints
│   │   ├── services/         
│   │   │   └── ml_service_client.py  # ⭐ ML service HTTP client
│   │   ├── core/             # Config, security
│   │   └── db/               # Database layer
│   ├── requirements.txt      # NO ML dependencies
│   └── README.md
│
├── ml-face-service/          ❌ LOCAL ONLY ML Service
│   ├── app/
│   │   ├── api/routes.py     # Face recognition endpoints
│   │   ├── utils/            # Face detection, encoding, matching
│   │   ├── storage/          # Local embeddings storage
│   │   └── core/             # Config
│   ├── storage/
│   │   └── embeddings/       # JSON files with face data
│   ├── requirements.txt      # ML dependencies (opencv, dlib, etc.)
│   └── README.md
│
├── backend/                  ⚠️ DEPRECATED (old monolithic version)
├── frontend/                 # React frontend
└── README.md                 # Main documentation
```

## 🔄 Communication Flow

### 1. Face Registration
```
Student → Frontend → Backend API → ML Service
                         ↓              ↓
                    Cloudinary    Local Storage
                     (image)      (embeddings)
```

1. Student uploads photo via frontend
2. Frontend sends to Backend API
3. Backend API forwards to ML Service
4. ML Service extracts face embedding
5. ML Service stores embedding locally (JSON file)
6. Backend API uploads image to Cloudinary
7. Backend API marks student as verified in MongoDB

### 2. Attendance Marking
```
Camera → Frontend → Backend API → ML Service
                         ↓              ↓
                     MongoDB      Match Faces
                   (students)    (embeddings)
```

1. Frontend captures photo from camera
2. Frontend sends to Backend API with subject_id
3. Backend API gets student IDs from MongoDB
4. Backend API calls ML Service with photo + student IDs
5. ML Service detects faces and matches against stored embeddings
6. ML Service returns matched student IDs with confidence
7. Backend API enriches with student details from DB
8. Backend API returns results to frontend
9. Frontend displays matches, teacher confirms
10. Backend API updates attendance in MongoDB

## 🎯 Service Responsibilities

### Backend API (Deployable)

**Handles:**
- ✅ User authentication (JWT, OAuth)
- ✅ Student management (CRUD)
- ✅ Subject/class management
- ✅ Attendance record storage
- ✅ Reports and analytics
- ✅ Email notifications
- ✅ Image upload (Cloudinary)
- ✅ Database operations (MongoDB)

**Does NOT Handle:**
- ❌ Face detection
- ❌ Face encoding
- ❌ Face matching
- ❌ Camera access
- ❌ ML operations

**Dependencies:**
- FastAPI
- MongoDB (pymongo/motor)
- Cloudinary
- httpx (for ML service communication)
- NO OpenCV, NO face_recognition

**Deployment:**
- ✅ Can deploy to Render, Railway, Heroku, VPS
- ✅ Works without ML service (face features disabled)
- ✅ Fast startup, low memory
- ✅ No system dependencies

### ML Face Service (Local Only)

**Handles:**
- ✅ Face detection in images
- ✅ Face embedding extraction
- ✅ Face matching
- ✅ Embeddings storage (local files)

**Does NOT Handle:**
- ❌ Authentication
- ❌ Database operations
- ❌ Business logic
- ❌ Image storage (only processes)

**Dependencies:**
- FastAPI
- OpenCV
- dlib
- face_recognition
- numpy

**Deployment:**
- ❌ NOT meant for cloud deployment
- ✅ Runs on local machine only
- ✅ Requires camera access
- ✅ Heavy system dependencies

## 🚀 Getting Started

### Quick Start (Both Services)

```bash
# Terminal 1: Start ML Service
cd ml-face-service
pip install -r requirements.txt
cp .env.example .env
python -m app.main
# Runs on http://localhost:8001

# Terminal 2: Start Backend API
cd backend-api
pip install -r requirements.txt
cp .env.example .env
# Edit .env: ML_SERVICE_URL=http://localhost:8001
python -m app.main
# Runs on http://localhost:8000

# Terminal 3: Start Frontend
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

### Backend API Only (Without Face Recognition)

```bash
cd backend-api
pip install -r requirements.txt
cp .env.example .env
# Leave ML_SERVICE_URL empty or remove it
python -m app.main
```

Face recognition features will be gracefully disabled.

## 🔧 Configuration

### Backend API (.env)
```env
MONGO_URI=mongodb://localhost:27017
ML_SERVICE_URL=http://localhost:8001  # Optional
JWT_SECRET=your-secret
GOOGLE_CLIENT_ID=...
CLOUDINARY_CLOUD_NAME=...
```

### ML Service (.env)
```env
ML_SERVICE_PORT=8001
CONFIDENCE_THRESHOLD=0.50
EMBEDDINGS_STORAGE_PATH=./storage/embeddings
```

## 📡 API Contracts

### ML Service → Backend API

#### Register Face
**Request:**
```http
POST http://localhost:8001/api/face/register-face
Content-Type: multipart/form-data

file: <image>
student_id: "user_object_id"
```

**Response:**
```json
{
  "success": true,
  "message": "Face registered successfully",
  "student_id": "user_object_id"
}
```

#### Recognize Faces
**Request:**
```http
POST http://localhost:8001/api/face/recognize-face
Content-Type: application/json

{
  "image_base64": "data:image/jpeg;base64,...",
  "student_ids": ["id1", "id2", ...]
}
```

**Response:**
```json
{
  "faces": [
    {
      "student_id": "id1",
      "confidence": 0.95,
      "distance": 0.42,
      "status": "present",
      "box": {"top": 100, "right": 300, "bottom": 400, "left": 100}
    }
  ],
  "count": 1
}
```

## 🎯 Benefits of This Architecture

### ✅ Clean Separation
- Backend API focuses on business logic
- ML Service focuses on computer vision
- Each service has clear responsibilities

### ✅ Deployability
- Backend API can deploy anywhere (no ML dependencies)
- ML Service stays local with heavy dependencies
- Reduces deployment complexity and cost

### ✅ Scalability
- Backend API can scale horizontally
- ML Service can be optimized separately
- Independent resource allocation

### ✅ Maintainability
- Changes to ML don't affect backend
- Backend updates don't require ML rebuild
- Clear interfaces between services

### ✅ Flexibility
- Backend works without ML (manual attendance)
- Can swap ML service with different implementation
- Easy to add more ML features

## 🔒 Security Considerations

### Backend API
- JWT authentication for all endpoints
- CORS protection
- Input validation
- Rate limiting (recommended)

### ML Service
- Should run on localhost only
- No authentication (trusted local network)
- CORS allows local origins only
- Not exposed to internet

## 📊 Performance

### Backend API
- Startup: <5 seconds
- Memory: ~100MB
- Response time: <100ms (without ML)
- CPU: Minimal

### ML Service
- Startup: ~10 seconds
- Memory: ~500MB
- Face detection: 0.5-2s per image
- Face matching: ~0.1s for 100 students
- CPU intensive

## 🆚 Old vs New

### Old (Monolithic)
```
Backend API
├── Auth ✅
├── Students ✅
├── Attendance ✅
├── Face Detection 🔴 (ML)
├── Face Encoding 🔴 (ML)
└── Face Matching 🔴 (ML)

Problems:
❌ Can't deploy (ML dependencies)
❌ Slow startup
❌ High memory usage
❌ Tight coupling
```

### New (Microservices)
```
Backend API             ML Service
├── Auth ✅             ├── Face Detection ✅
├── Students ✅         ├── Face Encoding ✅
├── Attendance ✅       └── Face Matching ✅
└── Reports ✅

Benefits:
✅ Deployable
✅ Fast startup
✅ Low memory
✅ Loose coupling
```

## 🛠️ Development Workflow

### Adding New ML Feature
1. Add endpoint to ML Service
2. Add client method to `ml_service_client.py`
3. Call from Backend API route
4. Update frontend

### Adding New Business Feature
1. Add route to Backend API
2. Update database if needed
3. Update frontend
4. No ML service changes

## 📝 Migration Notes

### From Old Backend
- ✅ All routes preserved
- ✅ Authentication unchanged
- ✅ Database schema compatible (minus face_embeddings)
- ✅ API responses same format
- ⚠️ Face embeddings moved from DB to ML service local storage

### Database Changes
**Old:** Students had `face_embeddings` array in MongoDB
**New:** Students have `verified` boolean, embeddings stored in ML service

No migration needed - can run both systems in parallel.

## 🐛 Troubleshooting

### ML Service Not Responding
- Check if ML service is running: `http://localhost:8001/api/face/health`
- Check `ML_SERVICE_URL` in backend .env
- Backend will continue working without face features

### Face Registration Fails
- Ensure ML service is running
- Check image quality (good lighting, clear face)
- Check logs: `tail -f ml-face-service/app.log`

### Attendance Marking Fails
- Verify students have registered faces
- Ensure ML service has embeddings for those students
- Check `ml-face-service/storage/embeddings/` directory

## 📚 Additional Resources

- [Backend API Documentation](./backend-api/README.md)
- [ML Service Documentation](./ml-face-service/README.md)
- [Frontend Documentation](./frontend/README.md)
- [Main README](./README.md)

## 🤝 Contributing

When contributing:
- Backend API changes → `backend-api/`
- ML changes → `ml-face-service/`
- Keep services independent
- Update both READMEs if needed

## 📄 License

MIT License - See LICENSE file
