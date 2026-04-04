import html

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.bot.constants import I18N_FORMAT_KEY


def _default_format_text(text: str, data: dict) -> str:
    return text.format_map(data)


class MeetingInfoText(Text):
    def __init__(self, *, admin_info: bool = False, only_head: bool = False, when: WhenCondition = None):
        super().__init__(when=when)
        self.show_admin_info = admin_info
        self.only_head = only_head

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
        discipline = payload.get("discipline")
        payload["d_lang"] = html.escape(str(getattr(discipline, "language", "")))
        payload["d_year"] = getattr(discipline, "year", "")
        payload["d_name"] = html.escape(str(getattr(discipline, "name", "")))
        payload["status_name"] = getattr(payload.get("status"), "name", "")
        payload["date"] = str(payload["date"]) if payload.get("date") else "N/A"
        payload["attendance_count"] = (
            payload["attendance_count"] if payload.get("attendance_count") is not None else "N/A"
        )

        lines = []
        lines.extend(
            [
                format_text("MEETING_INFO_HEADER", payload),
                "",
                format_text("MEETING_INFO_TITLE_LINE", payload),
                format_text("MEETING_INFO_DISCIPLINE_LINE", payload),
            ]
        )

        if self.only_head:
            text = "\n".join(lines)
            rendered = text.format(**payload).strip()
            return rendered if rendered else "Meeting"

        lines.extend([""])

        lines.extend(
            [
                format_text("MEETING_INFO_DATE_LINE", payload),
                format_text("MEETING_INFO_ROOM_LINE", payload),
            ]
        )

        lines.extend(
            [
                format_text("MEETING_INFO_DURATION_LINE", payload),
                format_text("MEETING_INFO_TUTOR_LINE", payload),
            ]
        )

        if self.show_admin_info:
            lines.extend(
                [
                    "",
                    format_text("MEETING_INFO_ADMIN_STATUS_LINE", payload),
                    format_text("MEETING_INFO_ADMIN_ATTENDANCE_LINE", payload),
                ]
            )

        if self.__has_description(data):
            lines.extend(
                [
                    "",
                    format_text("MEETING_INFO_DESCRIPTION_HEADER", payload),
                    format_text("MEETING_INFO_DESCRIPTION_BLOCK", payload),
                ]
            )

        text = "\n".join(lines)
        rendered = text.format(**payload).strip()
        return rendered if rendered else "Meeting"

    def __has_description(self, data) -> bool:
        description = data.get("description")
        return description is not None
