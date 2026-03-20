from aiogram import F, Router, types
from aiogram.filters import CommandStart, ExceptionTypeFilter

from src.bot.filters import StatusFilter, UserStatus
from src.db.repositories import meeting_repo, tutor_repo

from .texts import *

router = Router(name="notification_bot_commands")


START_DEFAULT = """
Hello, I am a notification bot for Academic Tutorship of Innopolis.
I do nothing but sending notifications 💌

To see more go to <a href="{link}">Academic Tutorship</a>
"""

START_FROM_CONTROL_BOT = """
Thank you for activating the notification bot! 🎉
Here you will receive all notifications from Academic Tutorship 💌

To go back to the main bot <a href="{link}">click the link</a>
"""


def _extract_start_payload(message: types.Message) -> str | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    payload = parts[1].strip()
    return payload or None


@router.error(ExceptionTypeFilter(Exception))
async def on_error(query: types.CallbackQuery, error: Exception):
    await query.answer(f"Error: {error}", show_alert=True)
    # TODO: Log the error


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    link = notification_manager._gen_bot_link()
    payload = _extract_start_payload(message)
    if payload == "from_control_bot":
        await message.reply(START_FROM_CONTROL_BOT.format(link=link))
    else:
        await message.reply(START_DEFAULT.format(link=link))


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("approve_", "discard_")))
async def handle_admin_approve_discard(query: types.CallbackQuery):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=1)
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    meeting_id = int(meeting_id_text)
    if action == "approve":
        reply_markup = notification_manager._gen_confirm_approve_reply_markup(meeting_id)
        text = query.message.html_text + "\n\n" + MEETING_CONFIRM_APPROVE_APPENDIX
        await query.message.edit_text(text=text, reply_markup=reply_markup)
    elif action == "discard":
        reply_markup = notification_manager._gen_confirm_discard_reply_markup(meeting_id)
        await query.message.edit_reply_markup(reply_markup=reply_markup)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("confirm_approve_", "confirm_discard_")))
async def handle_admin_confirm_approve_discard(query: types.CallbackQuery):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    assert query.data and isinstance(query.message, types.Message)
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)
    if action == "approve":  # TODO: maybe move that to logic layer?
        assert meeting.tutor_id
        tutor = await tutor_repo.get(id=meeting.tutor_id)
        meeting.approve()
        await meeting_repo.update(meeting, attrs=["status"])
        await query.answer("Meeting approval confirmed ✅", show_alert=True)
        await notification_manager.send_meeting_approved(meeting)
        await notification_manager.send_meeting_announced(meeting, tutor)
    elif action == "discard":
        await query.answer("Meeting discard confirmed ❌", show_alert=True)
        meeting.discard_approval()
        await meeting_repo.update(meeting, attrs=["status"])
        await notification_manager.send_meeting_discarded(meeting, "no way to input reason for now, sorry")
    await query.message.edit_reply_markup(reply_markup=None)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("cancel_approve_", "cancel_discard_")))
async def handle_admin_cancel_approve_discard(query: types.CallbackQuery):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    # Go step back
    text = await _text_meeting_approve_request(int(meeting_id_text))
    reply_markup = notification_manager._gen_approve_discard_request_reply_markup(int(meeting_id_text))
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(
    ~StatusFilter(UserStatus.admin), F.data.startswith(("approve_", "discard_", "confirm_approve_", "confirm_discard_"))
)
async def handle_non_admin_approve_discard(query: types.CallbackQuery):
    await query.answer("You are not authorized to perform this action", show_alert=True)
    if isinstance(query.message, types.Message):
        await query.message.edit_reply_markup(reply_markup=None)


async def _text_meeting_approve_request(meeting_id: int):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    meeting = await meeting_repo.get(meeting_id)
    assert meeting.tutor_id
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    meeting_data = meeting.model_dump(by_alias=True)
    link = notification_manager._gen_meeting_link(meeting)
    return MEETING_APPROVE_REQUEST.format(**meeting_data, username=tutor.username, link=link)
