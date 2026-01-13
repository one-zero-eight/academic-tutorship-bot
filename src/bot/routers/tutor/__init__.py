from aiogram_dialog import Dialog

from src.bot.filters import *
from src.bot.middlewares import AuthGuardMiddleware
from src.bot.utils import get_windows
from src.domain.models import *

from . import windows
from .states import *

router = Dialog(*get_windows(windows))

auth_guard_middleware = AuthGuardMiddleware()
router.message.middleware(auth_guard_middleware)
router.callback_query.middleware(auth_guard_middleware)
