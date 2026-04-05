from aiogram_dialog import Dialog

from src.bot.filters import *
from src.bot.utils import get_windows
from src.domain.models import *

from . import windows
from .states import *

dialog = Dialog(*get_windows(windows))
