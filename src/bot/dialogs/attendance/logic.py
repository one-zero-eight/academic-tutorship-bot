from aiogram.types import BufferedInputFile, InputFile, Message
from aiogram_dialog import DialogManager

from src.bot.dialog_extension import extend_dialog
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo
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
    if not meeting.attendance:
        raise NoMeetingAttendance()
    file_content = "\n".join([email.value for email in meeting.attendance])
    file_content += "\n"
    safe_title = re.sub(r"[^\w\s-]", "", meeting.title).strip().replace(" ", "_")
    filename = f"attendance_{safe_title}.txt"
    file_bytes = file_content.encode("utf-8")
    return BufferedInputFile(file_bytes, filename=filename)


async def extract_email(message: Message) -> Email:
    if not message.text:
        raise NoMessageText()
    return Email(message.text)


async def add_email_to_attendance(email: Email, manager: DialogManager):
    manager = extend_dialog(manager)
    async with manager.state.sync_meeting() as meeting:
        if not meeting.attendance:
            raise NoMeetingAttendance()
        if email in meeting.attendance:
            raise EmailAlreadyPresent()
        meeting.attendance.append(email)
        await meetings_repo.save(meeting)
