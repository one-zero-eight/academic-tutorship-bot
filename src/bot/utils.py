import re
from datetime import time
from types import ModuleType

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    Message,
    ReplyKeyboardMarkup,
)
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from pydantic import TypeAdapter

from src.bot import bot_container
from src.config import settings
from src.domain.models import Meeting, UserStatus

commands_type_adapter = TypeAdapter(list[BotCommand])


def check_commands_equality(x: list[BotCommand], y: list[BotCommand]) -> bool:
    return commands_type_adapter.dump_json(x) == commands_type_adapter.dump_json(y)


def get_windows(module: ModuleType):
    """
    Returns a dictionary of variables from the given module that match the pattern:
    .*_ww (i.e., anything ending with '_ww')
    """
    pattern = re.compile(r"^.*_ww$")
    result = []
    for name, value in vars(module).items():
        if pattern.match(name):
            result.append(value)
    return result


def get_state(dialog_manager: DialogManager) -> FSMContext:
    # NOTE: the "state" key must always exist in middleware_data
    return dialog_manager.middleware_data["state"]


async def clear_messages(dialog_manager: DialogManager):
    """Delete tracked messages ("to_delete_id" in state)"""
    bot: Bot = dialog_manager.middleware_data["bot"]
    chat: Chat = dialog_manager.middleware_data["event_chat"]
    state = get_state(dialog_manager)
    if to_delete_id := await state.get_value("to_delete_id"):
        try:
            await bot.delete_message(chat.id, to_delete_id)
            await state.update_data({"to_delete_id": None})
        except Exception as e:
            return print(f"clear_messages failed, due to {e}")


async def track_message(message: Message, dialog_manager: DialogManager):
    """Track messages to delete later ("to_delete_id" in state)"""
    await get_state(dialog_manager).update_data({"to_delete_id": message.message_id})


async def handle_clear(query: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if not query.bot:
        raise ValueError("No query.bot")
    if not query.message:
        raise ValueError("No query.message")
    await clear_messages(dialog_manager)


request_users = KeyboardButtonRequestUsers(
    request_id=0,
    user_is_bot=False,
    request_username=True,
    request_name=True,
    max_quantity=1,
)

CHOOSE_USER_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Choose User 👤", request_users=request_users)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

del request_users


async def user_status_getter(dialog_manager: DialogManager, **kwargs):
    state = get_state(dialog_manager)
    status: UserStatus | None = await state.get_value("status")
    return {
        "is_admin": (status == UserStatus.admin),
        "is_tutor": (status == UserStatus.tutor),
        "is_student": (status == UserStatus.student),
    }


_time_pattern = re.compile(r"[0-2][0-9][:. ][0-5][0-9]")


def parse_time(text: str) -> time:
    text = text.strip()
    if not re.fullmatch(_time_pattern, text):
        raise ValueError("Invalid time format")
    hour = int(text[:2])
    minute = int(text[3:])
    if not (0 <= hour <= 23):
        raise ValueError("Hours not in range [0, 23]")
    if not (0 <= minute <= 59):
        raise ValueError("Minutes not in range [0, 59]")
    return time(hour, minute)


async def send_to_admins(meeting: Meeting, text: str, **kwargs):
    bot = bot_container.get_bot()
    whom_to_send = settings.admins
    whom_to_send = list(set(whom_to_send))  # remove duplicates

    for tg_id in whom_to_send:
        try:
            await bot.send_message(chat_id=tg_id, text=text, **kwargs)
        except Exception as e:
            print(f"Could not send message to [{tg_id}], {e}")


async def send_to_tutor(meeting: Meeting, text: str, **kwargs):
    bot = bot_container.get_bot()
    if not meeting.tutor:
        raise ValueError("No meeting.tutor")
    tg_id = meeting.tutor.tg_id
    try:
        await bot.send_message(chat_id=tg_id, text=text, **kwargs)
    except Exception as e:
        print(f"Could not send message to [{tg_id}], {e}")


async def send_to_admins_and_tutor(meeting: Meeting, text: str, **kwargs):
    bot = bot_container.get_bot()
    whom_to_send = settings.admins
    if meeting.tutor:
        whom_to_send.append(meeting.tutor.tg_id)
    whom_to_send = list(set(whom_to_send))  # remove duplicates

    for tg_id in whom_to_send:
        try:
            await bot.send_message(chat_id=tg_id, text=text, **kwargs)
        except Exception as e:
            print(f"Could not send message to [{tg_id}], {e}")


def create_attendance_sending_kb(meeting: Meeting) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Send Attendance File", callback_data=f"open-send-attendance_{meeting.id}")]
        ]
    )
