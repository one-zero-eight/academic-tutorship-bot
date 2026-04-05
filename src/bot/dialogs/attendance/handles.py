import html

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput

from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error, log_info, log_warning
from src.bot.user_errors import *
from src.bot.utils import *
from src.db.repositories import meeting_repo

from .getters import *
from .logic import *
from .states import *


async def download_document_contents(message: Message, manager: DialogManager) -> str:
    manager = extend_dialog(manager)
    log_info("attendance.file.download.requested", user_id=message.chat.id)
    if not message.document:
        log_warning("attendance.file.download.invalid", user_id=message.chat.id, reason="no_document")
        raise NoDocumentError()
    file = await manager.bot.get_file(message.document.file_id)
    if not file.file_size:
        log_warning("attendance.file.download.invalid", user_id=message.chat.id, reason="no_file_size")
        raise ValueError("No file.file_size")
    if not file.file_path:
        log_warning("attendance.file.download.invalid", user_id=message.chat.id, reason="no_file_path")
        raise ValueError("No file.file_path")
    file_data = await manager.bot.download_file(file.file_path)
    if not file_data:
        log_warning("attendance.file.download.invalid", user_id=message.chat.id, reason="no_file_bytes")
        raise ValueError("No file bytes")
    return get_document_contents(file.file_size, file_data.read())


async def get_attendance_file_close(message: Message, __: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        log_info("attendance.close.requested", user_id=message.chat.id)
        contents = await download_document_contents(message, manager)
        emails = parse_attendance(contents)
        async with manager.state.sync_meeting() as meeting:
            await meeting_close(meeting, emails, closed_by_telegram_id=message.chat.id)
            log_info(
                "attendance.close.succeeded", user_id=message.chat.id, meeting_id=meeting.id, emails_count=len(emails)
            )
    except NoDocumentError:
        log_warning("attendance.close.invalid", user_id=message.chat.id, reason="no_document")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_NO_FILE"))
    except FileTooBigError:
        log_warning("attendance.close.invalid", user_id=message.chat.id, reason="file_too_big")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_FILE_TOO_BIG"))
    except Exception as e:
        log_error("attendance.close.failed", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(_("Q_ATTENDANCE_FILE_ERROR", error=html.escape(str(e))))
    await manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def get_attendance_file_resend(message: Message, __: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        log_info("attendance.resend.requested", user_id=message.chat.id)
        contents = await download_document_contents(message, manager)
        emails = parse_attendance(contents)
        async with manager.state.sync_meeting() as meeting:
            await meeting_repo.set_attendance(meeting.id, emails)
            log_info(
                "attendance.resend.succeeded", user_id=message.chat.id, meeting_id=meeting.id, emails_count=len(emails)
            )
    except NoDocumentError:
        log_warning("attendance.resend.invalid", user_id=message.chat.id, reason="no_document")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_NO_FILE"))
    except FileTooBigError:
        log_warning("attendance.resend.invalid", user_id=message.chat.id, reason="file_too_big")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_FILE_TOO_BIG"))
    except Exception as e:
        log_error("attendance.resend.failed", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(_("Q_ATTENDANCE_FILE_ERROR", error=html.escape(str(e))))
    await manager.switch_to(state=AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)


async def on_download_attendance(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    try:
        log_info("attendance.download.requested", user_id=query.from_user.id)
        meeting = await manager.state.get_meeting()
        input_file = await get_attendance_file_to_download(meeting)
        await query.answer(_("Q_ATTENDANCE_SENDING_FILE"))
        await manager.bot.send_document(manager.chat.id, document=input_file)
        log_info("attendance.download.succeeded", user_id=query.from_user.id, meeting_id=meeting.id)
    except NoMeetingAttendance:
        log_warning("attendance.download.no_data", user_id=query.from_user.id)
        return await query.answer(_("Q_ATTENDANCE_NO_ATTENDANCE"), show_alert=True)
    except Exception as e:
        log_error("attendance.download.failed", user_id=query.from_user.id, reason=str(e))
        return await query.answer(_("Q_ATTENDANCE_ERROR", error=html.escape(str(e))), show_alert=True)
    await manager.switch_to_current(ShowMode.DELETE_AND_SEND)  # to make window appear after the document


async def get_email_to_add(message: Message, __: MessageInput, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    await manager.clear_messages()
    await message.delete()
    try:
        if not message.text:
            raise NoMessageText
        email = message.text.strip()
        log_info("attendance.add_email.requested", user_id=message.chat.id, email=email[:64])
        async with manager.state.sync_meeting() as meeting:
            await add_email_to_attendance(email, meeting)
            log_info("attendance.add_email.succeeded", user_id=message.chat.id, meeting_id=meeting.id)
    except NoMessageText:
        log_warning("attendance.add_email.invalid", user_id=message.chat.id, reason="no_text")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_NO_TEXT_ADD_EMAIL"))
    except NoMeetingAttendance:
        log_warning("attendance.add_email.invalid", user_id=message.chat.id, reason="no_attendance")
        return await manager.answer_and_retry(_("Q_ATTENDANCE_NO_ATTENDANCE_RESEND"))
    except Exception as e:
        log_error("attendance.add_email.failed", user_id=message.chat.id, reason=str(e))
        return await manager.answer_and_retry(_("Q_ATTENDANCE_ERROR", error=html.escape(str(e))))
    await manager.switch_to(AttendanceStates.init, show_mode=ShowMode.DELETE_AND_SEND)
