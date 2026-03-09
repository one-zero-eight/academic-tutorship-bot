from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.domain.models import Discipline

HEADER_DISPLAY = [
    "🧑‍🏫 Tutor's Profile",
]

HEADER_TUTOR = [
    "🧑‍🏫 Your Tutor's Profile",
]

LINES = [
    "",
    "<b>{profile_name}</b>",
    "@{username}",
]


DISCIPLINE_LINES = [
    "",
    "📚 Disciplines:",
]


DISCIPLINE_FORMAT = "- <b>[{discipline.language} {discipline.year}y] {discipline.name}</b>"

ABOUT_LINES = [
    "",
    "<blockquote>{about}</blockquote>",
]


class TutorProfileText(Text):
    def __init__(self, *, tutor_view: bool = False, when: WhenCondition = None):
        super().__init__(when=when)
        self.tutor_view = tutor_view

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        lines = []
        lines.extend(HEADER_TUTOR if self.tutor_view else HEADER_DISPLAY)
        lines.extend(LINES)
        if data.get("about"):
            lines.extend(ABOUT_LINES)
        lines.extend(DISCIPLINE_LINES)
        disciplines: list[Discipline] = data["disciplines"]
        for discipline in disciplines:
            lines.append(DISCIPLINE_FORMAT.format(discipline=discipline))
        text = "\n".join(lines)
        return text.format_map(data)
