from typing import Any

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text.base import Text

from src.bot.constants import I18N_FORMAT_KEY
from src.bot.dialog_extension import extend_dialog
from src.bot.logging_ import log_error
from src.domain.models import Meeting


def _default_format_text(text: str, data: dict) -> str:
    return text.format_map(data)


class MeetingUpdateText(Text):
    def __init__(self, when: WhenCondition = None):
        super().__init__(when=when)

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        manager = extend_dialog(manager)
        format_text = manager.middleware_data.get(
            I18N_FORMAT_KEY,
            _default_format_text,
        )

        meeting_update = await manager.state.get_value("meeting_updated", default={})
        meeting = await manager.state.get_meeting()

        update_data = self.__filter_valid_update_data(meeting_update, meeting)

        lines = []
        lines.append(format_text("MEETING_UPDATE_HEADER"))
        for key, value in update_data.items():
            if key in ["datetime", "datetime_"]:
                lines.append(format_text("MEETING_UPDATE_DATETIME_LINE", datetime=value))
            elif key in ["room"]:
                lines.append(format_text("MEETING_UPDATE_ROOM_LINE", room=value))
            else:
                log_error("MeetingUpdateText._render_text.unknown_key", key=key)
                continue

        return "\n".join(lines)

    def __filter_valid_update_data(self, meeting_update: dict[str, Any], meeting: Meeting) -> dict[str, Any]:
        """Filters out only valid keys in `meeting_update` (those which exist as attributes in `meeting`)"""
        meeting_dump = meeting.model_dump(by_alias=True)  # NOTE: for having attr datetime_ as datetime
        update_data = {}
        for key, value in meeting_update.items():
            if key not in meeting_dump:
                log_error(
                    "MeetingUpdateText._render_text.key_not_in_meeting", key=key, value=value, meeting_dump=meeting_dump
                )
            # elif isinstance(value, type(meeting_dump[key])):
            #     log_error('MeetingUpdateText._render_text.value_type_not_matched', key=key, type=type(value), meeting_dump=meeting_dump)
            else:
                update_data[key] = value
        return update_data
