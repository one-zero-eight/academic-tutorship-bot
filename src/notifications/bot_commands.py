from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router(name="notification_bot_commands")


START_DEFAULT = """
Hello, I am a notification bot for Academic Tutorship of Innopolis.
I do nothing but sending notifications 💌

To see more go to <a href="{link}">Academic Tutorship</a>
"""

START_FROM_CONTROL_BOT = """
Thank you for activating the notification bot! 🎉
Here you will receive all notifications from Academic Tutorship 💌

To go back to the main bot <a href="{link}">click the link</a>
"""


def _extract_start_payload(message: types.Message) -> str | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    payload = parts[1].strip()
    return payload or None


@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    from src.notifications import notification_manager  # i am a rascal and want to avoid circular imports

    link = notification_manager._gen_bot_link()
    payload = _extract_start_payload(message)
    if payload == "from_control_bot":
        await message.reply(START_FROM_CONTROL_BOT.format(link=link))
    else:
        await message.reply(START_DEFAULT.format(link=link))
