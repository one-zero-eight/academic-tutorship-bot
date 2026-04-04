from datetime import datetime

from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart, ExceptionTypeFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ErrorEvent

from src.bot.filters import StatusFilter, UserStatus
from src.bot.i18n import NOTIFICATION_L10NS
from src.db.repositories import meeting_repo, student_repo, tutor_repo
from src.domain.models import MeetingStatus
from src.notifications import notification_dp, notification_manager

router = Router(name="notification_bot_handles")
notification_dp.include_router(router)


# region states


class ApprovalStates(StatesGroup):
    discard_reason = State()


class UpdateApprovalStates(StatesGroup):
    discard_reason = State()


# endregion states


# region utils


def _telegram_lang_or_default(language_code: str | None) -> str:
    if not language_code:
        return "en"
    lang = language_code.strip().lower().split("-", maxsplit=1)[0]
    return lang or "en"


async def resolve_lang(event: types.CallbackQuery | types.Message) -> str:
    if isinstance(query := event, types.CallbackQuery):
        default_lang = _telegram_lang_or_default(query.from_user.language_code)
        return await student_repo.get_language(telegram_id=query.from_user.id, default=default_lang)
    if isinstance(message := event, types.Message):
        if not message.from_user:
            return "en"
        default_lang = _telegram_lang_or_default(message.from_user.language_code)
        return await student_repo.get_language(telegram_id=message.from_user.id, default=default_lang)
    return "en"


def translate(text_id: str, lang: str, **kwargs) -> str:
    l10n = NOTIFICATION_L10NS.get(lang, NOTIFICATION_L10NS["en"])
    return l10n.format_value(text_id, kwargs)


def extract_start_payload(message: types.Message) -> str | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    payload = parts[1].strip()
    return payload or None


async def text_meeting_approve_request(meeting_id: int, lang: str):
    meeting = await meeting_repo.get(meeting_id)
    assert meeting.tutor_id
    tutor = await tutor_repo.get(id=meeting.tutor_id)
    meeting_data = meeting.model_dump(by_alias=True)
    link = notification_manager.gen_meeting_link(meeting.id)
    return translate(
        "NOTIF_MEETING_APPROVE_REQUEST",
        lang,
        **meeting_data,
        username=tutor.username,
        link=link,
    )


async def text_update_approve_request(meeting_id: int, lang: str):
    meeting = await meeting_repo.get(meeting_id)
    assert meeting.tutor_id
    meeting_update = await meeting_repo.get_update(meeting_id)
    link = notification_manager.gen_meeting_link(meeting.id)
    old_datetime = meeting.datetime_.isoformat(sep=" ", timespec="minutes") if meeting.datetime_ else "-"
    new_datetime = (
        meeting_update.datetime_.isoformat(sep=" ", timespec="minutes") if meeting_update.datetime_ else old_datetime
    )
    data = {
        "old_datetime": old_datetime,
        "datetime": new_datetime,
        "room_old": meeting.room,
        "room": meeting_update.room or meeting.room,
    }
    lines = [translate("NOTIF_MEETING_UPDATE_REQUEST", lang, title=meeting.title)]
    if meeting_update.datetime_:
        lines.append(translate("NOTIF_MEETING_UPDATE_DATETIME", lang, **data))
    if meeting_update.room:
        lines.append(translate("NOTIF_MEETING_UPDATE_ROOM", lang, **data))
    lines.append(translate("NOTIF_MEETING_LINK", lang, link=link))
    return "\n".join(lines)


# endregion utils


# region common


@router.error(ExceptionTypeFilter(Exception))
async def on_error(event: ErrorEvent):
    if event.update.callback_query:
        error_txt = translate("NH_ERROR", await resolve_lang(event.update.callback_query), error=str(event.exception))
        await event.update.callback_query.answer(error_txt, show_alert=True)
        if isinstance(event.update.callback_query.message, types.Message):
            await event.update.callback_query.message.edit_reply_markup(reply_markup=None)
    # TODO: Log the error


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    assert message.from_user
    await student_repo.set_notification_bot_activated(telegram_id=message.from_user.id)
    lang = await resolve_lang(message)

    payload = extract_start_payload(message)
    match payload:
        case "from_control_bot":
            link = notification_manager.gen_control_bot_link("settings")
            await message.answer(translate("NH_START_FROM_CONTROL_BOT", lang, link=link))
        case "guide":
            link = notification_manager.gen_control_bot_link("guide")
            await message.answer(translate("NH_START_FROM_CONTROL_BOT", lang, link=link))
        case _:
            link = notification_manager.gen_control_bot_link()
            await message.answer(translate("NH_START_DEFAULT", lang, link=link))


@router.callback_query(
    ~StatusFilter(UserStatus.admin),
    F.data.startswith(
        (
            "approve_",
            "discard_",
            "confirm_approve_",
            "confirm_discard_",
            "update_approve_",
            "update_discard_",
            "update_confirm_approve_",
            "update_confirm_discard_",
        )
    ),
)
async def handle_non_admin_approve_discard(query: types.CallbackQuery):
    await query.answer(translate("NH_NOT_AUTHORIZED", await resolve_lang(query)), show_alert=True)
    if isinstance(query.message, types.Message):
        await query.message.edit_reply_markup(reply_markup=None)


# endregion common


# region appprove discard meeting


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("approve_", "discard_")))
async def handle_admin_approve_or_discard(query: types.CallbackQuery):
    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=1)
    lang = await resolve_lang(query)

    assert meeting_id_text.isdigit()
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)
    assert meeting.datetime_  # it should be set to be sent for approval
    if meeting.status != MeetingStatus.APPROVING:
        await query.answer(translate("NH_MEETING_NOT_PENDING", lang), show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    try:
        match action:
            case "approve":
                if meeting.datetime_ <= datetime.now():
                    raise TimeoutError("Meeting date is in the past")
                reply_markup = notification_manager.gen_confirm_approve_meeting_reply_markup(meeting_id, lang=lang)
                text = query.message.html_text + "\n\n" + translate("NOTIF_MEETING_CONFIRM_APPROVE_APPENDIX", lang)
                await query.message.edit_text(text=text, reply_markup=reply_markup)
            case "discard":
                reply_markup = notification_manager.gen_confirm_discard_meeting_reply_markup(meeting_id, lang=lang)
                await query.message.edit_reply_markup(reply_markup=reply_markup)
    except TimeoutError:
        await query.answer(translate("NH_DATE_IN_PAST", lang), show_alert=True)


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("confirm_approve_", "confirm_discard_")))
async def handle_admin_confirm_approve_or_confirm_discard(query: types.CallbackQuery, state: FSMContext):
    assert query.data and isinstance(query.message, types.Message)
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    if not meeting_id_text.isdigit():
        await query.answer(translate("NH_INVALID_CALLBACK_DATA", await resolve_lang(query)), show_alert=True)
        return
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)

    if meeting.status != MeetingStatus.APPROVING:
        await query.answer(translate("NH_MEETING_NOT_PENDING", await resolve_lang(query)), show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    lang = await resolve_lang(query)

    try:
        match action:
            case "approve":  # TODO: maybe move that to logic layer?
                from src.bot.dialogs.meetings.logic import approve_meeting

                await approve_meeting(meeting)
                await query.answer(translate("NH_MEETING_APPROVE_CONFIRMED", lang), show_alert=True)
                await query.message.edit_reply_markup(reply_markup=None)
            case "discard":
                await query.answer(translate("NH_MEETING_DISCARD_REASON_PROMPT", lang), show_alert=True)
                await state.set_state(ApprovalStates.discard_reason)
                await state.update_data(
                    {
                        "approving_meeting_id": meeting_id,
                        "message_id": query.message.message_id,
                    }
                )
                await query.message.edit_reply_markup(
                    reply_markup=notification_manager.gen_cancel_discard_meeting_reply_markup(
                        meeting_id,
                        lang=lang,
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
        await query.answer(translate("NH_INVALID_CALLBACK_DATA", await resolve_lang(query)), show_alert=True)
        return
    # Go step back
    lang = await resolve_lang(query)
    text = await text_meeting_approve_request(int(meeting_id_text), lang)
    reply_markup = notification_manager.gen_approve_discard_meeting_request_reply_markup(
        int(meeting_id_text),
        lang=lang,
    )
    await query.message.edit_text(text, reply_markup=reply_markup)


# endregion approve discard meeting


# region approve discard update


@router.callback_query(StatusFilter(UserStatus.admin), F.data.startswith(("update_approve_", "update_discard_")))
async def handle_admin_update_approve_or_discard(query: types.CallbackQuery):
    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=2)[1:]
    lang = await resolve_lang(query)

    assert meeting_id_text.isdigit()
    meeting_id = int(meeting_id_text)
    try:
        await meeting_repo.get_update(meeting_id)
    except LookupError:
        await query.answer(translate("NH_UPDATE_NOT_PENDING", lang), show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    try:
        match action:
            case "approve":
                reply_markup = notification_manager.gen_confirm_approve_update_reply_markup(meeting_id, lang=lang)
                text = query.message.html_text + "\n\n" + translate("NH_UPDATE_CONFIRM_APPROVE_APPENDIX", lang)
                await query.message.edit_text(text=text, reply_markup=reply_markup)
            case "discard":
                reply_markup = notification_manager.gen_confirm_discard_update_reply_markup(meeting_id, lang=lang)
                await query.message.edit_reply_markup(reply_markup=reply_markup)
    except TimeoutError as e:
        await query.answer(translate("NH_ERROR", lang, error=str(e)), show_alert=True)


@router.callback_query(
    StatusFilter(UserStatus.admin), F.data.startswith(("update_confirm_approve_", "update_confirm_discard_"))
)
async def handle_admin_update_confirm_approve_or_confirm_discard(query: types.CallbackQuery, state: FSMContext):
    assert query.data and isinstance(query.message, types.Message)
    action, meeting_id_text = query.data.split("_", maxsplit=3)[2:]

    assert meeting_id_text.isdigit()
    meeting_id = int(meeting_id_text)
    meeting = await meeting_repo.get(meeting_id)

    try:
        meeting_update = await meeting_repo.get_update(meeting_id)
    except LookupError:
        await query.answer(translate("NH_UPDATE_NOT_PENDING", await resolve_lang(query)), show_alert=True)
        await query.message.edit_reply_markup(reply_markup=None)
        return

    lang = await resolve_lang(query)

    try:
        match action:
            case "approve":  # TODO: maybe move that to logic layer?
                from src.bot.dialogs.meetings.logic import approve_meeting_update

                await approve_meeting_update(meeting, meeting_update)
                await query.answer(translate("NH_UPDATE_APPROVE_CONFIRMED", lang), show_alert=True)
                await query.message.edit_reply_markup(reply_markup=None)
            case "discard":
                await query.answer(translate("NH_UPDATE_DISCARD_REASON_PROMPT", lang), show_alert=True)
                await state.set_state(UpdateApprovalStates.discard_reason)
                await state.update_data(
                    {
                        "approving_meeting_id": meeting_id,
                        "message_id": query.message.message_id,
                    }
                )
                await query.message.edit_reply_markup(
                    reply_markup=notification_manager.gen_cancel_discard_update_reply_markup(
                        meeting_id,
                        lang=lang,
                    )
                )
    except TimeoutError as e:
        await query.answer(translate("NH_ERROR", lang, error=str(e)), show_alert=True)


@router.message(StatusFilter(UserStatus.admin), StateFilter(UpdateApprovalStates.discard_reason), F.text)
async def handle_admin_update_discard_reason(message: types.Message, bot: Bot, state: FSMContext):
    meeting_id = await state.get_value("approving_meeting_id")
    message_id = await state.get_value("message_id")
    assert meeting_id and message.html_text

    meeting = await meeting_repo.get(meeting_id)
    meeting_update = await meeting_repo.get_update(meeting_id)

    await meeting_repo.remove_update(meeting_id)
    await notification_manager.send_meeting_update_discarded(meeting, meeting_update, message.html_text)

    await state.set_state(None)
    await state.update_data(
        {
            "approving_meeting_id": None,
            "message_id": None,
        }
    )
    await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message_id, reply_markup=None)


@router.callback_query(
    StatusFilter(UserStatus.admin), F.data.startswith(("update_cancel_approve_", "update_cancel_discard_"))
)
async def handle_admin_update_cancel_approve_or_cancel_discard(query: types.CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await state.update_data(
        {
            "approving_meeting_id": None,
            "message_id": None,
        }
    )

    assert query.data and isinstance(query.message, types.Message) and query.message.text
    action, meeting_id_text = query.data.split("_", maxsplit=3)[2:]
    if not meeting_id_text.isdigit():
        await query.answer(translate("NH_INVALID_CALLBACK_DATA", await resolve_lang(query)), show_alert=True)
        return
    # Go step back
    lang = await resolve_lang(query)
    text = await text_update_approve_request(int(meeting_id_text), lang)
    reply_markup = notification_manager.gen_approve_discard_update_request_reply_markup(
        int(meeting_id_text),
        lang=lang,
    )
    await query.message.edit_text(text, reply_markup=reply_markup)


# endregion approve discard update
