from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional
import base64

from app.utils.face_encode import get_face_embedding
from app.utils.face_detect import detect_faces_and_embeddings
from app.utils.match_utils import match_embedding
from app.storage.embeddings import embeddings_storage
from app.core.config import settings


router = APIRouter(prefix="/api/face", tags=["Face Recognition"])


class RegisterFaceRequest(BaseModel):
    student_id: str
    image_base64: Optional[str] = None  # Base64 encoded image


class RegisterFaceResponse(BaseModel):
    success: bool
    message: str
    student_id: str


class RecognizeFaceRequest(BaseModel):
    image_base64: str  # Base64 encoded image
    student_ids: Optional[List[str]] = None  # Limit search to these students


class FaceMatch(BaseModel):
    student_id: str
    confidence: float
    distance: float
    status: str  # "present", "uncertain", "unknown"
    box: Dict[str, int]


class RecognizeFaceResponse(BaseModel):
    faces: List[FaceMatch]
    count: int


@router.post("/register-face", response_model=RegisterFaceResponse)
async def register_face(file: UploadFile = File(...), student_id: str = None):
    """
    Register a face for a student.
    Extracts face embedding and stores it locally.
    
    Args:
        file: Image file containing student's face
        student_id: Student identifier
    
    Returns:
        Success status and message
    """
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id is required")
    
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG allowed")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Extract face embedding
    try:
        embedding = get_face_embedding(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Store embedding locally
    embeddings_storage.save_embedding(student_id, embedding)
    
    return RegisterFaceResponse(
        success=True,
        message="Face registered successfully",
        student_id=student_id
    )


@router.post("/register-face-base64", response_model=RegisterFaceResponse)
async def register_face_base64(request: RegisterFaceRequest):
    """
    Register a face for a student using base64 encoded image.
    
    Args:
        request: Contains student_id and base64 encoded image
    
    Returns:
        Success status and message
    """
    if not request.image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required")
    
    # Strip base64 header if present
    image_b64 = request.image_base64
    if "," in image_b64:
        _, image_b64 = image_b64.split(",", 1)
    
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")
    
    # Extract face embedding
    try:
        embedding = get_face_embedding(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Store embedding locally
    embeddings_storage.save_embedding(request.student_id, embedding)
    
    return RegisterFaceResponse(
        success=True,
        message="Face registered successfully",
        student_id=request.student_id
    )


@router.post("/recognize-face", response_model=RecognizeFaceResponse)
async def recognize_face(request: RecognizeFaceRequest):
    """
    Recognize faces in an image.
    
    Args:
        request: Contains base64 encoded image and optional student_ids filter
    
    Returns:
        List of recognized faces with match information
    """
    # Decode base64 image
    image_b64 = request.image_base64
    if "," in image_b64:
        _, image_b64 = image_b64.split(",", 1)
    
    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")
    
    # Detect faces and get embeddings
    faces = detect_faces_and_embeddings(image_bytes)
    
    if not faces:
        return RecognizeFaceResponse(faces=[], count=0)
    
    # Load stored embeddings
    if request.student_ids:
        # Only load specific students
        all_student_embeddings = {
            sid: embeddings_storage.get_embeddings(sid)
            for sid in request.student_ids
        }
        # Filter out None values
        all_student_embeddings = {k: v for k, v in all_student_embeddings.items() if v}
    else:
        # Load all students
        all_student_embeddings = embeddings_storage.get_all_student_embeddings()
    
    results = []
    
    for face in faces:
        best_match_id = None
        best_distance = 1e9
        
        # Match against all students
        for student_id, known_embeddings in all_student_embeddings.items():
            distance = match_embedding(face["embedding"], known_embeddings)
            if distance is not None and distance < best_distance:
                best_distance = distance
                best_match_id = student_id
        
        # Determine status based on distance
        if best_distance < settings.CONFIDENCE_THRESHOLD:
            status = "present"
        elif best_distance < settings.UNCERTAIN_THRESHOLD:
            status = "uncertain"
        else:
            status = "unknown"
            best_match_id = None
        
        # Calculate confidence (inverse of distance)
        confidence = max(0.0, 1.0 - best_distance) if best_match_id else 0.0
        
        results.append(FaceMatch(
            student_id=best_match_id if best_match_id else "",
            confidence=round(confidence, 3),
            distance=round(best_distance, 4) if best_match_id else 0.0,
            status=status,
            box={
                "top": face["box"][0],
                "right": face["box"][1],
                "bottom": face["box"][2],
                "left": face["box"][3]
            }
        ))
    
    return RecognizeFaceResponse(faces=results, count=len(results))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ml-face-recognition"}


@router.delete("/embeddings/{student_id}")
async def delete_student_embeddings(student_id: str):
    """Delete all embeddings for a student."""
    deleted = embeddings_storage.delete_embeddings(student_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Student embeddings not found")
    
    return {"success": True, "message": f"Embeddings deleted for student {student_id}"}
