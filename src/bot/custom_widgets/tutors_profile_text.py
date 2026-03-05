from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

LINES = [
    "🧑‍🏫 Tutor's Profile",
    "",
    "<b>{full_name}</b>",
    "@{username}",
    "📚 Discipline: <b>{discipline}</b>",
]

ABOUT_LINES = [
    "",
    "{about}",
]


class TutorProfileText(Text):
    def __init__(self, *, when: WhenCondition = None):
        super().__init__(when=when)

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        lines = []
        lines.extend(LINES)
        if data.get("about"):
            lines.extend(ABOUT_LINES)
        text = "\n".join(lines)
        return text.format_map(data)
