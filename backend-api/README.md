# Backend API - Smart Attendance System

This is the **deployable** backend API service. It handles authentication, student management, attendance records, and reports without any ML dependencies.

## ⚠️ Important

- **This service is deployable** to platforms like Render, Railway, or any VPS
- **Does NOT contain ML/OpenCV dependencies**
- Communicates with the local ML service via HTTP for face operations
- Can run independently without ML service (face recognition disabled)

## 🚀 Setup

### 1. Install Dependencies

```bash
cd backend-api
pip install -r requirements.txt
```

No heavy ML dependencies - installs quickly!

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=smart_attendance

# ML Service (optional - for face recognition)
ML_SERVICE_URL=http://localhost:8001

# JWT & Session
JWT_SECRET=your-secret-key
SESSION_SECRET_KEY=your-session-key

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. Run the Server

```bash
# From backend-api directory
python -m app.main

# Or using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API server will start on `http://localhost:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /auth/google/login` - Google OAuth login
- `GET /auth/google/callback` - Google OAuth callback

### Students
- `GET /students/me/profile` - Get student profile
- `POST /students/me/face-image` - Upload face image (calls ML service)
- `GET /students/me/available-subjects` - Get available subjects
- `POST /students/me/subjects` - Add subject to student
- `DELETE /students/me/remove-subject/{id}` - Remove subject

### Attendance
- `POST /api/attendance/mark` - Mark attendance (calls ML service)
- `POST /api/attendance/confirm` - Confirm attendance

### Teacher Settings
- See `/docs` for full API documentation

## 🔧 Architecture

### Without ML Service (Deployable Mode)
```
Frontend → Backend API → MongoDB
                ↓
           Cloudinary (images)
```

Face recognition features are disabled if ML service is unavailable.

### With ML Service (Full Mode)
```
Frontend → Backend API → MongoDB
              ↓            ↓
         ML Service    Cloudinary
              ↓
    Local Embeddings Storage
```

Face recognition fully functional.

## 📁 Structure

```
backend-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── students.py      # Uses ML service client
│   │       ├── attendance.py    # Uses ML service client
│   │       └── ...
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── ...
│   ├── db/
│   │   ├── mongo.py
│   │   └── ...
│   ├── services/
│   │   ├── ml_service_client.py  # NEW: ML service HTTP client
│   │   ├── students.py
│   │   ├── attendance.py
│   │   └── ...
│   └── main.py
├── requirements.txt              # NO ML dependencies
├── .env.example
└── README.md
```

## 🔗 ML Service Integration

The backend communicates with ML service via HTTP:

### Face Registration Flow
1. Student uploads face image → Backend API
2. Backend forwards image → ML Service
3. ML Service extracts embedding and stores locally
4. Backend stores image URL in MongoDB
5. Backend returns success to frontend

### Face Recognition Flow
1. Frontend sends photo → Backend API
2. Backend forwards photo + student IDs → ML Service
3. ML Service detects faces and matches
4. ML Service returns matched student IDs
5. Backend enriches with student details from DB
6. Backend returns results to frontend

### Error Handling
- If ML service is down: Face features gracefully disabled
- Backend logs warnings but continues to function
- Auth, student management, reports still work

## 🚀 Deployment

### Deploy to Render / Railway

1. **Create `render.yaml` or configure via dashboard**
2. **Set environment variables** (from `.env.example`)
3. **No ML service URL** - deploy without face recognition
4. **MongoDB**: Use MongoDB Atlas or hosted instance

### Environment Variables for Production

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net
ML_SERVICE_URL=  # Leave empty if no ML service
JWT_SECRET=<strong-random-secret>
SESSION_SECRET_KEY=<strong-random-secret>
GOOGLE_CLIENT_ID=<your-production-id>
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/google/callback
```

### Deploy without ML Service

The backend will work without ML service - face recognition features will be disabled:
- Students can still register (without face)
- Attendance can be marked manually
- All other features work normally

## ⚠️ Key Differences from Original Backend

### Removed
- ❌ `face_encode.py` - moved to ML service
- ❌ `face_detect.py` - moved to ML service
- ❌ `match_utils.py` - moved to ML service
- ❌ ML dependencies (opencv, face_recognition, numpy)

### Added
- ✅ `ml_service_client.py` - HTTP client for ML service
- ✅ `ML_SERVICE_URL` environment variable
- ✅ Error handling for ML service unavailability

### Modified
- 🔄 `students.py` - calls ML service instead of local encoding
- 🔄 `attendance.py` - calls ML service instead of local detection
- 🔄 Database schema - no `face_embeddings` field (stored in ML service)

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Test without ML service
ML_SERVICE_URL="" python -m app.main

# Test with ML service
# (Start ML service first on port 8001)
python -m app.main
```

## 📊 Performance

- Fast startup (<5 seconds)
- Low memory usage (~100MB)
- No GPU required
- Easily scales horizontally
- ML operations delegated to separate service

## 🔒 Security

- No ML libraries reduces attack surface
- Stateless API design
- JWT authentication
- CORS protection
- Input validation with Pydantic
- Secure password hashing

## ❓ FAQ

**Q: Can I deploy this without the ML service?**
A: Yes! Face recognition will be disabled, but all other features work.

**Q: How do I enable face recognition in production?**
A: Deploy ML service on a local server and set `ML_SERVICE_URL` to point to it.

**Q: What if ML service goes down?**
A: Backend continues working. Face operations return errors but don't crash.

**Q: Can ML service be deployed to cloud?**
A: Not recommended. It requires local camera access and has heavy dependencies.
