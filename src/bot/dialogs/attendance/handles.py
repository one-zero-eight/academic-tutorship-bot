from aiogram.types import BufferedInputFile, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from src.bot.dto import *
from src.bot.utils import *
from src.db.repositories import meetings_repo

from .getters import *
from .states import *

MAX_ATTENDANCE_FILE_SIZE = 5_242_880  # 5 MiB


async def get_attendance_file_close(message: Message, _: MessageInput, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data["bot"]
    state = get_state(dialog_manager)
    await clear_messages(dialog_manager)
    await message.delete()

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    if not message.document:
        to_delete = await message.answer("You've sent no file ‼️")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.close, show_mode=ShowMode.DELETE_AND_SEND)

    file = await bot.get_file(message.document.file_id)

    if not file.file_size:
        raise ValueError("No file.file_size")
    if not file.file_path:
        raise ValueError("No file.file_path")

    if file.file_size > MAX_ATTENDANCE_FILE_SIZE:
        to_delete = await message.answer("File you've sent is over 5MiB in size, I won't accept that ‼️")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.close, show_mode=ShowMode.DELETE_AND_SEND)

    bytes = await bot.download_file(file.file_path)
    if not bytes:
        raise ValueError("No bytes")

    content: str = bytes.read().decode("utf-8")

    try:
        attendance = parse_attendance(content)
        meeting.close(attendance)
        await meetings_repo.save(meeting)
    except Exception as e:
        to_delete = await message.answer(f"There is an error with your file: {e}")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.close, show_mode=ShowMode.DELETE_AND_SEND)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def get_attendance_file_resend(message: Message, _: MessageInput, dialog_manager: DialogManager):
    bot: Bot = dialog_manager.middleware_data["bot"]
    state = get_state(dialog_manager)
    await clear_messages(dialog_manager)
    await message.delete()

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    if not message.document:
        to_delete = await message.answer("You've sent no file ‼️")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.resend, show_mode=ShowMode.DELETE_AND_SEND)

    file = await bot.get_file(message.document.file_id)

    if not file.file_size:
        raise ValueError("No file.file_size")
    if not file.file_path:
        raise ValueError("No file.file_path")

    if file.file_size > MAX_ATTENDANCE_FILE_SIZE:
        to_delete = await message.answer("File you've sent is over 5MiB in size, I won't accept that ‼️")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.resend, show_mode=ShowMode.DELETE_AND_SEND)

    bytes = await bot.download_file(file.file_path)
    if not bytes:
        raise ValueError("No bytes")

    content: str = bytes.read().decode("utf-8")

    try:
        attendance = parse_attendance(content)
        meeting._attendance = attendance
        await meetings_repo.save(meeting)
    except Exception as e:
        to_delete = await message.answer(f"There is an error with your file: {e}")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.resend, show_mode=ShowMode.DELETE_AND_SEND)

    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await dialog_manager.switch_to(state=AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_download_attendance(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    state = get_state(dialog_manager)

    if not query.message:
        raise ValueError("No query.message")

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    if not meeting.attendance:
        return await query.answer("This meeting has no attendance somehow", show_alert=True)

    file_content = "\n".join([email.value for email in meeting.attendance])
    file_content += "\n"

    safe_title = re.sub(r"[^\w\s-]", "", meeting.title).strip().replace(" ", "_")
    filename = f"attendance_{safe_title}.txt"

    file_bytes = file_content.encode("utf-8")

    try:
        input_file = BufferedInputFile(file_bytes, filename=filename)
        await query.answer("Sending attendance file...")
        await query.message.answer_document(document=input_file)
        await dialog_manager.switch_to(
            state=AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND
        )  # to make window appear after the document
    except Exception as e:
        await query.answer(f"Error: {e}", show_alert=True)


async def get_email_to_add(message: Message, _: MessageInput, dialog_manager: DialogManager):
    state = get_state(dialog_manager)
    await clear_messages(dialog_manager)
    await message.delete()

    if not message.text:
        to_delete = await message.answer("️There's no text in your message, enter email of a person to add")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.add_email, show_mode=ShowMode.DELETE_AND_SEND)

    meeting = dto_to_meeting(await state.get_value("meeting"))
    if not meeting:
        raise ValueError("No meeting")

    if not meeting.attendance:
        to_delete = await message.answer("Somehow there is no attendance for this meeting, resend the file maybe")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.add_email, show_mode=ShowMode.DELETE_AND_SEND)

    try:
        email = Email(message.text)
    except Exception as e:
        to_delete = await message.answer(f"️Error: {e}")
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.add_email, show_mode=ShowMode.DELETE_AND_SEND)

    if email in meeting.attendance:
        to_delete = await message.answer(f'"{email.value}" is already present')
        await track_message(to_delete, dialog_manager)
        return await dialog_manager.switch_to(AttendanceStates.add_email, show_mode=ShowMode.DELETE_AND_SEND)

    meeting.attendance.append(email)
    await state.update_data({"meeting": meeting_to_dto(meeting)})
    await meetings_repo.save(meeting)

    await dialog_manager.switch_to(AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)
