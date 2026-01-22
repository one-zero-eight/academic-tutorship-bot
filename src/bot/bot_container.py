"""Utility module that stores AIOgram Bot
Needed to pass the Bot object to lower layers of the app.
As the Bot is created at the conclusion of initialization.

Maybe a crutch.
"""

from aiogram import Bot

_bot: Bot | None = None


def set_bot(bot: Bot):
    global _bot  # noqa: PLW0603
    _bot = bot


def get_bot() -> Bot:
    if not _bot:
        raise ValueError("Bot is not assigned in bot_container")
    return _bot
