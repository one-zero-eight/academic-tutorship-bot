from src.bot.dialog_extension import StatusGuard, StatusGuardedDialog
from src.bot.filters import *
from src.bot.utils import get_windows
from src.domain.models import *

from . import windows
from .states import *

dialog = StatusGuardedDialog(*get_windows(windows), guard=StatusGuard((UserStatus.admin,)))
