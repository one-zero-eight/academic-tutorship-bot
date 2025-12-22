import asyncio
import inspect
import logging
import os
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, Message, TelegramObject

from src.bot.accounts_sdk import inh_accounts
from src.bot.exceptions import UnauthenticatedException
from src.bot.filters import UserStatus
from src.bot.logging_ import logger
from src.config import settings


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
        data["authenticated"] = await self._update_authenticated(data)
        data["status"] = await self._update_status(data)
        return await super().__call__(handler, event, data)

    async def _update_authenticated(self, data: dict[str, Any]) -> bool:
        (was_auth, become_auth) = (False, False)  # for _log_authenticated()
        state: FSMContext = data["state"]
        chat: Chat = data["event_chat"]
        authenticated = was_auth = await state.get_value("authenticated", False)
        if not authenticated:
            user = await inh_accounts.get_user(telegram_id=chat.id)
            if user is not None:
                authenticated = become_auth = True
            await state.update_data({"authenticated": authenticated})
        self._log_authenticated(chat, was_auth, become_auth)
        return authenticated

    def _log_authenticated(self, chat: Chat, was_auth: bool, become_auth: bool):
        if was_auth:
            return logger.info(f"[{chat.id}] was authenticated")
        elif become_auth:
            return logger.info(f"[{chat.id}] become auto authenticated")
        else:
            return logger.info(f"[{chat.id}] failed to auto authenticate")

    async def _update_status(self, data: dict[str, Any]) -> UserStatus:
        state: FSMContext = data["state"]
        chat: Chat = data["event_chat"]
        status = await state.get_value("status")
        if status is None:
            if chat.id in settings.admins:
                status = UserStatus.admin
            elif False:  # TODO: add tutors check
                status = UserStatus.tutor
            else:
                status = UserStatus.student
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
            logger.info(f"[{chat.id}] un authenticated")
            raise UnauthenticatedException
        return await handler(event, data)
