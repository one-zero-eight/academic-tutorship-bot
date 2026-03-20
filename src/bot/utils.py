import csv
import io
import re
from datetime import time
from types import ModuleType
from typing import Literal

from aiogram.types import (
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
)
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from email_validator import EmailNotValidError, validate_email
from pydantic import TypeAdapter

from src.bot.dialog_extension import extend_dialog
from src.domain.models import Meeting, UserStatus

commands_type_adapter = TypeAdapter(list[BotCommand])


BLANK_BTN = Button(Const(" "), id="blank")


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


async def handle_clear(query: CallbackQuery, button: Button, manager: DialogManager):
    manager = extend_dialog(manager)
    await manager.clear_messages()


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
    dialog_manager = extend_dialog(dialog_manager)
    status: UserStatus | None = await dialog_manager.state.get_value("status")
    self_tutor = await dialog_manager.state.get_value("self_tutor", None)
    return {
        "is_admin": (status == UserStatus.admin),
        "is_not_admin": (status != UserStatus.admin),
        "is_tutor": (self_tutor is not None),
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


def create_attendance_sending_kb(meeting: Meeting) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Send Attendance File", callback_data=f"open-send-attendance_{meeting.id}")]
        ]
    )


DELETE_WARNING_KB = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Delete Warning", callback_data="delete_warning")]]
)


def parse_attendance(content: str) -> list[str]:
    match _determine_attendance_type(content):
        case "moodle":
            return _parse_attendance_csv(content)
        case "raw":
            return _parse_attendance_csv(content)
        case "txt":
            return _parse_attendance_txt(content)
        case _:
            raise ValueError("Unknown attendance file type")


def _determine_attendance_type(content: str) -> Literal["moodle", "raw", "txt"]:
    lines = content.split("\n")
    if lines[0] == "External user field,status":
        return "moodle"
    elif lines[0] == "email,stage,time,manual":
        return "raw"
    elif _is_email(lines[0]):
        return "txt"
    else:
        raise ValueError("Unknown attendance file type")


def _is_email(text: str) -> bool:
    try:
        validate_email(text)
        return True
    except EmailNotValidError:
        return False


def _parse_attendance_csv(content: str) -> list[str]:
    attendance = []
    content_io = io.StringIO(content)
    reader = csv.reader(content_io)
    for row in reader:
        if _is_email(row[0]):
            attendance.append(str(row[0]))
    return attendance


def _parse_attendance_txt(content: str) -> list[str]:
    attendance = []
    for line in content.split("\n"):
        if _is_email(line):
            attendance.append(str(line))
    return attendance
