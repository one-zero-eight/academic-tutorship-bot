from time import perf_counter

from aiogram import Bot, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage  # type: ignore
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

from src.bot import bot_container
from src.bot.dispatcher import CustomDispatcher
from src.bot.logging_ import logger
from src.bot.middlewares import AutoAuthMiddleware
from src.bot.utils import check_commands_equality
from src.config import settings
from src.db.repositories import admin_repo, db
from src.notifications import init_handlers, notification_manager
from src.scheduling.scheduler import scheduler

_time1 = perf_counter()

bot = Bot(token=settings.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot_container.set_bot(bot)  # NOTE: needed to use bot in lower layers

if settings.redis_url:
    storage = RedisStorage.from_url(
        settings.redis_url.get_secret_value(), key_builder=DefaultKeyBuilder(with_destiny=True)
    )
    logger.info("Using Redis storage")
else:
    storage = MemoryStorage()
    logger.info("Using Memory storage")

dp = CustomDispatcher(storage=storage)

auto_auth_middleware = AutoAuthMiddleware()
if settings.mock_auth:
    # Using mock authentication to bypass InNoHassle Accounts (for testing)
    from src.bot.middlewares import MockAutoAuthMiddleware

    auto_auth_middleware = MockAutoAuthMiddleware()

dp.message.middleware(auto_auth_middleware)
dp.callback_query.middleware(auto_auth_middleware)
dp.error.middleware(auto_auth_middleware)


@dp.error(ExceptionTypeFilter(UnknownIntent), F.update.callback_query.as_("callback_query"))
async def unknown_intent_handler(event: ErrorEvent, callback_query: types.CallbackQuery):
    await callback_query.answer("Unknown intent: Please, try to restart the action.")


@dp.error(ExceptionTypeFilter(UnknownState))
async def on_unknown_state(event: ErrorEvent, state: FSMContext, dialog_manager: DialogManager):
    logger.warning("Messed up dialog: %s", event.exception)
    await state.clear()
    await dialog_manager.reset_stack()
    raise SkipHandler()


from src.bot.dialogs.attendance import dialog as attendance_dialog  # noqa: E402
from src.bot.dialogs.authentication import dialog as authentication_dialog  # noqa: E402
from src.bot.dialogs.change_meeting import dialog as change_meeting_dialog  # noqa: E402
from src.bot.dialogs.discipline_picker import dialog as discipline_picker_dialog  # noqa: E402
from src.bot.dialogs.guide import dialog as guide_dialog  # noqa: E402
from src.bot.dialogs.meetings import dialog as meetings_dialog  # noqa: E402
from src.bot.dialogs.root import dialog as root_dialog  # noqa: E402
from src.bot.dialogs.student_meetings import dialog as student_meetings_dialog  # noqa: E402
from src.bot.dialogs.tutors import dialog as tutors_dialog  # noqa: E402
from src.bot.dialogs.tutors_profile import dialog as tutors_profile_dialog  # noqa: E402
from src.bot.routers.commands import router as commands_router  # noqa: E402
from src.bot.routers.queries import router as queries_router  # noqa: E402

# non dialog handlers
dp.include_router(commands_router)  # start, help, menu commands
dp.include_router(queries_router)  # callback handles for notification messages

# separate functional dialogs
dp.include_router(root_dialog)
dp.include_router(authentication_dialog)
dp.include_router(meetings_dialog)
dp.include_router(discipline_picker_dialog)
dp.include_router(student_meetings_dialog)
dp.include_router(change_meeting_dialog)
dp.include_router(tutors_dialog)
dp.include_router(tutors_profile_dialog)
dp.include_router(attendance_dialog)
dp.include_router(guide_dialog)

setup_dialogs(dp)


@dp.startup()
async def on_startup():
    logger.info("Bot starting...")
    init_handlers()
    # Set bot name, description and commands
    scope = types.BotCommandScopeAllPrivateChats()
    existing_bot = {
        "name": (await bot.get_my_name()).name,
        "description": (await bot.get_my_description()).description,
        "shortDescription": (await bot.get_my_short_description()).short_description,
        "commands": await bot.get_my_commands(scope=scope),
        "username": (await bot.me()).username,
    }
    if settings.bot_name and existing_bot["name"] != settings.bot_name:
        _ = await bot.set_my_name(settings.bot_name)
        logger.info(f"Bot name updated. Success {_}")
    if settings.bot_description and existing_bot["description"] != settings.bot_description:
        _ = await bot.set_my_description(settings.bot_description)
        logger.info(f"Bot description updated. Success: {_}")
    if settings.bot_short_description and existing_bot["shortDescription"] != settings.bot_short_description:
        _ = await bot.set_my_short_description(settings.bot_short_description)
        logger.info(f"Bot short description updated. Succes: {_}")
    if settings.bot_commands and not check_commands_equality(existing_bot["commands"], settings.bot_commands):
        logger.info(f"Was: {existing_bot['commands']}; New: {settings.bot_commands}")
        _ = await bot.set_my_commands(settings.bot_commands, scope=scope)
        logger.info(f"Bot commands updated. Success: {_}.")
    logger.info(f"Bot started https://t.me/{existing_bot['username']} in {perf_counter() - _time1:.2f} sec.")

    # Set bots usernames in notification_manager
    await notification_manager.load_notification_bot_username()
    notification_manager.set_control_bot_username(existing_bot["username"])

    logger.info("Starting Scheduler...")
    scheduler.start()
    logger.info("Starting Notification Bot Polling...")
    await notification_manager.start_polling()
    logger.info("Sending startup notification...")
    await notification_manager.send_bot_started()
    logger.info("Syncing admins with config...")
    added, removed = await admin_repo.sync_with_config(settings.admins)
    logger.info(f"Admins synced, added: {added}, removed: {removed}")


@dp.shutdown()
async def on_shutdown():
    logger.info("Bot shutting down...")
    logger.info("Sending shutdown notification...")
    await notification_manager.send_bot_shutdown()
    logger.info("Stopping Notification Bot Polling...")
    await notification_manager.stop_polling()
    logger.info("Shutting down Scheduler...")
    scheduler.shutdown()
    logger.info("Disposing Repository...")
    await db.dispose()


async def main():
    # Drop pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    # Start long-polling
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.storage.close()
        await bot.session.close()
        await notification_manager._bot.session.close()
