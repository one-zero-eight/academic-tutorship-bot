from aiogram.types import BufferedInputFile, InputFile

from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo, student_repo
from src.domain.models import Meeting
from src.notifications import notification_manager

MAX_ATTENDANCE_FILE_SIZE = 5_242_880  # 5 MiB


def get_document_contents(file_size: int, file_bytes: bytes) -> str:
    if file_size > MAX_ATTENDANCE_FILE_SIZE:
        log_warning("attendance.logic.file_too_big", file_size=file_size)
        raise FileTooBigError()
    return file_bytes.decode("utf-8")


async def get_attendance_file_to_download(meeting: Meeting) -> InputFile:
    if not await meeting_repo.has_attendance(meeting.id):
        log_warning("attendance.logic.download.no_attendance", meeting_id=meeting.id)
        raise NoMeetingAttendance()
    try:
        emails = await meeting_repo.get_attendance(meeting.id)
        file_content = "\n".join(emails)
        file_content += "\n"
        safe_title = re.sub(r"[^\w\s-]", "", meeting.title).strip().replace(" ", "_")
        filename = f"attendance_{safe_title}.txt"
        file_bytes = file_content.encode("utf-8")
    except Exception as e:
        log_error("attendance.logic.download.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("attendance.logic.download.file_built", meeting_id=meeting.id, emails_count=len(emails))
    return BufferedInputFile(file_bytes, filename=filename)


async def add_email_to_attendance(email: str, meeting: Meeting):
    if not await meeting_repo.has_attendance(meeting.id):
        log_warning("attendance.logic.add_email.blocked", meeting_id=meeting.id, reason="no_attendance")
        raise NoMeetingAttendance()
    try:
        await meeting_repo.add_attendee(meeting.id, email)
    except Exception as e:
        log_error("attendance.logic.add_email.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("attendance.logic.add_email.persisted", meeting_id=meeting.id)


async def meeting_close(meeting: Meeting, emails: list[str], closed_by_telegram_id: int):
    try:
        meeting.close()
        await meeting_repo.set_attendance(meeting.id, emails)
        await meeting_repo.update(meeting, ["status"])
        by_admin = await student_repo.is_admin(closed_by_telegram_id)
        await notification_manager.send_meeting_closed(meeting, by_admin=by_admin)
    except Exception as e:
        log_error("attendance.logic.close.failed", meeting_id=meeting.id, reason=str(e))
        raise
    log_info("attendance.logic.close.persisted_notified", meeting_id=meeting.id, by_admin=by_admin)
