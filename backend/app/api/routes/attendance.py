from fastapi import APIRouter, HTTPException
from typing import Dict, List
import base64
from bson import ObjectId
from datetime import date


from app.db.mongo import db
from app.utils.face_detect import detect_faces_and_embeddings
from app.utils.match_utils import match_embedding

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

# distance thresholds
CONFIDENT_TH = 0.60
UNCERTAIN_TH = 0.75


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
    
    # load subject
    subject = await db.subjects.find_one(
        {"_id": ObjectId(subject_id)},
        {"students": 1}
    )
    
    if not subject:
        raise HTTPException(404, "Subject not found")
    
    student_user_ids = [
        s["student_id"]
        for s in subject["students"]
        if s.get("verified", False)
    ]

    if not image_b64 or not subject_id:
        raise HTTPException(status_code=400, detail="image and subject_id required")

    # strip base64 header
    if "," in image_b64:
        _, image_b64 = image_b64.split(",", 1)

    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image")

    # detect faces
    faces = detect_faces_and_embeddings(image_bytes)

    if not faces:
        return {"faces": [], "count": 0}

    # load students of this subject with embeddings
    students_cursor = db.students.find({
        "userId": {"$in": student_user_ids},
        "verified": True,
        "face_embeddings": {"$exists": True, "$ne": []}
    })

    students = await students_cursor.to_list(length=500)

    results = []
    
    print("Faces detected:", len(faces))

    for face in faces:
        best_match = None
        best_distance = 1e9


        for student in students:
            d = match_embedding(face["embedding"], student["face_embeddings"])
            if d is not None and d < best_distance:
                best_distance = d
                best_match = student
                
        print(
            "MATCH:",
            best_match["name"] if best_match else "NONE",
            "distance:",
            best_distance
        )

        # decide status
        if best_match and best_distance < UNCERTAIN_TH:
            status = "present"
        else:
            status = "unknown"
            best_match = None
            
        user = None
        if best_match:
            user = await db.users.find_one(
                {"_id": best_match["userId"]},
                {"name": 1, "roll": 1}
            )


        results.append({
            "box": {
                "top": face["box"][0],
                "right": face["box"][1],
                "bottom": face["box"][2],
                "left": face["box"][3]
            },
            "status": status, 
            "distance": None if not best_match else round(best_distance, 4),
            "confidence": None if not best_match else round(
                max(0.0, 1.0 - best_distance), 3
            ),
            "student": None if not best_match else {
                "id": str(best_match["userId"]),
                "roll": user.get("roll") if user else None,
                "name": best_match["name"]
            }
        })

    # print("Image size:", len(image_bytes))
    # print("Detected face locations:", faces)
    
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