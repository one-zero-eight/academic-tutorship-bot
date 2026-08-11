from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.bot.constants import I18N_FORMAT_KEY
from src.domain.models import Discipline


def _default_format_text(text: str, data: dict) -> str:
    return text.format_map(data)


class DisciplinesControlListText(Text):
    def __init__(self, when: WhenCondition = None):
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
        disciplines: list[Discipline] = payload.get("disciplines")  # type: ignore
        if disciplines is None:
            return "Error: disciplines is None"

        lines = []

        prev_d: Discipline = None  # type: ignore
        for d in disciplines:
            if prev_d is not None:
                if prev_d.language != d.language or prev_d.year != d.year or prev_d.semester != d.semester:
                    lines.append("")
            context = {
                "d_id": d.id,
                "d_lang": d.language,
                "d_year": d.year,
                "d_semester": d.semester,
                "d_name": d.name,
            }

            lines.append(format_text("DISCIPLINES_CONTROL_LIST_ENTRY", context))
            prev_d = d

        text = "\n".join(lines)
        rendered = text.format(**payload).strip()
        return rendered if rendered else "Disciplines Control"
