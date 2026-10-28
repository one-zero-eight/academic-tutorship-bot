from src.bot.dialog_extension import StatusGuard, StatusGuardedDialog
from src.bot.middlewares import AuthGuardMiddleware
from src.bot.utils import get_windows
from src.domain.models import UserStatus as US

from . import windows
from .states import *

dialog = StatusGuardedDialog(*get_windows(windows), guard=StatusGuard((US.tutor, US.admin)))

auth_guard_middleware = AuthGuardMiddleware()
dialog.message.middleware(auth_guard_middleware)
dialog.callback_query.middleware(auth_guard_middleware)
