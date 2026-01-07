import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import router as face_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Attendance - ML Face Recognition Service",
        description="Local ML service for face detection and recognition",
        version="1.0.0"
    )

    # CORS - Allow backend API to communicate
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",      # Backend API (local)
            "http://127.0.0.1:8000",      # Backend API (local)
            "http://localhost:5173",      # Frontend (local dev)
            "*"                           # Allow all for local service
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(face_router)

    @app.get("/")
    async def root():
        return {
            "service": "ML Face Recognition Service",
            "status": "running",
            "version": "1.0.0",
            "endpoints": {
                "register_face": "POST /api/face/register-face",
                "register_face_base64": "POST /api/face/register-face-base64",
                "recognize_face": "POST /api/face/recognize-face",
                "health": "GET /api/face/health"
            }
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.ML_SERVICE_HOST,
        port=settings.ML_SERVICE_PORT,
        reload=True
    )
