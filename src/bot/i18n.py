import os
from datetime import date, datetime
from typing import Any, Protocol

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from fluent.runtime import FluentLocalization, FluentResourceLoader

from src.bot.constants import I18N_FORMAT_KEY
from src.bot.middlewares import DialogI18nMiddleware


class Values(Protocol):
    def __getitem__(self, item: Any) -> Any:
        raise NotImplementedError


class I18NFormat(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        format_text = manager.middleware_data.get(
            I18N_FORMAT_KEY,
            default_format_text,
        )
        normalized_data = normalize_l10n_kwargs(data)
        translated_text = format_text(self.text, normalized_data)
        return translated_text.format(**normalized_data)


def default_format_text(text: str, data: Values) -> str:
    if isinstance(data, dict):
        data = normalize_l10n_kwargs(data)
    return text.format_map(data)


def normalize_l10n_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="minutes")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: normalize_l10n_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_l10n_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_l10n_value(item) for item in value)
    return value


def normalize_l10n_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {key: normalize_l10n_value(value) for key, value in kwargs.items()}


def make_i18n_middleware(locales: list[str], default_locale: str = "en"):
    loader = FluentResourceLoader(
        os.path.join(
            os.getcwd(),
            "locales",
            "{locale}",
            "LC_MESSAGES",
        )
    )
    l10ns = {
        locale: FluentLocalization(
            [locale, default_locale],
            ["dialog.ftl", "handles.ftl"],
            loader,
        )
        for locale in locales
    }
    return DialogI18nMiddleware(l10ns, default_locale)


LOCALES = ["en", "ru"]
DEFAULT_LOCALE = "en"
DEFAULT_LOADER = FluentResourceLoader(
    os.path.join(
        os.getcwd(),
        "locales",
        "{locale}",
        "LC_MESSAGES",
    )
)
NOTIFICATION_L10NS = {
    locale: FluentLocalization(
        [locale, DEFAULT_LOCALE],
        ["notifications.ftl", "notification_handles.ftl"],
        DEFAULT_LOADER,
    )
    for locale in LOCALES
}
