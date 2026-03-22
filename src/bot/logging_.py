__all__ = ["logger", "log_info", "log_warning", "log_error"]

import logging.config
import os
from collections.abc import Mapping
from typing import Any

import yaml


class RelativePathFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.relativePath = os.path.relpath(record.pathname)
        return True


with open("logging.yaml") as f:
    config = yaml.safe_load(f)

for handler in config.get("handlers", {}).values():
    filename = handler.get("filename")
    if filename:
        os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)

    logging.config.dictConfig(config)

logger = logging.getLogger("src.bot")
logger.addFilter(RelativePathFilter())


def _format_value(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return value.strip().replace("\n", "\\n")
    if isinstance(value, int | float):
        return str(value)
    return repr(value)


def _format_context(context: Mapping[str, Any]) -> str:
    if not context:
        return ""
    pairs = [f"{key}={_format_value(value)}" for key, value in context.items()]
    return " | " + " ".join(pairs)


def log_info(event: str, **context: Any):
    logger.info(f"{event}{_format_context(context)}")


def log_warning(event: str, **context: Any):
    logger.warning(f"{event}{_format_context(context)}")


def log_error(event: str, *, exc_info: bool = True, **context: Any):
    logger.error(f"{event}{_format_context(context)}", exc_info=exc_info)


def log_debug(event: str, **context: Any):
    logger.debug(f"{event}{_format_context(context)}")
