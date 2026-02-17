import logging

from app.db.mongo import db
from app.core.email import BrevoEmailService

logger = logging.getLogger(__name__)


async def process_monthly_low_attendance_alerts():
    """
    1. Find teachers who have enabled 'settings.general.email_low_attendance_automated'
    2. For each teacher, get their subjects
    3. For each subject, find students with < 75% attendance
    4. Send email via Brevo
    """
    logger.info(
        "Starting monthly low attendance alert processing via automatic scheduler..."
    )

    # 1. Find teachers with the setting enabled
    # The setting is stored in 'settings.emailPreferences' array as an object:
    # { "key": "settings.general.email_low_attendance_automated", "enabled": true }
    
    # We need to find users where:
    # role = 'teacher' AND
    # settings.emailPreferences contains an element matching the key and enabled=true
    
    teachers_cursor = db.users.find({
        "role": "teacher",
        "settings.emailPreferences": {
            "$elemMatch": {
                "key": "settings.general.email_low_attendance_automated",
                "enabled": True
            }
        }
    })
    
    teachers = await teachers_cursor.to_list(length=None)
    
    if not teachers:
        logger.info("No teachers have enabled automated low attendance alerts.")
        return

    logger.info(f"Found {len(teachers)} teachers with automated alerts enabled.")

    emails_sent_count = 0

    for teacher in teachers:
        teacher_id = teacher["_id"]
        
        # 2. Get subjects for this teacher
        subjects_cursor = db.subjects.find({"professor_ids": teacher_id})
        subjects = await subjects_cursor.to_list(length=None)
        
        for subject in subjects:
            subject_name = subject.get("name", "Unknown Subject")
            students = subject.get("students", [])
            
            # 3. Iterate students and check attendance
            for student_record in students:
                # schema: { student_id: ObjectId, attendance: 
                # { present: int, absent: int, ... } }
                attendance = student_record.get("attendance", {})
                present = attendance.get("present", 0)
                absent = attendance.get("absent", 0)
                total = present + absent
                
                if total == 0:
                    continue # No classes conducted/attended, skip
                
                percentage = (present / total) * 100
                
                if percentage < 75.0:
                    # FETCH STUDENT EMAIL
                    student_user_id = student_record.get("student_id")
                    student_user = await db.users.find_one({"_id": student_user_id})
                    
                    if not student_user or not student_user.get("email"):
                        continue
                        
                    student_email = student_user["email"]
                    student_name = student_user.get("name", "Student")
                    
                    
                    # 4. Send Email
                    result = await BrevoEmailService.send_low_attendance_warning(
                        to_email=student_email,
                        student_name=student_name,
                        subject=subject_name,
                        attendance_percentage=percentage,
                        threshold=75,
                        present_count=present,
                        total_count=total
                    )
                    
                    if result.get("status") == "sent":
                        emails_sent_count += 1
                        logger.info(
                            f"Sent alert to student {student_user_id} for "
                            f"{subject_name} ({percentage:.1f}%)"
                        )
                    else:
                        error_msg = result.get("error", "Unknown error")
                        logger.error(
                            f"Failed to send alert to student {student_user_id}: "
                            f"{error_msg}"
                        )

    logger.info(
        f"Completed low attendance alert processing. "
        f"Total emails sent: {emails_sent_count}"
    )
