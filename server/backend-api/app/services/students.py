from app.db.mongo import db
from bson import ObjectId
from datetime import datetime

students_col = db["students"]
users_col = db["users"]
attendance_col = db["attendance"]
subjects_col = db["subjects"]


async def get_student_profile(user_id: str):
    # 1. Get user document
    user = await users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    # 2. Get student document
    student = await students_col.find_one({"userId": ObjectId(user_id)})
    if not student:
        return None

    # 3. Get overall attendance summary (for backward compatibility)
    overall_attendance_summary = await build_attendance_summary(student["_id"])

    # 4. Populate subjects with per-subject attendance
    subject_ids = student.get("subjects", [])

    subjects = []
    if subject_ids:
        subject_cursor = subjects_col.find(
            {"_id": {"$in": subject_ids}}
        )
        
        async for sub in subject_cursor:
            # Calculate attendance for THIS specific subject
            subject_attendance = await build_attendance_summary(
                student["_id"], 
                sub["_id"]
            )
            
            subjects.append({
                "_id": str(sub["_id"]),
                "name": sub.get("name"),
                "code": sub.get("code"),
                "attendance": subject_attendance  # ✅ Per-subject stats
            })

    # 5. Build clean API-safe profile
    profile = {
        "id": str(student["_id"]),
        "userId": str(student["userId"]),
        "name": user.get("name"),
        "email": user.get("email"),
        "branch": student.get("branch"),
        "roll": student.get("roll"),
        "year": student.get("year"),
        "subjects": subjects,              # ✅ Now includes per-subject attendance
        "avatarUrl": student.get("avatarUrl"),
        "image_url": student.get("image_url"),
        "attendance": overall_attendance_summary,  # ✅ Overall stats still available
        "recent_attendance": overall_attendance_summary["recent_attendance"],
    }

    return profile


async def build_attendance_summary(student_doc_id: ObjectId, subject_id: ObjectId = None):
    """
    Returns attendance stats for a student.
    If subject_id is provided, filters by that subject.
    
    Returns:
    {
      total_classes,
      present,
      absent,
      percentage,
      forecasted_score,
      recent_attendance: [...]
    }
    """

    # Build query - always filter by student
    q = {"student_id": student_doc_id}
    
    # ✅ Filter by subject if provided
    if subject_id:
        q["subject_id"] = subject_id

    total_classes = await attendance_col.count_documents(q)
    present = await attendance_col.count_documents({**q, "present": True})
    absent = total_classes - present

    percentage = round((present / total_classes) * 100, 2) if total_classes else 0
    forecasted_score = 2 if percentage < 50 else 5

    # Last 5 attendance records (filtered by subject if specified)
    recent_cursor = (
        attendance_col.find(q)
        .sort("date", -1)
        .limit(5)
    )

    recent = []
    async for r in recent_cursor:
        recent.append({
            "id": str(r["_id"]),
            "date": r.get("date"),
            "period": r.get("period"),
            "present": r.get("present"),
            "class_id": str(r["class_id"]) if r.get("class_id") else None,
        })

    return {
        "total_classes": total_classes,
        "present": present,
        "absent": absent,
        "percentage": percentage,
        "forecasted_score": forecasted_score,
        "recent_attendance": recent,
    }