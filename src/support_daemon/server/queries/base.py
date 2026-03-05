import shlex
from abc import ABC, abstractmethod
from typing import Any


class Query(ABC):
    name: str = "Base"
    "Name of query"
    args_dict: dict[str, Any]
    "Argument names with default values"

    @classmethod
    @abstractmethod
    def _prepare_args(cls, data: dict) -> dict:
        """Updates raw data recieved from _parse_args(),
        by setting required types and other things
        """
        ...

    @abstractmethod
    async def run(self) -> str: ...

    @classmethod
    def parse(cls, str_query: str) -> "Query":
        args = shlex.split(str_query)[1:]
        data = cls._parse_args(args)
        data = cls._prepare_args(data)
        return cls(**data)

    @classmethod
    def _parse_args(cls, args: list[str]) -> dict:
        data = cls.args_dict
        for arg in args:
            split = arg.split("=")
            if len(split) != 2:
                raise ValueError(f'Invalid argument "{arg}", should be "key=value"')
            key, value = split
            if key in data.keys():
                data[key] = value
        return data
