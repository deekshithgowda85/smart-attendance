from fastapi import APIRouter, HTTPException
from typing import Dict, List
import base64
from bson import ObjectId
from datetime import date


from app.db.mongo import db
from app.services.ml_service_client import ml_service_client

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

# distance thresholds
CONFIDENT_TH = 0.50
UNCERTAIN_TH = 0.60


@router.post("/mark")
async def mark_attendance(payload: Dict):
    """
    payload:
    {
      "image": "data:image/jpeg;base64,...",
      "subject_id": "..."
    }
    """

    image_b64 = payload.get("image")
    subject_id = payload.get("subject_id")
    
    if not image_b64 or not subject_id:
        raise HTTPException(status_code=400, detail="image and subject_id required")
    
    # Load subject
    subject = await db.subjects.find_one(
        {"_id": ObjectId(subject_id)},
        {"students": 1}
    )
    
    if not subject:
        raise HTTPException(404, "Subject not found")
    
    # Get verified student IDs for this subject
    student_user_ids = [
        str(s["student_id"])  # Convert ObjectId to string for ML service
        for s in subject["students"]
        if s.get("verified", False)
    ]
    
    if not student_user_ids:
        return {"faces": [], "count": 0}

    # Call ML service to recognize faces
    try:
        ml_response = await ml_service_client.recognize_faces(
            image_base64=image_b64,
            student_ids=student_user_ids
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"ML Service unavailable: {str(e)}")
    
    faces = ml_response.get("faces", [])
    
    if not faces:
        return {"faces": [], "count": 0}
    
    # Enrich results with student details from database
    results = []
    
    print("Faces detected:", len(faces))

    for face in faces:
        student_id = face.get("student_id")
        status = face.get("status")
        
        # Fetch student details if matched
        user = None
        student = None
        if student_id and status != "unknown":
            student = await db.students.find_one(
                {"userId": ObjectId(student_id)},
                {"userId": 1, "name": 1}
            )
            if student:
                user = await db.users.find_one(
                    {"_id": ObjectId(student_id)},
                    {"name": 1, "roll": 1}
                )
        
        print(
            "MATCH:",
            user.get("name") if user else "NONE",
            "distance:",
            face.get("distance", 0)
        )

        results.append({
            "box": face.get("box", {}),
            "status": status,
            "distance": face.get("distance"),
            "confidence": face.get("confidence"),
            "student": None if not user else {
                "id": student_id,
                "roll": user.get("roll") if user else None,
                "name": user.get("name", "Unknown")
            }
        })

    return {
        "faces": results,
        "count": len(results)
    }


@router.post("/confirm")
async def confirm_attendance(payload: Dict):
    subject_id = payload.get("subject_id")
    present_students: List[str] = payload.get("present_students", [])
    absent_students: List[str] = payload.get("absent_students", [])
    
    print("absent students ",absent_students)
    
    if not subject_id:
        raise HTTPException(status_code=400, detail="subject_id required")
    
    today = date.today().isoformat()
    subject_oid = ObjectId(subject_id)
    present_oids = [ObjectId(sid) for sid in present_students]
    absent_oids = [ObjectId(sid) for sid in absent_students]
    
   # ✅ Mark PRESENT students
    await db.subjects.update_one(
        {"_id": subject_oid},
        {
            "$inc": {"students.$[p].attendance.present": 1},
            "$set": {"students.$[p].attendance.lastMarkedAt": today}
        },
        array_filters=[
            {
                "p.student_id": {"$in": present_oids},
                "p.attendance.lastMarkedAt": {"$ne": today}
            }
        ]
    )
    
   # ✅ Mark ABSENT students
    await db.subjects.update_one(
        {"_id": subject_oid},
        {
            "$inc": {"students.$[a].attendance.absent": 1},
            "$set": {"students.$[a].attendance.lastMarkedAt": today}
        },
        array_filters=[
            {
                "a.student_id": {"$in": absent_oids},
                "a.attendance.lastMarkedAt": {"$ne": today}
            }
        ]
    )

    return {
        "ok": True,
        "present_updated": len(present_students),
        "absent_updated": len(absent_students)
    }