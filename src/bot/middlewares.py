import asyncio
import inspect
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, Message, TelegramObject
from email_validator import validate_email
from email_validator.exceptions import EmailNotValidError

from src.accounts_sdk import inh_accounts
from src.bot.dialog_extension.extended_fsm_context import extend_fsm_context
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import UserStatus
from src.bot.logging_ import log_debug, logger
from src.db.repositories import student_repo, tutor_repo


# noinspection PyMethodMayBeStatic
class LogAllEventsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        r = await handler(event, data)
        finish_time = loop.time()
        duration = finish_time - start_time
        try:
            # get to `aiogram.dispatcher.event.TelegramEventObserver.trigger` method
            frame = inspect.currentframe()
            frame_info = inspect.getframeinfo(frame)
            while frame is not None:
                if frame_info.function == "trigger":
                    _handler = frame.f_locals.get("handler")
                    if _handler is not None:
                        _handler: HandlerObject
                        record = self._create_log_record(_handler, event, data, duration=duration)
                        logger.handle(record)
                    break
                frame = frame.f_back
                frame_info = inspect.getframeinfo(frame)
        finally:
            del frame
        return r

    def _create_log_record(
        self, handler: HandlerObject, event: TelegramObject, data: dict[str, Any], *, duration: float | None = None
    ) -> logging.LogRecord:
        callback = handler.callback
        func_name = callback.__name__
        pathname = inspect.getsourcefile(callback)
        lineno = inspect.getsourcelines(callback)[1]

        event_type = type(event).__name__
        if hasattr(event, "from_user"):
            username = event.from_user.username
            user_string = f"User @{username}<{event.from_user.id}>" if username else f"User <{event.from_user.id}>"
        else:
            user_string = "User <unknown>"

        if isinstance(event, Message):
            if event.text is not None:
                message_text = f"{event.text[:50]}..." if len(event.text) > 50 else event.text
            else:
                message_text = "no-text"
            msg = f"{user_string}: [{event_type}] `{message_text}`"
        elif isinstance(event, CallbackQuery):
            msg = f"{user_string}: [{event_type}] `{event.data}`"
        else:
            msg = f"{user_string}: [{event_type}]"

        if duration is not None:
            msg = f"Handler `{func_name}` took {int(duration * 1000)} ms: {msg}"

        record = logging.LogRecord(
            name="src.bot.middlewares.LogAllEventsMiddleware",
            level=logging.INFO,
            pathname=pathname,
            lineno=lineno,
            msg=msg,
            args=(),
            exc_info=None,
            func=func_name,
        )
        record.relativePath = os.path.relpath(record.pathname)
        return record


class AutoAuthMiddleware(LogAllEventsMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["authenticated"] = await self._update_authenticated(event, data)
        data["status"] = await self._update_status(event, data)
        return await super().__call__(handler, event, data)

    async def _update_authenticated(self, event: TelegramObject, data: dict[str, Any]) -> bool:
        (was_auth, become_auth) = (False, False)  # for _log_authenticated()
        state: FSMContext = extend_fsm_context(data["state"])
        chat: Chat = data["event_chat"]
        # authenticated = was_auth = await state.get_value("authenticated", False)
        authenticated = False
        if not authenticated:
            user = await inh_accounts.get_user(telegram_id=chat.id)
            if user is not None:
                authenticated = become_auth = True
                assert (tg := user.telegram_info)
                assert (inno := user.innopolis_info)
                if not await student_repo.exists(telegram_id=tg.id):
                    self_student = await student_repo.create(
                        telegram_id=tg.id,
                        first_name=tg.first_name,
                        last_name=tg.last_name,
                        username=tg.username,
                        email_=inno.email,
                    )
                else:
                    self_student = await student_repo.get(telegram_id=tg.id)
                await state.set_self_student(self_student)
            await state.update_data({"authenticated": authenticated})
        self._log_authenticated(chat, was_auth, become_auth)
        return authenticated

    def _log_authenticated(self, chat: Chat, was_auth: bool, become_auth: bool):
        if was_auth:
            return log_debug("auth.was_authenticated", user_id=chat.id)
        elif become_auth:
            return log_debug("auth.became_authenticated", user_id=chat.id)
        else:
            return log_debug("auth.failed_to_authenticate", user_id=chat.id)

    async def _update_status(self, event: TelegramObject, data: dict[str, Any]) -> UserStatus:
        state: FSMContext = data["state"]
        chat: Chat = data["event_chat"]

        if await tutor_repo.exists(chat.id):
            status = UserStatus.tutor
            self_tutor = await tutor_repo.get(telegram_id=chat.id)
            await state.update_data({"self_tutor": self_tutor.model_dump()})
        else:
            status = UserStatus.student
        if await student_repo.is_admin(chat.id):
            status = UserStatus.admin
        await state.update_data({"status": status})
        return status


class AuthGuardMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        chat: Chat = data["event_chat"]
        authenticated = data.get("authenticated", False)
        if not authenticated:
            log_debug("auth.unauthenticated", user_id=chat.id)
            raise UnauthenticatedException
        return await handler(event, data)


class MockAutoAuthMiddleware(AutoAuthMiddleware):
    async def _update_authenticated(self, event: TelegramObject, data: dict[str, Any]) -> bool:
        (was_auth, become_auth) = (False, False)  # for _log_authenticated()
        state: FSMContext = extend_fsm_context(data["state"])
        chat: Chat = data["event_chat"]
        bot: Bot = data["bot"]
        # authenticated = was_auth = await state.get_value("authenticated", False)
        authenticated = False
        if not authenticated:
            if await student_repo.exists(telegram_id=chat.id):
                authenticated = was_auth = True
                self_student = await student_repo.get(telegram_id=chat.id)
                await state.set_self_student(self_student)
            else:
                if isinstance(event, Message) and self.__entered_innopolis_email(event):
                    assert (email := event.text)
                    if await student_repo.exists(email_=email):
                        await bot.send_message(chat.id, "Student with this email already authenticated, enter another")
                    else:
                        self_student = await student_repo.create(
                            telegram_id=chat.id,
                            first_name=chat.first_name,
                            last_name=chat.last_name,
                            username=chat.username,
                            email_=email,
                        )
                        authenticated = become_auth = True
                        await state.set_self_student(self_student)
                else:
                    log_debug("mock_auth.ask_email", chat_id=chat.id)
                    await bot.send_message(chat.id, "Enter your innopolis email to authenticate")
            await state.update_data({"authenticated": authenticated})
        self._log_authenticated(chat, was_auth, become_auth)
        if become_auth:
            log_debug("mock_auth.success", chat_id=chat.id)
            await bot.send_message(chat.id, "Authenticated succescfully, now use /start again")
        return authenticated

    def __entered_innopolis_email(self, event: Message) -> bool:
        VALID_DOMAINS = ["innopolis.university", "innopolis.ru"]
        if event.text:
            try:
                email = validate_email(event.text)
                if email.domain in VALID_DOMAINS:
                    return True
            except EmailNotValidError:
                return False
        return False
