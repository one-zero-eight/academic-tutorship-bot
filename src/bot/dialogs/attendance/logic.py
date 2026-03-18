from aiogram.types import BufferedInputFile, InputFile

from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo, student_repo
from src.domain.models import Meeting
from src.notifications import notification_manager

MAX_ATTENDANCE_FILE_SIZE = 5_242_880  # 5 MiB


def get_document_contents(file_size: int, file_bytes: bytes) -> str:
    if file_size > MAX_ATTENDANCE_FILE_SIZE:
        raise FileTooBigError()
    return file_bytes.decode("utf-8")


async def get_attendance_file_to_download(meeting: Meeting) -> InputFile:
    if not await meeting_repo.has_attendance(meeting.id):
        raise NoMeetingAttendance()
    emails = await meeting_repo.get_attendance(meeting.id)
    file_content = "\n".join(emails)
    file_content += "\n"
    safe_title = re.sub(r"[^\w\s-]", "", meeting.title).strip().replace(" ", "_")
    filename = f"attendance_{safe_title}.txt"
    file_bytes = file_content.encode("utf-8")
    return BufferedInputFile(file_bytes, filename=filename)


async def add_email_to_attendance(email: str, meeting: Meeting):
    if not await meeting_repo.has_attendance(meeting.id):
        raise NoMeetingAttendance()
    await meeting_repo.add_attendee(meeting.id, email)


async def meeting_close(meeting: Meeting, emails: list[str], closed_by_telegram_id: int):
    meeting.close()
    await meeting_repo.set_attendance(meeting.id, emails)
    await meeting_repo.update(meeting, ["status"])
    by_admin = await student_repo.is_admin(closed_by_telegram_id)
    await notification_manager.send_meeting_closed(meeting, by_admin=by_admin)
