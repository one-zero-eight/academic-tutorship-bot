from aiogram.filters import Command
from aiogram_dialog import Dialog

from src.bot.filters import *
from src.domain.models import *

from . import windows
from .handles import *
from .states import *
from .utils import get_windows

router = Dialog(*get_windows(windows))

router.message.register(open_menu, Command("admin"), StatusFilter("admin"))
