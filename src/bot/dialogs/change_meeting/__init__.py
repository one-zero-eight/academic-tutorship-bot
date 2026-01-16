from aiogram_dialog import Dialog

from src.bot.middlewares import AuthGuardMiddleware
from src.bot.utils import get_windows

from . import windows
from .states import *

dialog = Dialog(*get_windows(windows))

auth_guard_middleware = AuthGuardMiddleware()
dialog.message.middleware(auth_guard_middleware)
dialog.callback_query.middleware(auth_guard_middleware)
