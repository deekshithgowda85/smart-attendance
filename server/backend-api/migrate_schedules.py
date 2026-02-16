import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "smart-attendance")

async def migrate():
    print(f"Connecting to {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Check if 'schedules' collection exists or is empty
    count = await db.schedules.count_documents({})
    if count > 0:
        print(
            f"Schedules collection already has {count} documents. "
            "Skipping migration (or clear it manually first)."
        )
        # return # Uncomment to prevent double migration, for now I'll just print

    print("Fetching teachers...")
    teachers = db.teachers.find({})
    
    new_schedules = []
    
    async for teacher in teachers:
        teacher_id = teacher.get("_id")
        branch = teacher.get("branch") # Taking branch from teacher level
        
        # Check nested schedule
        schedule = teacher.get("schedule", {})
        timetable = schedule.get("timetable", [])
        
        for day_schedule in timetable:
            day_name = day_schedule.get("day")
            periods = day_schedule.get("periods", [])
            
            for period in periods:
                metadata = period.get("metadata", {})
                
                # Check for required fields
                # If subject_id is missing, we can't create a valid link, 
                # but maybe we migrate anyway?
                subject_id = metadata.get("subject_id") if metadata else None

                # Start/End times
                start_time = period.get("start")
                end_time = period.get("end")
                slot = period.get("slot")

                if not (day_name and start_time and end_time):
                    print(f"Skipping invalid period for teacher {teacher_id}: {period}")
                    continue

                entry = {
                    "day": day_name,
                    "slot": slot,
                    "start_time": start_time,
                    "end_time": end_time,
                    "teacher_id": teacher_id,
                    "subject_id": ObjectId(subject_id) if subject_id else None,
                    "room_number": metadata.get("room"),
                    "branch": branch,  # Inherit from teacher
                    "semester": None # Not available in current structure
                }
                
                # Try to guess semester from grade if available
                # metadata.grade might exist based on routes/schedule.py ClassPeriod
                grade = metadata.get("grade") # e.g. "4th Sem"
                if grade:
                    # simplistic parsing
                    try:
                        import re
                        match = re.search(r'\d+', str(grade))
                        if match:
                            entry["semester"] = int(match.group())
                    except Exception:
                        pass

                new_schedules.append(entry)

    if new_schedules:
        print(f"Migrating {len(new_schedules)} schedule entries...")
        result = await db.schedules.insert_many(new_schedules)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    else:
        print("No schedule data found to migrate.")

if __name__ == "__main__":
    asyncio.run(migrate())
