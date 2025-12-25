from typing import Literal

from aiogram.types import CallbackQuery, Message, SharedUser
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from .getters import *
from .keyboards import *
from .states import *
from .utils import *


async def open_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def open_meetings_type_choice(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.meetings_type)


def open_meetings_list_of_type(type: Literal["created", "announced", "closed"]):
    """Higher order function, returns Awaitable that opens specified meetings list"""

    async def open_meetings_list(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
        dialog_manager.dialog_data.update({"meetings_type": type})
        await dialog_manager.switch_to(AdminStates.meetings_list)

    return open_meetings_list


async def open_meeting_create(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_meeting)


async def open_admin_menu(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


async def open_meeting_info(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot or not button.widget_id:
        return
    await clear_messages(query.bot, dialog_manager)
    if button.widget_id.startswith("a_meeting"):
        meeting_id = int(button.widget_id.replace("a_meeting_", ""))  # type: ignore
        dialog_manager.dialog_data.update({"meeting": [x for x in TEST_MEETINGS if x.id == meeting_id][0]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def get_new_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        return
    TEST_MEETINGS.append(Meeting(id=len(TEST_MEETINGS) + 1, title=message.text))
    dialog_manager.dialog_data.update({"meeting": TEST_MEETINGS[-1]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def on_meeting_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    # TODO : add database fetch data here
    meeting = TEST_MEETINGS[int(item_id)]

    dialog_manager.dialog_data.update({"meeting": meeting})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def open_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        return
    to_delete = await query.message.answer(text="Click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)
    dialog_manager.dialog_data.update({"to_delete": to_delete})
    await dialog_manager.switch_to(AdminStates.assign_tutor)


async def open_set_title(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_title)


async def open_set_description(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_description)


async def open_set_date(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_date)


async def open_set_duration(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.set_duration)


async def get_assigned_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.users_shared or not message.bot:
        return
    await clear_messages(message.bot, dialog_manager)

    tutor = message.users_shared.users[0]
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")

    dialog_manager.dialog_data.update({"tutor": tutor})

    if not isinstance(meeting, Meeting):
        raise Exception("No meeting in get_assigned_tutor wtf?")
    if not isinstance(tutor, SharedUser):
        raise Exception("No tutor in get_assigned_tutor wtf?")
    # TODO : changes to database
    meeting.tutor_id = tutor.user_id
    meeting.tutor_username = tutor.username

    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_title(message: Message, _: MessageInput, dialog_manager: DialogManager):
    # TODO : proper error handeling
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")
    if not meeting or not message.text:
        return
    meeting.title = message.text
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_description(message: Message, _: MessageInput, dialog_manager: DialogManager):
    # TODO : proper error handeling
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")
    if not meeting or not message.text:
        return
    meeting.description = message.text
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_date(message: Message, _: MessageInput, dialog_manager: DialogManager):
    # TODO : proper error handeling
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")
    if not meeting or not message.text:
        return
    try:
        meeting.date = int(datetime.strptime(message.text, "%d.%m.%Y").timestamp())
    except Exception:
        return
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def get_meeting_duration(message: Message, _: MessageInput, dialog_manager: DialogManager):
    # TODO : proper error handeling
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")
    if not meeting or not message.text:
        return
    try:
        minutes, seconds = map(int, message.text.split(":"))
        meeting.duration = (minutes * 60 + seconds) * 60
    except Exception:
        return
    await message.delete()
    await dialog_manager.switch_to(AdminStates.meeting_change, show_mode=ShowMode.DELETE_AND_SEND)


async def on_tutor_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    tutor = await tutors_repo.get(id=int(item_id))
    dialog_manager.dialog_data.update({"tutor": tutor})
    await dialog_manager.switch_to(AdminStates.tutor_info)


async def on_remove_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    data = dialog_manager.dialog_data
    tutor: Tutor = data["tutor"]
    await tutors_repo.remove(tutor=tutor)
    await query.answer(f"@{tutor.username} is no longer a Tutor", show_alert=True)
    await dialog_manager.switch_to(AdminStates.tutors_list)


async def open_add_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        return
    to_delete = await query.message.answer(text="Click the button to choose a user 👇", reply_markup=CHOOSE_USER_KB)
    dialog_manager.dialog_data.update({"to_delete": to_delete})
    await dialog_manager.switch_to(AdminStates.add_tutor)


async def get_added_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.users_shared or not message.bot:
        return
    await clear_messages(message.bot, dialog_manager)

    shared_user = message.users_shared.users[0]
    if not isinstance(shared_user, SharedUser):
        raise Exception("No tutor in get_added_tutor wtf?")

    if shared_user.username is None:
        to_delete = await message.answer(text="Tutor must have a username ⚠️", reply_markup=CHOOSE_USER_KB)
        dialog_manager.dialog_data.update({"to_delete": to_delete})
        return await dialog_manager.switch_to(AdminStates.add_tutor, show_mode=ShowMode.DELETE_AND_SEND)

    if await tutors_repo.exists(tg_id=shared_user.user_id):
        to_delete = await message.answer(text="User is already a Tutor ⚠️", reply_markup=CHOOSE_USER_KB)
        dialog_manager.dialog_data.update({"to_delete": to_delete})
        return await dialog_manager.switch_to(AdminStates.add_tutor, show_mode=ShowMode.DELETE_AND_SEND)

    tutor = await tutors_repo.create(
        tg_id=shared_user.user_id,
        username=shared_user.username,
        first_name=shared_user.first_name,
        last_name=shared_user.last_name,
    )
    dialog_manager.dialog_data.update({"tutor": tutor})

    await dialog_manager.switch_to(AdminStates.tutor_info, show_mode=ShowMode.DELETE_AND_SEND)


async def open_tutors_list_with_clear(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot or not button.widget_id:
        return
    await clear_messages(query.bot, dialog_manager)
    await dialog_manager.switch_to(AdminStates.tutors_list)
