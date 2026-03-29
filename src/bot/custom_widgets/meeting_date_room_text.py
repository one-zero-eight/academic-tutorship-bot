from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.bot.constants import I18N_FORMAT_KEY


def _default_format_text(text: str, data: dict) -> str:
    return text.format_map(data)


class MeetingDateRoomText(Text):
    def __init__(self, *, when: WhenCondition = None):
        super().__init__(when=when)

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        format_text = manager.middleware_data.get(
            I18N_FORMAT_KEY,
            _default_format_text,
        )

        payload = dict(data)
        payload["date"] = str(payload["date"]) if payload.get("date") else "N/A"

        lines = []
        lines.extend(
            [
                format_text("MEETING_INFO_HEADER", payload),
                "",
                format_text("MEETING_INFO_DATE_LINE", payload),
                format_text("MEETING_INFO_ROOM_LINE", payload),
            ]
        )

        text = "\n".join(lines)
        return text.format(**payload)
