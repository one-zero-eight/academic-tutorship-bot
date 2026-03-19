import html

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

LINES = [
    "ℹ️ Meeting Information",
    "",
    "<b>{title}</b>",
    "[{d_lang} {d_year}y] {d_name}",  # discipline info: language, year, name
    "",
    "📆 Date: <b>{date}</b>",
    "⏱️ Duration: <b>{duration}</b>",
    "📍 Room: <b>{room}</b>",
    "🧑‍🏫 Tutor: @{tutor_username}",
]

ADMIN_LINES = [
    "",
    "Status: <b>{status.name}</b>",
    "Attendance: <b>{attendance_count}</b>",
]

DESCRIPTION_LINES = [
    "",
    "Description:\n<blockquote>{description}</blockquote>",
]


class MeetingInfoText(Text):
    def __init__(self, *, admin_info: bool = False, when: WhenCondition = None):
        super().__init__(when=when)
        self.show_admin_info = admin_info

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        discipline = data.get("discipline")
        data["d_lang"] = html.escape(str(getattr(discipline, "language", "")))
        data["d_year"] = getattr(discipline, "year", "")
        data["d_name"] = html.escape(str(getattr(discipline, "name", "")))
        lines = []
        lines.extend(LINES)
        if self.show_admin_info:
            lines.extend(ADMIN_LINES)
        if self.__has_description(data):
            lines.extend(DESCRIPTION_LINES)
        text = "\n".join(lines)
        return text.format_map(data)

    def __has_description(self, data) -> bool:
        description = data.get("description")
        return description is not None
