from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, ExceptionTypeFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ErrorEvent
from aiogram.utils.i18n import gettext as _

from src.bot.filters import StatusFilter, UserStatus
from src.db.repositories import meeting_repo, student_repo, tutor_repo
from src.domain.models import MeetingStatus
from src.notifications import notification_dp, notification_manager

from .texts import *

router = Router(name="notification_bot_handles")
notification_dp.include_router(router)


class ApprovalStates(StatesGroup):
    discard_reason = State()


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
        error_txt = _("Error: {error}").format(error=event.exception)
        await event.update.callback_query.answer(error_txt, show_alert=True)
        if isinstance(event.update.callback_query.message, types.Message):
            await event.update.callback_query.message.edit_reply_markup(reply_markup=None)
    # TODO: Log the error


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    assert message.from_user
    await student_repo.set_notification_bot_activated(telegram_id=message.from_user.id)

    payload = _extract_start_payload(message)
    match payload:
        case "from_control_bot":
            link = notification_manager.gen_control_bot_link("settings")
            await message.answer(START_FROM_CONTROL_BOT.format(link=link))
        case "guide":
            link = notification_manager.gen_control_bot_link("guide")
            await message.answer(START_FROM_CONTROL_BOT.format(link=link))
        case _:
            link = notification_manager.gen_control_bot_link()
            await message.answer(START_DEFAULT.format(link=link))


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("approve_", "discard_")))
async def handle_admin_approve_or_discard(query: types.CallbackQuery):
    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=1)
    lang = _resolve_query_lang(query)

    assert meeting_id_text.isdigit()
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)
    assert meeting.datetime_  # it should be set to be sent for approval
    if meeting.status != MeetingStatus.APPROVING:
        await query.answer(_("This meeting is not pending approval anymore"), show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    try:
        match action:
            case "approve":
                if meeting.datetime_ <= datetime.now():
                    raise TimeoutError("Meeting date is in the past")
                reply_markup = notification_manager.gen_confirm_approve_reply_markup(meeting_id, lang=lang)
                text = query.message.html_text + "\n\n" + MEETING_CONFIRM_APPROVE_APPENDIX
                await query.message.edit_text(text=text, reply_markup=reply_markup)
            case "discard":
                reply_markup = notification_manager.gen_confirm_discard_reply_markup(meeting_id, lang=lang)
                await query.message.edit_reply_markup(reply_markup=reply_markup)
    except TimeoutError as e:
        await query.answer(str(e), show_alert=True)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("confirm_approve_", "confirm_discard_")))
async def handle_admin_confirm_approve_or_confirm_discard(query: types.CallbackQuery, state: FSMContext):
    assert query.data and isinstance(query.message, types.Message)
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)

    if meeting.status != MeetingStatus.APPROVING:
        await query.answer("This meeting is not pending approval anymore", show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    try:
        match action:
            case "approve":  # TODO: maybe move that to logic layer?
                from src.bot.dialogs.meetings.logic import approve_meeting

                await approve_meeting(meeting)
                await query.answer("Meeting approval confirmed ✅", show_alert=True)
                await query.message.edit_reply_markup(reply_markup=None)
            case "discard":
                await query.answer("Enter reason to discard the meeting", show_alert=True)
                await state.set_state(ApprovalStates.discard_reason)
                await state.update_data(
                    {
                        "approving_meeting_id": meeting_id,
                        "message_id": query.message.message_id,
                    }
                )
                await query.message.edit_reply_markup(
                    reply_markup=notification_manager.gen_cancel_discard_reply_markup(
                        meeting_id,
                        lang=_resolve_query_lang(query),
                    )
                )
    except TimeoutError as e:
        await query.answer(str(e), show_alert=True)


@router.message(StatusFilter(UserStatus.admin), StateFilter(ApprovalStates.discard_reason), F.text)
async def handle_admin_discard_reason(message: types.Message, bot: Bot, state: FSMContext):
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
async def handle_admin_cancel_approve_or_cancel_discard(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await state.update_data(
        {
            "approving_meeting_id": None,
            "message_id": None,
        }
    )

    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer("Invalid callback data", show_alert=True)
        return
    # Go step back
    text = await _text_meeting_approve_request(int(meeting_id_text))
    reply_markup = notification_manager.gen_approve_discard_request_reply_markup(
        int(meeting_id_text),
        lang=_resolve_query_lang(query),
    )
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
    meeting = await meeting_repo.get(meeting_id)
    assert meeting.tutor_id
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    meeting_data = meeting.model_dump(by_alias=True)
    link = notification_manager.gen_meeting_link(meeting)
    return MEETING_APPROVE_REQUEST.format(**meeting_data, username=tutor.username, link=link)


def _resolve_query_lang(query: types.CallbackQuery) -> str:
    if not query.from_user.language_code:
        return "en"
    lang = query.from_user.language_code.strip().lower().split("-", maxsplit=1)[0]
    return lang or "en"
