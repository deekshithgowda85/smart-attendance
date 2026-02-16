# backend/app/api/routes/schedule.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import os
import pytz
from bson import ObjectId

from app.api.deps import get_current_user
from app.db.mongo import db
from app.schemas.schedule import ScheduleEntry

router = APIRouter(prefix="/schedule", tags=["schedule"])


# Response Models
class ClassPeriod(BaseModel):
    id: Optional[str] = None
    day: Optional[str] = None
    subject: Optional[str] = None
    grade: Optional[str] = None
    room: Optional[str] = None
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"
    slot: int
    attendance_status: Optional[str] = None  # "completed", "pending", None


class TodayScheduleResponse(BaseModel):
    classes: List[ClassPeriod]
    current_day: str


class CreateScheduleRequest(ScheduleEntry):
    pass


@router.get("/", response_model=List[ClassPeriod])
async def get_full_schedule(current_user: dict = Depends(get_current_user)):
    """
    Get full schedule for the authenticated user.
    """
    user_id = current_user["_id"]
    role = current_user.get("role")
    
    query = {}

    if role == "teacher":
        teacher = await db.teachers.find_one({"user_id": user_id})
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        query["teacher_id"] = teacher["_id"]

    elif role == "student":
        student = await db.students.find_one({"user_id": user_id})
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        if student.get("branch"):
            query["branch"] = student["branch"]
        if student.get("semester"):
            query["semester"] = student["semester"]
            
        if not student.get("branch"):
             return []

    else:
        raise HTTPException(status_code=403, detail="Role not authorized")

    schedules = await db.schedules.find(query).to_list(length=1000)

    classes = []
    for s in schedules:
        subject_name = "Unknown Subject"
        if s.get("subject_id"):
            subject = await db.subjects.find_one({"_id": s["subject_id"]})
            if subject:
                subject_name = subject.get("name", "Unknown")

        classes.append(
            ClassPeriod(
                id=str(s.get("_id")),
                day=s.get("day", ""),
                subject=subject_name,
                grade=str(s.get("semester")) if s.get("semester") else None,
                room=s.get("room_number"),
                start_time=s.get("start_time"),
                end_time=s.get("end_time"),
                slot=s.get("slot", 0),
            )
        )
    
    return classes


@router.get("/today", response_model=TodayScheduleResponse)
async def get_today_schedule(current_user: dict = Depends(get_current_user)):
    """
    Get today's schedule for the authenticated user (Student or Teacher).
    Fetches from the dedicated 'schedules' collection.
    """
    user_id = current_user["_id"]
    role = current_user.get("role")

    # Timezone setup
    timezone_str = os.getenv("SCHOOL_TIMEZONE", "Asia/Kolkata")
    try:
        school_tz = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        school_tz = pytz.timezone("Asia/Kolkata")

    now_in_school_tz = datetime.now(school_tz)
    days_of_week = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    current_day = days_of_week[now_in_school_tz.weekday()]

    # Build Query
    query = {"day": current_day}

    if role == "teacher":
        teacher = await db.teachers.find_one({"user_id": user_id})
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher profile not found")
        query["teacher_id"] = teacher["_id"]

    elif role == "student":
        student = await db.students.find_one({"user_id": user_id})
        # Fallback for older data where user_id might not be linked, 
        # or if student id is passed
        # But assuming user_id link exists
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # Filter by branch and semester
        # Note: If student semester is missing, this might return nothing or too much.
        # Strict filtering:
        if student.get("branch"):
            query["branch"] = student["branch"]
        if student.get("semester"):
            query["semester"] = student["semester"]
            
        if not student.get("branch"):
             # If branch is unknown, we cannot safely show class schedule for a student
             return TodayScheduleResponse(classes=[], current_day=current_day)

    else:
        raise HTTPException(status_code=403, detail="Role not authorized")

    # Execute Fetch
    cursor = db.schedules.find(query)
    schedules = await cursor.to_list(length=100)

    today_classes = []

    for s in schedules:
        # Resolve Subject Name
        subject_name = "Unknown Subject"
        if s.get("subject_id"):
            subject = await db.subjects.find_one({"_id": s["subject_id"]})
            if subject:
                subject_name = subject.get("name", "Unknown")

        # Basic Validation of times
        start_time = s.get("start_time")
        end_time = s.get("end_time")
        if not (start_time and end_time):
            continue

        today_classes.append(
            ClassPeriod(
                id=str(s.get("_id")),
                subject=subject_name,
                grade=str(s.get("semester")) if s.get("semester") else None,
                room=s.get("room_number"),
                start_time=start_time,
                end_time=end_time,
                slot=s.get("slot", 0),
                attendance_status=None,  # TODO: Implement attendance status check
            )
        )

    # Sort by start time
    try:
        today_classes.sort(
            key=lambda x: datetime.strptime(x.start_time, "%H:%M").time()
        )
    except ValueError:
        pass # Keep original order if parsing fails

    return TodayScheduleResponse(classes=today_classes, current_day=current_day)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_schedule_entry(
    entry: CreateScheduleRequest, current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403, detail="Only teachers can manage schedule"
        )

    teacher = await db.teachers.find_one({"user_id": current_user["_id"]})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    doc = entry.dict()

    # Validate ObjectId
    if not ObjectId.is_valid(entry.subject_id):
        raise HTTPException(400, "Invalid Subject ID")

    doc["subject_id"] = ObjectId(entry.subject_id)
    doc["teacher_id"] = teacher["_id"]  # Enforce teacher ownership

    result = await db.schedules.insert_one(doc)
    return {"id": str(result.inserted_id), "msg": "Schedule created"}


@router.delete("/{schedule_id}")
async def delete_schedule_entry(
    schedule_id: str, current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403, detail="Only teachers can manage schedule"
        )

    if not ObjectId.is_valid(schedule_id):
        raise HTTPException(400, "Invalid ID")

    teacher = await db.teachers.find_one({"user_id": current_user["_id"]})
    if not teacher:
        raise HTTPException(404, "Teacher info not found")

    res = await db.schedules.delete_one(
        {"_id": ObjectId(schedule_id), "teacher_id": teacher["_id"]}
    )
    
    if res.deleted_count == 0:
        raise HTTPException(404, "Schedule not found or permission denied")

    return {"msg": "Deleted"}


@router.put("/", status_code=status.HTTP_200_OK)
async def replace_full_schedule(
    entries: List[CreateScheduleRequest], current_user: dict = Depends(get_current_user)
):
    """
    Replace the entire schedule for the teacher.
    Deletes existing entries and inserts new ones.
    """
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403, detail="Only teachers can manage schedule"
        )

    teacher = await db.teachers.find_one({"user_id": current_user["_id"]})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    # 1. Delete all existing
    await db.schedules.delete_many({"teacher_id": teacher["_id"]})

    # 2. Insert new
    if not entries:
        return {"msg": "Schedule cleared"}

    new_docs = []
    for entry in entries:
        doc = entry.dict()
        if entry.subject_id and ObjectId.is_valid(entry.subject_id):
            doc["subject_id"] = ObjectId(entry.subject_id)
        doc["teacher_id"] = teacher["_id"]
        new_docs.append(doc)

    if new_docs:
        await db.schedules.insert_many(new_docs)

    return {"msg": f"Schedule updated with {len(new_docs)} entries"}
