from aiogram import Bot, F, Router, types
from aiogram.filters import Command, CommandStart, ExceptionTypeFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BotCommandScopeChat,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram_dialog import DialogManager, StartMode

from src.accounts_sdk import inh_accounts
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import StatusFilter
from src.bot.routers.admin import AdminStates
from src.bot.routers.authentication import AuthStates
from src.bot.routers.student import StudentStates
from src.config import settings
from src.db.repositories import tutors_repo
from src.domain.enums import UserStatus as US

router = Router(name="commands")


class CmdStates(StatesGroup):
    add_tutor = State("add_tutor")


MATCHING_START_STATE = {
    US.student: StudentStates.start,
    # US.tutor: TutorStates.start,
    US.admin: AdminStates.start,
}


@router.message(CommandStart())
@router.error(ExceptionTypeFilter(UnauthenticatedException))
async def on_start(
    message: types.Message, state: FSMContext, dialog_manager: DialogManager, authenticated: bool, status: US
):
    if not authenticated:
        return await dialog_manager.start(AuthStates.bind_tg_inh)
    else:
        return await dialog_manager.start(MATCHING_START_STATE[status])


@router.message(Command("admin"), StatusFilter(US.admin))
async def enable_admin_mode(message: types.Message, bot: Bot, dialog_manager: DialogManager):
    text = "You are the Admin!"
    await message.answer(text)
    await bot.set_my_commands(
        settings.bot_commands
        or []
        + [
            types.BotCommand(command="admin", description="Enable admin mode"),
        ],
        scope=BotCommandScopeChat(chat_id=message.chat.id),
    )
    await dialog_manager.start(AdminStates.start, mode=StartMode.RESET_STACK)


@router.message(Command("admin"), ~StatusFilter(US.admin))
async def failed_enable_admin_mode(message: types.Message, bot: Bot):
    text = "You are not the Admin!"
    await message.answer(text)
    await bot.set_my_commands(
        settings.bot_commands or [],
        scope=BotCommandScopeChat(chat_id=message.chat.id),
    )


@router.message(Command("testapi"), StatusFilter(US.admin))
async def test_accounts_api(message: types.Message, dialog_manager: DialogManager):
    inh_user = await inh_accounts.get_user(telegram_id=message.chat.id)
    if inh_user is None:
        await message.answer("You're not found :(")
    else:
        await message.answer(f"Your inh id: {inh_user.id}")


@router.message(Command("list_tutors"), StatusFilter(US.admin))
async def admin_list_tutors(message: types.Message):
    tutors = await tutors_repo.list()
    text = "Tutors:\n"
    text += "\n".join(f"[{t.tg_id}] @{t.username}" for t in tutors)
    await message.answer(text)


_req_users = KeyboardButtonRequestUsers(
    request_id=1,
    user_is_bot=False,
    max_quantity=1,
    request_name=True,
    request_username=True,
)

_add_tutor_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Share user", request_users=_req_users)]])


@router.message(Command("add_tutor"), StatusFilter(US.admin))
async def admin_add_tutor_init(message: types.Message, state: FSMContext):
    await message.answer(text="Share any user by pressing the button", reply_markup=_add_tutor_kb)
    await state.set_state(CmdStates.add_tutor)


_remove_kb = ReplyKeyboardRemove(remove_keyboard=True)


@router.message(StateFilter(CmdStates.add_tutor), F.users_shared, StatusFilter(US.admin))
async def admin_add_tutor_end(message: types.Message, state: FSMContext):
    if message.users_shared is None:
        return await message.answer("Share any user by pressing the button")
    await state.clear()
    shared_user = message.users_shared.users[0]
    if await tutors_repo.exists(tg_id=shared_user.user_id):
        return await message.answer("User is already a tutor", reply_markup=_remove_kb)
    tutor = await tutors_repo.create(
        tg_id=shared_user.user_id,
        username=shared_user.username,
        first_name=shared_user.first_name,
        last_name=shared_user.last_name,
    )
    return await message.answer(f"New tutor added (id={tutor.id})", reply_markup=_remove_kb)


@router.message(Command("rm_tutor"), StatusFilter(US.admin))
async def admin_rm_tutor(message: types.Message, bot: Bot):
    id_or_username = _extract_id_username(message.text)
    if not id_or_username:
        return await message.answer("Provide id or @username")
    tg_id = id_or_username if isinstance(id_or_username, int) else None
    username = id_or_username if isinstance(id_or_username, str) else None
    if not await tutors_repo.exists(tg_id=tg_id, username=username):
        return await message.answer("User is already not a tutor")
    tutor = await tutors_repo.remove(tg_id=tg_id, username=username)
    return await message.answer(f"Tutor removed (id={tutor.id})")


def _extract_id_username(text: str | None) -> str | int | None:
    if text is not None:
        text = " ".join(text.split()[1:])  # remove /command
        text = text.strip()
        if text.isnumeric():
            return int(text)  # id
        elif ("@" in text) and (" " not in text) and (len(text) > 0):
            return text.replace("@", "")  # username
    return None
