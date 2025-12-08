from fastapi import APIRouter
from typing import Dict
from io import BytesIO
from PIL import Image
import base64

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/mark")
async def mark_attendance(payload: Dict):
    """
    Expecting JSON with {"image": "data:image/jpeg;base64,...."}
    We'll decode the image and (later) run face recognition / detection.
    """
    image_b64 = payload.get("image", "")
    if not image_b64:
        return {"error": "no image"}

    # strip header if present
    if "," in image_b64:
        _, image_b64 = image_b64.split(",", 1)

    try:
        img_bytes = base64.b64decode(image_b64)
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        # TODO: implement real face recognition here
        # img.save("last_capture.jpg")  # example
    except Exception as e:
        return {"error": str(e)}

    # TEMP stub (same as your old code)
    detected = [
        {"roll": "2101", "name": "Ravi Kumar"},
        {"roll": "2122", "name": "Mira Singh"},
    ]

    return {"ok": True, "detected": detected, "count": len(detected)}
