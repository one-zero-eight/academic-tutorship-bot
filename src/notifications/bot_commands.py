from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, ExceptionTypeFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ErrorEvent, InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.filters import StatusFilter, UserStatus
from src.db.repositories import meeting_repo, tutor_repo

from .texts import *

router = Router(name="notification_bot_commands")


class ApprovalStates(StatesGroup):
    discard_reason = State()


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
async def on_error(event: ErrorEvent):
    if event.update.callback_query:
        await event.update.callback_query.answer(f"Error: {event.exception}", show_alert=True)
        if isinstance(event.update.callback_query.message, types.Message):
            await event.update.callback_query.message.edit_reply_markup(reply_markup=None)
    # TODO: Log the error


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    payload = _extract_start_payload(message)
    if payload == "from_control_bot":
        link = notification_manager.gen_control_bot_link("settings")
        await message.answer(START_FROM_CONTROL_BOT.format(link=link))
    else:
        link = notification_manager.gen_control_bot_link()
        await message.answer(START_DEFAULT.format(link=link))


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
        reply_markup = notification_manager.gen_confirm_approve_reply_markup(meeting_id)
        text = query.message.html_text + "\n\n" + MEETING_CONFIRM_APPROVE_APPENDIX
        await query.message.edit_text(text=text, reply_markup=reply_markup)
    elif action == "discard":
        reply_markup = notification_manager.gen_confirm_discard_reply_markup(meeting_id)
        await query.message.edit_reply_markup(reply_markup=reply_markup)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("confirm_approve_", "confirm_discard_")))
async def handle_admin_confirm_approve_discard(query: types.CallbackQuery, state: FSMContext):
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
        await query.message.edit_reply_markup(reply_markup=None)
    elif action == "discard":
        await query.answer("Enter reason to discard the meeting", show_alert=True)
        await state.set_state(ApprovalStates.discard_reason)
        await state.update_data(
            {
                "approving_meeting_id": meeting_id,
                "message_id": query.message.message_id,
            }
        )
        await query.message.edit_reply_markup(reply_markup=_cancel_approval_discard_kbd(meeting_id))


@router.message(StatusFilter(UserStatus.admin), StateFilter(ApprovalStates.discard_reason), F.text)
async def handle_admin_discard_reason(message: types.Message, bot: Bot, state: FSMContext):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    meeting_id = await state.get_value("approving_meeting_id")
    message_id = await state.get_value("message_id")
    assert meeting_id and message.html_text

    meeting = await meeting_repo.get(meeting_id)
    meeting.discard_approval()
    await meeting_repo.update(meeting, attrs=["status"])
    await notification_manager.send_meeting_discarded(meeting, message.html_text)

    await state.set_state(None)
    await state.update_data(
        {
            "approving_meeting_id": None,
            "message_id": None,
        }
    )
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=None)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("cancel_approve_", "cancel_discard_")))
async def handle_admin_cancel_approve_discard(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await state.update_data(
        {
            "approving_meeting_id": None,
            "message_id": None,
        }
    )
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    # Go step back
    text = await _text_meeting_approve_request(int(meeting_id_text))
    reply_markup = notification_manager.gen_approve_discard_request_reply_markup(int(meeting_id_text))
    await query.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(
    ~StatusFilter(UserStatus.admin), F.data.startswith(("approve_", "discard_", "confirm_approve_", "confirm_discard_"))
)
async def handle_non_admin_approve_discard(query: types.CallbackQuery):
    await query.answer("You are not authorized to perform this action", show_alert=True)
    if isinstance(query.message, types.Message):
        await query.message.edit_reply_markup(reply_markup=None)


# == utils ==


async def _text_meeting_approve_request(meeting_id: int):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    meeting = await meeting_repo.get(meeting_id)
    assert meeting.tutor_id
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    meeting_data = meeting.model_dump(by_alias=True)
    link = notification_manager.gen_meeting_link(meeting)
    return MEETING_APPROVE_REQUEST.format(**meeting_data, username=tutor.username, link=link)


def _cancel_approval_discard_kbd(meeting_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data=f"cancel_discard_{meeting_id}")]]
    )
