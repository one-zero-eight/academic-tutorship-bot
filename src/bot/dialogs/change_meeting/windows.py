from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Calendar, Cancel, Column, Row, Start, SwitchTo

from src.bot.custom_widgets import MeetingDateRoomText, MeetingInfoText
from src.bot.dialogs.discipline_picker import DisciplinePickerStates
from src.bot.dialogs.meetings.getters import meeting_info_getter
from src.bot.filters import *
from src.bot.i18n import I18NFormat as I18N

from .dialog_buttons import *
from .getters import *
from .handles import *
from .states import *

info_change_ww = Window(
    MeetingInfoText(admin_info=True),
    Column(
        Button(
            I18N("CHANGE_INFO_BTN_TITLE_DISCIPLINE"), id="change_title_discipline", on_click=on_title_discipline_btn
        ),
        Button(I18N("CHANGE_INFO_BTN_DATE_ROOM"), id="to_date_room", on_click=on_date_room_btn),
        SwitchTo(
            I18N("CHANGE_INFO_BTN_ASSIGN_TUTOR"),
            id="assign_tutor",
            state=ChangeStates.tutor,
            on_click=open_assign_tutor,
            when="is_admin",
        ),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DURATION"), id="choose_duration", state=ChangeStates.duration),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DESCRIPTION"), id="set_description", state=ChangeStates.description),
    ),
    Row(Cancel(I18N("COMMON_BTN_BACK")), BTN_BLANK),
    state=ChangeStates.init,
    getter=meeting_info_getter,
)


title_discipline_ww = Window(
    MeetingInfoText(only_head=True),
    Row(
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_TITLE"), id="change_title", state=ChangeStates.title),
        Start(I18N("MEETING_CREATE_BTN_DISCIPLINE"), id="change_discipline", state=DisciplinePickerStates.language),
    ),
    Row(
        SwitchTo(
            I18N("COMMON_BTN_BACK"), id="to_info", state=ChangeStates.init, on_click=on_back_from_title_discipline_btn
        ),
        BTN_BLANK,
    ),
    getter=meeting_change_title_discipline_getter,
    state=ChangeStates.title_discipline,
)


date_room_ww = Window(
    MeetingDateRoomText(),
    Row(
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_DATE"), id="change_date", state=ChangeStates.date),
        SwitchTo(I18N("CHANGE_INFO_BTN_SET_ROOM"), id="change_room", state=ChangeStates.room),
    ),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_init", state=ChangeStates.init), BTN_BLANK, when="nothing_to_save"),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), id="to_init", state=ChangeStates.init),
        SwitchTo(
            I18N("MEETING_UPDATE_BTN_SAVE"),
            id="save_and_back",
            state=ChangeStates.init,
            on_click=on_date_room_save_rightaway,
        ),  # TODO: add handle that saves changes to db
        when="can_save_rightaway",
    ),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), id="to_init", state=ChangeStates.init),
        SwitchTo(I18N("MEETING_UPDATE_BTN_SAVE"), id="to_save_approve", state=ChangeStates.save_approve),
        when="can_send_approve",
    ),
    getter=meeting_change_date_room_getter,
    state=ChangeStates.date_room,
)


async def on_date_room_request_approve(query: CallbackQuery, __, manager: DialogManager):
    manager = extend_dialog(manager)
    _ = manager.tr
    meeting = await manager.state.get_meeting()
    update = await manager.state.get_value("meeting_update", {})
    log_info("meeting.change.on_date_room_request_approve.init", user_id=manager.chat.id)
    if not update:
        await query.answer(_("Q_CHANGE_UPDATE_NO_UPDATES"), show_alert=True)
        log_warning(
            "meeting.change.on_date_room_request_approve.no_updates", user_id=manager.chat.id, meeting_id=meeting.id
        )
        return
    if await meeting_repo.exists_update(meeting.id):
        await query.answer(_("Q_CHANGE_UPDATE_ALREADY_PENDING"), show_alert=True)
        log_warning(
            "meeting.change.on_date_room_request_approve.pending", user_id=manager.chat.id, meeting_id=meeting.id
        )
        return
    meeting_update = MeetingUpdate(id=meeting.id, **update)
    await meeting_repo.save_update(meeting_update)
    await notification_manager.send_meeting_update_request(meeting_update)
    await query.answer(_("Q_CHANGE_UPDATE_SENT"), show_alert=True)
    log_info("meeting.change.on_date_room_request_approve.sent", user_id=manager.chat.id, meeting_update=meeting_update)


save_approve_ww = Window(
    I18N("MEETING_UPDATE_SAVE_HEADER"),
    Row(
        SwitchTo(I18N("COMMON_BTN_BACK"), id="back_to_dr", state=ChangeStates.date_room),
        SwitchTo(
            I18N("MEETING_UPDATE_BTN_SEND"),
            id="send_changes_approve",
            state=ChangeStates.init,
            on_click=on_date_room_request_approve,
        ),
    ),
    state=ChangeStates.save_approve,
)


set_title_ww = Window(
    I18N("CHANGE_SET_TITLE_PROMPT"),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="back_to_td", state=ChangeStates.title_discipline), BTN_BLANK),
    MessageInput(get_meeting_title),
    state=ChangeStates.title,
    getter=meeting_info_getter,
)


set_description_ww = Window(
    I18N("CHANGE_SET_DESCRIPTION_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_description),
    state=ChangeStates.description,
    getter=meeting_info_getter,
)


set_room_ww = Window(
    I18N("CHANGE_SET_ROOM_PROMPT"),
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_dr", state=ChangeStates.date_room), BTN_BLANK),
    MessageInput(get_meeting_room),
    state=ChangeStates.room,
    getter=meeting_info_getter,
)


set_date_ww = Window(
    I18N("CHANGE_SET_DATE_PROMPT"),
    Calendar(id="set_date_calendar", on_click=on_date_selected),  # type: ignore
    Row(SwitchTo(I18N("COMMON_BTN_BACK"), id="to_dr", state=ChangeStates.date_room), BTN_BLANK),
    state=ChangeStates.date,
    getter=meeting_info_getter,
)


set_time_ww = Window(
    I18N("CHANGE_SET_TIME_PROMPT"),
    MessageInput(get_meeting_time),
    Row(
        SwitchTo(text=I18N("COMMON_BTN_BACK"), id="to_date", state=ChangeStates.date, on_click=handle_clear),
        BTN_BLANK,
    ),
    state=ChangeStates.time,
    getter=meeting_info_getter,
)


set_duration_ww = Window(
    I18N("CHANGE_SET_DURATION_PROMPT"),
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_meeting_duration),
    state=ChangeStates.duration,
    getter=meeting_info_getter,
)


assign_tutor_ww = Window(
    I18N("CHANGE_ASSIGN_TUTOR_TITLE"),
    TUTORS_ASSIGN_SCROLLING_GROUP,
    Row(BTN_INIT, BTN_BLANK),
    MessageInput(get_assigned_tutor),
    state=ChangeStates.tutor,
    getter=meeting_info_with_tutors_getter,
)
