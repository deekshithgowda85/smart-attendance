import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO

from app.core.config import settings


def get_face_embedding(image_bytes: bytes):
    """
    Extract face embedding from image bytes.
    
    Returns:
        embedding (list of 128 floats)
    
    Raises:
        ValueError if:
            - no face
            - multiple faces
            - face too small
    """
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)

    h, w, _ = image_np.shape
    image_area = h * w

    # Upsample helps HOG on small/medium images
    locations = face_recognition.face_locations(
        image_np,
        number_of_times_to_upsample=1,
        model="hog"
    )

    if len(locations) == 0:
        raise ValueError("No face detected")

    if len(locations) > 1:
        raise ValueError("Multiple faces detected")

    top, right, bottom, left = locations[0]
    face_area = (bottom - top) * (right - left)

    if face_area / image_area < settings.MIN_FACE_AREA_RATIO:
        raise ValueError("Face too small — move closer to camera")

    encoding = face_recognition.face_encodings(
        image_np,
        known_face_locations=locations,
        num_jitters=settings.NUM_JITTERS,
        model="small"   # faster; accuracy mainly comes from jitters
    )[0]

    return encoding.tolist()
