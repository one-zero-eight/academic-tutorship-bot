from aiogram import Bot

from src.db.repositories import admin_repo, meeting_repo, student_repo
from src.domain.models import Meeting, Tutor

from .texts import *


class NotificationManager:
    def __init__(self, notification_bot: Bot):
        self._bot = notification_bot

    async def send_tutor_promoted(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        admins_text = TUTOR_PROMOTED_FOR_ADMINS.format_map(tutor_data)
        tutor_text = TUTOR_PROMOTED_FOR_TUTOR.format_map(tutor_data)
        await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, text=tutor_text)

    async def send_tutor_dismissed(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        admins_text = TUTOR_DISMISSED_FOR_ADMINS.format_map(tutor_data)
        tutor_text = TUTOR_DISMISSED_FOR_TUTOR.format_map(tutor_data)
        await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, text=tutor_text)

    async def send_meeting_tutor_assigned(self, meeting: Meeting, tutor: Tutor):
        tutor_data = tutor.model_dump()
        meeting_data = meeting.model_dump()
        data = {**tutor_data, **meeting_data}
        admins_text = TUTOR_ASSIGNED_FOR_ADMINS.format_map(data)
        tutor_text = TUTOR_ASSIGNED_FOR_TUTOR.format_map(data)
        await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, text=tutor_text)

    async def send_meeting_tutor_changed(self, meeting: Meeting, old_tutor: Tutor, new_tutor: Tutor):
        meeting_data = meeting.model_dump()
        data = {**meeting_data}
        data["old_username"] = old_tutor.username
        data["new_username"] = new_tutor.username
        admins_text = TUTOR_CHANGED_FOR_ADMINS.format_map(data)
        old_tutor_text = TUTOR_CHANGED_FOR_OLD_TUTOR.format_map(data)
        new_tutor_text = TUTOR_CHANGED_FOR_NEW_TUTOR.format_map(data)
        await self._send_admins(text=admins_text)
        await self._send_telegram_ids(old_tutor.telegram_id, text=old_tutor_text)
        await self._send_telegram_ids(new_tutor.telegram_id, text=new_tutor_text)

    async def send_meeting_updated(self, meeting: Meeting, changed_key: str):
        text = self._format_meeting_updated_text(meeting, changed_key)
        await self._send_admins(text=text)
        if meeting.tutor_id:
            await self._send_ids(meeting.tutor_id, text=text)
        await self._send_students_whose_interested(meeting, text=text)

    def _format_meeting_updated_text(self, meeting: Meeting, changed_key: str) -> str:
        changed_value = getattr(meeting, changed_key)
        meeting_data = meeting.model_dump()
        if changed_key in ("datetime", "datetime_"):
            return MEETING_UPDATED_DATETIME.format(title=meeting_data.get("title", ""), datetime=changed_value)
        elif changed_key == "room":
            return MEETING_UPDATED_ROOM.format(title=meeting_data.get("title", ""), room=changed_value)
        elif changed_key == "tutor":
            return MEETING_UPDATED_TUTOR.format(
                title=meeting_data.get("title", ""), username=meeting_data.get("tutor_username", "")
            )
        else:
            return f"Meeting '{meeting_data.get('title', '')}' updated: {changed_key} -> {changed_value}"

    async def _send_students_whose_interested(self, meeting: Meeting, *, text: str):
        telegram_ids = await meeting_repo.get_interested_student_ids(meeting.id)
        await self._send_ids(telegram_ids, text=text)

    async def _send_admins(self, *, text: str):
        telegram_ids = await admin_repo.get_telegram_ids()
        await self._send_telegram_ids(telegram_ids, text=text)

    async def _send_ids(self, student_ids: list[int] | int, *, text: str):
        if isinstance(student_ids, int):
            student_ids = [student_ids]
        telegram_ids = await student_repo.get_telegram_ids(student_ids)
        await self._send_telegram_ids(telegram_ids, text=text)

    async def _send_telegram_ids(self, telegram_ids: list[int] | int, *, text: str):
        if isinstance(telegram_ids, int):
            telegram_ids = [telegram_ids]
        for chat_id in telegram_ids:
            await self._bot.send_message(chat_id=chat_id, text=text)
