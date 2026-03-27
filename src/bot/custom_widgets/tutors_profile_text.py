import html

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.bot.constants import I18N_FORMAT_KEY
from src.domain.models import Discipline


def _default_format_text(text: str, data: dict) -> str:
    return text.format_map(data)


class TutorProfileText(Text):
    def __init__(self, *, tutor_view: bool = False, when: WhenCondition = None):
        super().__init__(when=when)
        self.tutor_view = tutor_view

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        format_text = manager.middleware_data.get(
            I18N_FORMAT_KEY,
            _default_format_text,
        )

        lines = []
        lines.append(
            format_text(
                "TUTOR_PROFILE_HEADER_TUTOR_VIEW" if self.tutor_view else "TUTOR_PROFILE_HEADER_STUDENT_VIEW",
                data,
            )
        )
        lines.extend(
            [
                "",
                format_text("TUTOR_PROFILE_PROFILE_NAME_LINE", data),
                format_text("TUTOR_PROFILE_USERNAME_LINE", data),
            ]
        )
        if data.get("about"):
            lines.extend(["", format_text("TUTOR_PROFILE_ABOUT_BLOCK", data)])
        lines.extend(["", format_text("TUTOR_PROFILE_DISCIPLINES_HEADER", data)])

        disciplines: list[Discipline] = data["disciplines"]
        for discipline in disciplines:
            lines.append(
                format_text(
                    "SETTINGS_DISCIPLINE_ITEM",
                    {
                        **data,
                        "language": html.escape(str(discipline.language)),
                        "year": discipline.year,
                        "name": html.escape(discipline.name),
                    },
                )
            )
        text = "\n".join(lines)
        return text.format_map(data)
