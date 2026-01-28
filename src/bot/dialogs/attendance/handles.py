from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from src.bot.dialog_extension import extend_dialog
from src.bot.dto import *
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meetings_repo

from .getters import *
from .logic import *
from .states import *


async def get_attendance_file_close(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        contents = await get_document_contents(message, manager)
        attendance = parse_attendance(contents)
        async with manager.state.sync_meeting() as meeting:
            meeting.close(attendance)
            await meetings_repo.save(meeting)
    except NoDocumentError:
        return await manager.answer_and_retry("You've sent no file ‼️")
    except FileTooBigError:
        return await manager.answer_and_retry("File you've sent is over 5MiB in size, I won't accept that ‼️")
    except Exception as e:
        return await manager.answer_and_retry(f"There is an error with your file: {e}")
    await manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def get_attendance_file_resend(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        contents = await get_document_contents(message, manager)
        attendance = parse_attendance(contents)
        async with manager.state.sync_meeting() as meeting:
            meeting._attendance = attendance
            await meetings_repo.save(meeting)
    except NoDocumentError:
        return await manager.answer_and_retry("You've sent no file ‼️")
    except FileTooBigError:
        return await manager.answer_and_retry("File you've sent is over 5MiB in size, I won't accept that ‼️")
    except Exception as e:
        return await manager.answer_and_retry(f"There is an error with your file: {e}")
    await manager.switch_to(state=AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_download_attendance(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    try:
        input_file = await get_attendance_file_to_download(manager)
        await query.answer("Sending attendance file...")
        await manager.bot.send_document(manager.chat.id, document=input_file)
    except NoMeetingAttendance:
        return await query.answer("This meeting has no attendance somehow", show_alert=True)
    except Exception as e:
        return await query.answer(f"Error: {e}", show_alert=True)
    await manager.switch_to_current(ShowMode.DELETE_AND_SEND)  # to make window appear after the document


async def get_email_to_add(message: Message, _: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()
    await message.delete()
    try:
        email = await extract_email(message)
        await add_email_to_attendance(email, manager)
    except NoMessageText:
        return await manager.answer_and_retry("There's no text in your message, enter email of a person to add")
    except NoMeetingAttendance:
        return await manager.answer_and_retry("Somehow there is no attendance for this meeting, resend the file maybe")
    except EmailAlreadyPresent:
        return await manager.answer_and_retry(f'"{email.value}" is already present')
    except Exception as e:
        return await manager.answer_and_retry(f"️Error: {e}")
    await manager.switch_to(AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)
