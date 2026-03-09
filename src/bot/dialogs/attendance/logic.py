from aiogram.types import BufferedInputFile, InputFile, Message
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo
from src.scheduling.scheduling import *

MAX_ATTENDANCE_FILE_SIZE = 5_242_880  # 5 MiB


async def get_document_contents(message: Message, manager: DialogManager) -> str:
    manager = extend_dialog(manager)
    if not message.document:
        raise NoDocumentError()
    file = await manager.bot.get_file(message.document.file_id)
    if not file.file_size:
        raise ValueError("No file.file_size")
    if not file.file_path:
        raise ValueError("No file.file_path")
    if file.file_size > MAX_ATTENDANCE_FILE_SIZE:
        raise FileTooBigError()
    bytes = await manager.bot.download_file(file.file_path)
    if not bytes:
        raise ValueError("No bytes")
    return bytes.read().decode("utf-8")


async def get_attendance_file_to_download(manager: DialogManager) -> InputFile:
    manager = extend_dialog(manager)
    meeting = await manager.state.get_meeting()
    if not await meeting_repo.has_attendance(meeting.id):
        raise NoMeetingAttendance()
    emails = await meeting_repo.get_attendance(meeting.id)
    file_content = "\n".join(emails)
    file_content += "\n"
    safe_title = re.sub(r"[^\w\s-]", "", meeting.title).strip().replace(" ", "_")
    filename = f"attendance_{safe_title}.txt"
    file_bytes = file_content.encode("utf-8")
    return BufferedInputFile(file_bytes, filename=filename)


async def add_email_to_attendance(email: str, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        if not await meeting_repo.has_attendance(meeting.id):
            raise NoMeetingAttendance()
        await meeting_repo.add_attendee(meeting.id, email)
