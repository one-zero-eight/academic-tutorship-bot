import re
from types import ModuleType

from aiogram.types import BotCommand
from pydantic import TypeAdapter

commands_type_adapter = TypeAdapter(list[BotCommand])


def check_commands_equality(x: list[BotCommand], y: list[BotCommand]) -> bool:
    return commands_type_adapter.dump_json(x) == commands_type_adapter.dump_json(y)


def get_windows(module: ModuleType):
    """
    Returns a dictionary of variables from the given module that match the pattern:
    .*_ww (i.e., anything ending with '_ww')
    """
    pattern = re.compile(r"^.*_ww$")
    result = []
    for name, value in vars(module).items():
        if pattern.match(name):
            result.append(value)
    return result
