import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO

from app.core.config import settings


def detect_faces_and_embeddings(image_bytes: bytes):
    """
    Detect all faces in image and return their embeddings.
    
    Returns:
        List of face dictionaries with 'box' and 'embedding'
    """
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    
    h, w, _ = image_np.shape
    image_area = h * w

    locations = face_recognition.face_locations(
        image_np,
        number_of_times_to_upsample=1,
        model="hog"   # CPU-friendly, works in Docker
    )
    
    if not locations:
        return []

    encodings = face_recognition.face_encodings(
        image_np, 
        locations,
        num_jitters=settings.NUM_JITTERS,
        model="small" 
    )

    faces = []
    
    for (top, right, bottom, left), enc in zip(locations, encodings):
        face_area = (bottom - top) * (right - left)
        if face_area / image_area < settings.MIN_FACE_AREA_RATIO:
            continue
        
        faces.append({
            "box": (top, right, bottom, left),
            "embedding": enc.tolist()
        })
    
    return faces
