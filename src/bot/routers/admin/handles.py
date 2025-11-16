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
    await dialog_manager.start(AdminStates.menu, mode=StartMode.RESET_STACK)


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
    await dialog_manager.start(AdminStates.menu, mode=StartMode.RESET_STACK)


async def open_meeting_info(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    print("SHEEE", button)
    if not query.bot or not button.widget_id:
        return
    await clear_messages(query.bot, dialog_manager)
    if button.widget_id.startswith("a_meeting"):
        meeting_id = int(button.widget_id.replace("a_meeting_", ""))  # type: ignore
        dialog_manager.dialog_data.update({"meeting": [x for x in TEST_MEETINGS if x.id == meeting_id][0]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def get_title_of_meeting(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.text:
        return
    TEST_MEETINGS.append(Meeting(id=len(TEST_MEETINGS) + 1, title=message.text))
    dialog_manager.dialog_data.update({"meeting": TEST_MEETINGS[-1]})
    await dialog_manager.switch_to(AdminStates.meeting_info)


async def open_assign_tutor(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.message:
        return
    to_delete = await query.message.answer(text="Click the button to choose a User 👇", reply_markup=CHOOSE_USER_KB)
    dialog_manager.dialog_data.update({"to_delete": to_delete})
    await dialog_manager.switch_to(AdminStates.assign_tutor)


async def get_assigned_tutor(message: Message, _: MessageInput, dialog_manager: DialogManager):
    if not message.users_shared or not message.bot:
        return
    await clear_messages(message.bot, dialog_manager)
    tutor = message.users_shared.users[0]
    dialog_manager.dialog_data.update({"tutor": tutor})
    await dialog_manager.switch_to(AdminStates.confirm_tutor, show_mode=ShowMode.DELETE_AND_SEND)


async def confirm_tutor_open_meeting_info(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    meeting: Meeting | None = dialog_manager.dialog_data.get("meeting")
    tutor: SharedUser | None = dialog_manager.dialog_data.get("tutor")
    if not isinstance(meeting, Meeting):
        raise Exception("No meeting in confirm_tutor wtf?")
    if not isinstance(tutor, SharedUser):
        raise Exception("No tutor in confirm_tutor wtf?")

    # TODO : changes to database
    meeting.tutor_id = tutor.user_id
    meeting.tutor_username = tutor.username

    await dialog_manager.switch_to(AdminStates.meeting_info)


async def on_meeting_selected(query: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str):
    # TODO : add database fetch data here
    meeting = TEST_MEETINGS[int(item_id)]

    dialog_manager.dialog_data.update({"meeting": meeting})
    await dialog_manager.switch_to(AdminStates.meeting_info)
