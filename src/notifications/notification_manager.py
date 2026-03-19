import asyncio

from aiogram import Bot, Dispatcher

from src.db.repositories import admin_repo, meeting_repo, student_repo, tutor_repo
from src.domain.models import Meeting, MeetingStatus, Tutor

from .texts import *


class NotificationManager:
    def __init__(self, notification_bot: Bot, notification_dispatcher: Dispatcher):
        self._bot = notification_bot
        self._dispatcher = notification_dispatcher
        self._polling_task = None

    def set_main_bot_username(self, username: str):
        """Sets the username of the main bot, used for generating meeting links."""
        self._main_bot_username = username

    async def start_polling(self):
        """Starts the unblocking polling task for the notification bot. Should be called once during startup."""
        self._polling_task = asyncio.create_task(self._dispatcher.start_polling(self._bot))

    async def stop_polling(self):
        """Stops the polling task for the notification bot. Should be called during shutdown."""
        if not self._polling_task:
            raise RuntimeError("Polling task is not running")
        self._polling_task.cancel()
        try:
            await self._polling_task
        except asyncio.CancelledError:
            pass

    async def send_bot_started(self):
        text = BOT_STARTED.format(link=self._gen_bot_link())
        await self._send_admins(text=text)

    async def send_bot_shutdown(self):
        text = BOT_SHUTDOWN.format(link=self._gen_bot_link())
        await self._send_admins(text=text)

    async def send_meeting_tutor_assigned(self, meeting: Meeting, tutor: Tutor):
        tutor_data = tutor.model_dump()
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**tutor_data, **meeting_data, "link": self._gen_meeting_link(meeting)}
        admins_text = TUTOR_ASSIGNED_FOR_ADMINS.format_map(data)
        tutor_text = TUTOR_ASSIGNED_FOR_TUTOR.format_map(data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)
        # NOTE: don't notify students , they don't know the meeting yet, so they won't care

    async def send_meeting_tutor_changed(self, meeting: Meeting, old_tutor: Tutor, new_tutor: Tutor):
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**meeting_data}
        data["old_username"] = old_tutor.username
        data["new_username"] = new_tutor.username
        data["link"] = self._gen_meeting_link(meeting)
        admins_text = TUTOR_CHANGED_FOR_ADMINS.format_map(data)
        old_tutor_text = TUTOR_CHANGED_FOR_OLD_TUTOR.format_map(data)
        new_tutor_text = TUTOR_CHANGED_FOR_NEW_TUTOR.format_map(data)
        students_text = TUTOR_CHANGED_FOR_STUDENTS.format_map(data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(old_tutor.telegram_id, exclude=sent, text=old_tutor_text)
        await self._send_telegram_ids(new_tutor.telegram_id, exclude=sent, text=new_tutor_text)
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            await self._send_students_who_interested(meeting, exclude=sent, text=students_text)

    async def send_meeting_updated(self, meeting: Meeting, changed_key: str):
        text = self._format_meeting_updated_text(meeting, changed_key)
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_announced(self, meeting: Meeting, tutor: Tutor):
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**meeting_data, "username": tutor.username, "link": self._gen_meeting_link(meeting)}
        text = MEETING_ANNOUNCED.format_map(data)
        sent = await self._send_admins(text=text)
        sent.extend(await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=text))
        await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_cancelled(self, meeting: Meeting):
        text = MEETING_CANCELLED.format(title=meeting.title)
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            await self._send_students_who_interested(meeting, exclude=sent, text=text)

    # TODO: add this notification somewhere in scheduling logic
    async def send_meeting_reminder(self, meeting: Meeting):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            **meeting.model_dump(by_alias=True),
            "link": self._gen_meeting_link(meeting),
            "username": tutor.username if tutor else None,
        }
        text = MEETING_REMINDER.format_map(data)
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_started(self, meeting: Meeting):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            **meeting.model_dump(),
            "link": self._gen_meeting_link(meeting),
            "username": tutor.username if tutor else None,
        }
        text = MEETING_STARTED.format_map(data)
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_finished(self, meeting: Meeting):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            "title": meeting.title,
            "link": self._gen_meeting_link(meeting),
            "username": tutor.username if tutor else None,
        }
        text = MEETING_FINISHED.format_map(data)
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        # NOTE: we don't send finished meeting notification to students,
        #       they might not care or find it annoying.

    async def send_meeting_closed(self, meeting: Meeting, by_admin: bool):
        assert meeting.tutor_id
        # NOTE: The meeting could be in this state only if tutor present,
        #       so the assert should never fail.
        attendance_count = len(await meeting_repo.get_attendance(meeting.id))
        data = {
            "title": meeting.title,
            "attendance_count": attendance_count,
            "link": self._gen_meeting_link(meeting),
        }
        if by_admin:
            text = MEETING_CLOSED_FOR_ADMINS.format_map(data)
        else:
            text = MEETING_CLOSED_FOR_TUTOR.format_map(data)
        sent = await self._send_admins(text=text)
        await self._send_ids(meeting.tutor_id, exclude=sent, text=text)

    async def send_tutor_promoted(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        admins_text = TUTOR_PROMOTED_FOR_ADMINS.format_map(tutor_data)
        tutor_text = TUTOR_PROMOTED_FOR_TUTOR.format_map(tutor_data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)

    async def send_tutor_dismissed(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        admins_text = TUTOR_DISMISSED_FOR_ADMINS.format_map(tutor_data)
        tutor_text = TUTOR_DISMISSED_FOR_TUTOR.format_map(tutor_data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)

    def _format_meeting_updated_text(self, meeting: Meeting, changed_key: str) -> str:
        link = self._gen_meeting_link(meeting)
        if changed_key in ("datetime", "datetime_"):
            return MEETING_UPDATED_DATETIME.format(title=meeting.title, datetime=meeting.datetime_, link=link)
        elif changed_key == "room":
            return MEETING_UPDATED_ROOM.format(title=meeting.title, room=meeting.room, link=link)
        raise ValueError(f"Unknown changed_key: {changed_key}")

    async def _send_students_who_interested(self, meeting: Meeting, *, exclude: list[int] = [], text: str):
        """Sends a message to all students who are interested in the meeting, excluding the provided telegram ids."""
        telegram_ids = await meeting_repo.get_interested_student_ids(meeting.id)
        await self._send_ids(telegram_ids, exclude=exclude, text=text)

    async def _send_admins(self, *, text: str) -> list[int]:
        """Sends a message to all admins, returns the list of telegram ids the message was sent to."""
        telegram_ids = await admin_repo.get_telegram_ids()
        return await self._send_telegram_ids(telegram_ids, text=text)

    async def _send_ids(self, student_ids: list[int] | int, *, exclude: list[int] = [], text: str) -> list[int]:
        """Sends a message to a list of student ids, resolves their telegram ids.
        If a single student id is provided, it will be converted to a list.
        Returns the list of telegram ids the message was sent to.
        """
        if isinstance(student_ids, int):
            student_ids = [student_ids]
        telegram_ids = await student_repo.get_telegram_ids(student_ids)
        return await self._send_telegram_ids(telegram_ids, exclude=exclude, text=text)

    async def _send_telegram_ids(
        self, telegram_ids: list[int] | int, *, exclude: list[int] = [], text: str
    ) -> list[int]:
        """Sends a message to a list of telegram ids, removing duplicates.
            If exclude list is provided, those telegram ids will be skipped.
        If a single telegram id is provided, it will be converted to a list.
        Returns the list of telegram ids the message was sent to.
        """
        if isinstance(telegram_ids, int):
            telegram_ids = [telegram_ids]
        telegram_ids = list(set(telegram_ids))  # Remove duplicates
        telegram_ids = [tid for tid in telegram_ids if tid not in exclude]  # Remove excluded ids
        sent = []
        for chat_id in telegram_ids:
            try:
                await self._bot.send_message(chat_id=chat_id, text=text)
                sent.append(chat_id)
            except Exception:
                # TODO: log the error properly
                pass
        return sent

    def _gen_bot_link(self) -> str:
        return f"https://t.me/{self._main_bot_username}?start=welcome"

    def _gen_meeting_link(self, meeting: Meeting) -> str:
        return f"https://t.me/{self._main_bot_username}?start=meeting_{meeting.id}"
