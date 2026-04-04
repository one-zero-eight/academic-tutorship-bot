import asyncio
from collections.abc import Callable
from typing import Literal

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.i18n import NOTIFICATION_L10NS, normalize_l10n_kwargs
from src.bot.logging_ import log_error, log_info
from src.db.repositories import admin_repo, meeting_repo, student_repo, tutor_repo
from src.domain.models import Meeting, MeetingStatus, MeetingUpdate, Tutor

type TextIDForm = tuple[str, dict]
"Represents a text_id message (for fluent l10n) and its formatting arguments"
type ReplyMarkupFactory = Callable[[str], InlineKeyboardMarkup]
"Builds an inline keyboard for a specific language"
type ReplyMarkup = InlineKeyboardMarkup | ReplyMarkupFactory | None
type ReminderKind = Literal["24h", "1h"]


def _txt(_text_id_: str, **kwargs) -> TextIDForm:
    return _text_id_, kwargs


class NotificationManager:
    def __init__(self, notification_bot: Bot, notification_dispatcher: Dispatcher):
        self._bot = notification_bot
        self._dispatcher = notification_dispatcher
        self._control_bot_username = None
        self._notification_bot_username = None
        self._polling_task = None

    def set_control_bot_username(self, username: str):
        """Sets the username of the control bot, used for generating meeting links."""
        self._control_bot_username = username

    async def load_notification_bot_username(self):
        """Loads the username of the notification bot from Telegram API, used for generating links."""
        me = await self._bot.get_me()
        self._notification_bot_username = me.username

    async def start_polling(self):
        """Starts the unblocking polling task for the notification bot. Should be called once during startup."""
        await self._bot.delete_webhook(drop_pending_updates=True)
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
        text = _txt("NOTIF_BOT_STARTED", link=self.gen_control_bot_link())
        await self._send_admins(text=text)

    async def send_bot_shutdown(self):
        text = _txt("NOTIF_BOT_SHUTDOWN", link=self.gen_control_bot_link())
        await self._send_admins(text=text)

    async def send_receive_notification_toggled(self, student_id: int, enabled: bool):
        if enabled:
            text = _txt("NOTIF_RECEIVE_NOTIFICATION_ENABLED", link=self.gen_control_bot_link())
        else:
            text = _txt("NOTIF_RECEIVE_NOTIFICATION_DISABLED", link=self.gen_control_bot_link("settings"))
        await self._send_ids(student_id, text=text)

    async def send_meeting_tutor_assigned(self, meeting: Meeting, tutor: Tutor):
        tutor_data = tutor.model_dump()
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**tutor_data, **meeting_data, "link": self.gen_meeting_link(meeting.id)}
        admins_text = _txt("NOTIF_TUTOR_ASSIGNED_FOR_ADMINS", **data)
        tutor_text = _txt("NOTIF_TUTOR_ASSIGNED_FOR_TUTOR", **data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)
        # NOTE: don't notify students , they don't know the meeting yet, so they won't care

    async def send_meeting_tutor_changed(self, meeting: Meeting, old_tutor: Tutor, new_tutor: Tutor):
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**meeting_data}
        data["old_username"] = old_tutor.username
        data["new_username"] = new_tutor.username
        data["link"] = self.gen_meeting_link(meeting.id)
        admins_text = _txt("NOTIF_TUTOR_CHANGED_FOR_ADMINS", **data)
        old_tutor_text = _txt("NOTIF_TUTOR_CHANGED_FOR_OLD_TUTOR", **data)
        new_tutor_text = _txt("NOTIF_TUTOR_CHANGED_FOR_NEW_TUTOR", **data)
        students_text = _txt("NOTIF_MEETING_UPDATED_TUTOR", **data)
        sent = await self._send_admins(text=admins_text)
        await self._send_telegram_ids(old_tutor.telegram_id, exclude=sent, text=old_tutor_text)
        await self._send_telegram_ids(new_tutor.telegram_id, exclude=sent, text=new_tutor_text)
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            await self._send_students_who_interested(meeting, exclude=sent, text=students_text)

    async def send_meeting_approve_request(self, meeting: Meeting, tutor: Tutor):
        """Sends approval request to the head of AT with approve/discard buttons"""
        meeting_data = meeting.model_dump(by_alias=True)
        text = _txt(
            "NOTIF_MEETING_APPROVE_REQUEST",
            **meeting_data,
            username=tutor.username,
            link=self.gen_meeting_link(meeting.id),
        )

        def reply_markup(lang: str) -> InlineKeyboardMarkup:
            return self.gen_approve_discard_meeting_request_reply_markup(meeting.id, lang)

        await self._send_admins(text=text, reply_markup=reply_markup)  # TODO: add approve/discard buttons

    async def send_meeting_approved(self, meeting: Meeting):
        text = _txt("NOTIF_MEETING_APPROVED", title=meeting.title, link=self.gen_meeting_link(meeting.id))
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))

    async def send_meeting_discarded(self, meeting: Meeting, reason: str):
        text = _txt(
            "NOTIF_MEETING_DISCARDED", title=meeting.title, reason=reason, link=self.gen_meeting_link(meeting.id)
        )
        sent = await self._send_admins(text=text)
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))

    async def send_meeting_announced(self, meeting: Meeting, tutor: Tutor):
        meeting_data = meeting.model_dump(by_alias=True)
        data = {**meeting_data, "username": tutor.username, "link": self.gen_meeting_link(meeting.id)}
        text = _txt("NOTIF_MEETING_ANNOUNCED", **data)
        sent = await self._send_admins(text=text)
        sent.extend(await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=text))
        await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_cancelled(self, meeting: Meeting):
        text = _txt("NOTIF_MEETING_CANCELLED_FOR_USERS", title=meeting.title)
        sent = []
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        if meeting.status >= MeetingStatus.APPROVING:
            # NOTE: admins should not now about the meeting while it is not sent for approval or announced
            sent.extend(await self._send_admins(text=text))
        if meeting.status in (MeetingStatus.ANNOUNCED, MeetingStatus.CONDUCTING):
            # NOTE: students would only care if meeting already announced and not finished
            await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_reminder(self, meeting: Meeting, reminder_kind: ReminderKind):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            **meeting.model_dump(by_alias=True),
            "link": self.gen_meeting_link(meeting.id),
            "username": tutor.username if tutor else None,
        }
        reminder_text_id = {
            "24h": "NOTIF_MEETING_REMINDER_24H",
            "1h": "NOTIF_MEETING_REMINDER_1H",
        }[reminder_kind]
        text = _txt(reminder_text_id, **data)
        sent = []
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        if meeting.status == MeetingStatus.ANNOUNCED:
            # NOTE: students would only care if meeting already announced
            sent.extend(await self._send_admins(text=text))
            await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_started(self, meeting: Meeting):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            **meeting.model_dump(),
            "link": self.gen_meeting_link(meeting.id),
            "username": tutor.username if tutor else None,
        }
        text = _txt("NOTIF_MEETING_STARTED", **data)
        sent = []
        if meeting.tutor_id:
            sent.extend(await self._send_ids(meeting.tutor_id, exclude=sent, text=text))
        sent.extend(await self._send_admins(text=text))
        await self._send_students_who_interested(meeting, exclude=sent, text=text)

    async def send_meeting_finished(self, meeting: Meeting):
        tutor = await tutor_repo.get(id=meeting.tutor_id) if meeting.tutor_id else None
        data = {
            "title": meeting.title,
            "link": self.gen_meeting_link(meeting.id),
            "username": tutor.username if tutor else None,
        }
        text = _txt("NOTIF_MEETING_FINISHED", **data)
        sent = []
        sent.extend(await self._send_admins(text=text))
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
            "link": self.gen_meeting_link(meeting.id),
        }
        if by_admin:
            text = _txt("NOTIF_MEETING_CLOSED_FOR_ADMINS", **data)
        else:
            text = _txt("NOTIF_MEETING_CLOSED_FOR_TUTOR", **data)
        sent = []
        sent.extend(await self._send_admins(text=text))
        await self._send_ids(meeting.tutor_id, exclude=sent, text=text)

    async def send_tutor_promoted(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        tutor_data.update({"link": self.gen_control_bot_link("promoted_tutor")})
        admins_text = _txt("NOTIF_TUTOR_PROMOTED_FOR_ADMINS", **tutor_data)
        tutor_text = _txt("NOTIF_TUTOR_PROMOTED_FOR_TUTOR", **tutor_data)
        sent = []
        sent.extend(await self._send_admins(text=admins_text))
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)

    async def send_tutor_dismissed(self, tutor: Tutor):
        tutor_data = tutor.model_dump()
        admins_text = _txt("NOTIF_TUTOR_DISMISSED_FOR_ADMINS", **tutor_data)
        tutor_text = _txt("NOTIF_TUTOR_DISMISSED_FOR_TUTOR", **tutor_data)
        sent = []
        sent.extend(await self._send_admins(text=admins_text))
        await self._send_telegram_ids(tutor.telegram_id, exclude=sent, text=tutor_text)

    def _format_meeting_update_text(
        self, header_id: str, meeting: Meeting, meeting_update: MeetingUpdate
    ) -> list[TextIDForm]:
        """Builds multiline localized message for a meeting update event."""
        lines = [_txt(header_id, title=meeting.title)]
        if meeting_update.room:
            lines.append(_txt("NOTIF_MEETING_UPDATE_ROOM", old_room=meeting.room, room=meeting_update.room))
        if meeting_update.datetime_:
            old_dt = meeting.datetime_.isoformat(sep=" ", timespec="minutes") if meeting.datetime_ else "-"
            new_dt = meeting_update.datetime_.isoformat(sep=" ", timespec="minutes")
            lines.append(_txt("NOTIF_MEETING_UPDATE_DATETIME", old_datetime=old_dt, datetime=new_dt))
        lines.append(_txt("NOTIF_MEETING_LINK", link=self.gen_meeting_link(meeting_update.id)))
        return lines

    async def send_meeting_update_request(self, meeting_update: MeetingUpdate):
        meeting = await meeting_repo.get(meeting_update.id)
        text = self._format_meeting_update_text("NOTIF_MEETING_UPDATE_REQUEST", meeting, meeting_update)

        def reply_markup(lang: str) -> InlineKeyboardMarkup:
            return self.gen_approve_discard_update_request_reply_markup(meeting_update.id, lang)

        await self._send_admins(text=text, reply_markup=reply_markup)

    async def send_meeting_update_approved(self, meeting: Meeting, meeting_update: MeetingUpdate):
        """Sends meeting update approved to tutor and update notification to students who are interested"""
        approved_text = self._format_meeting_update_text("NOTIF_MEETING_UPDATE_APPROVED", meeting, meeting_update)
        info_text = self._format_meeting_update_text("NOTIF_MEETING_UPDATE_INFO", meeting, meeting_update)
        assert meeting.tutor_id
        sent = []
        sent.extend(await self._send_admins(text=approved_text))
        sent.extend(await self._send_ids(meeting.tutor_id, text=approved_text, exclude=sent))
        sent.extend(await self._send_students_who_interested(meeting, text=info_text))

    async def send_meeting_update_discarded(self, meeting: Meeting, meeting_update: MeetingUpdate, reason: str):
        """Sends meeting update discarded to tutor and admins"""
        text = self._format_meeting_update_text("NOTIF_MEETING_UPDATE_DISCARDED", meeting, meeting_update)
        text.append(_txt("NOTIF_MEETING_UPDATE_DISCARDED_REASON", reason=reason))
        assert meeting.tutor_id
        sent = []
        sent.extend(await self._send_admins(text=text))
        sent.extend(await self._send_ids(meeting.tutor_id, text=text))

    async def _send_students_who_interested(
        self,
        meeting: Meeting,
        *,
        exclude: list[int] = [],
        text: TextIDForm | list[TextIDForm],
        reply_markup: ReplyMarkup = None,
    ) -> list[int]:
        """Sends a message to all students who are interested in the meeting, excluding the provided telegram ids."""
        telegram_ids = await meeting_repo.get_interested_student_ids(meeting.id)
        return await self._send_ids(telegram_ids, exclude=exclude, text=text, reply_markup=reply_markup)

    async def _send_admins(self, *, text: TextIDForm | list[TextIDForm], reply_markup: ReplyMarkup = None) -> list[int]:
        """Sends a message to all admins, returns the list of telegram ids the message was sent to."""
        telegram_ids = await admin_repo.get_telegram_ids()
        return await self._send_telegram_ids(telegram_ids, text=text, reply_markup=reply_markup)

    async def _send_ids(
        self,
        student_ids: list[int] | int,
        *,
        exclude: list[int] = [],
        text: TextIDForm | list[TextIDForm],
        reply_markup: ReplyMarkup = None,
    ) -> list[int]:
        """Sends a message to a list of student ids, resolves their telegram ids.
        If a single student id is provided, it will be converted to a list.
        Returns the list of telegram ids the message was sent to.
        """
        if isinstance(student_ids, int):
            student_ids = [student_ids]
        telegram_ids = await student_repo.get_telegram_ids(student_ids)
        return await self._send_telegram_ids(telegram_ids, exclude=exclude, text=text, reply_markup=reply_markup)

    async def _send_telegram_ids(
        self,
        telegram_ids: list[int] | int,
        *,
        exclude: list[int] = [],
        text: TextIDForm | list[TextIDForm],
        reply_markup: ReplyMarkup = None,
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
        id_lang_dict = await student_repo.get_language_by_telegram_ids(telegram_ids)
        if isinstance(text, tuple):
            text = [text]
        sent = []
        for chat_id, lang in id_lang_dict.items():
            try:
                localised_formatted_text = "\n".join(self._localize_format(line, lang) for line in text).strip()
                if not localised_formatted_text:
                    log_error("notification_manager.send.empty_text", user_id=chat_id, lang=lang)
                    continue
                localised_reply_markup = self._localize_reply_markup(reply_markup, lang)
                await self._bot.send_message(
                    chat_id=chat_id,
                    text=localised_formatted_text,
                    reply_markup=localised_reply_markup,
                )
                sent.append(chat_id)
            except TelegramForbiddenError as e:
                await student_repo.set_notification_bot_blocked(telegram_id=chat_id)
                log_info("notification_manager.send.blocked", user_id=chat_id, reason=str(e))
            except TelegramBadRequest as e:
                await student_repo.set_notification_bot_unactivated(telegram_id=chat_id)
                log_info("notification_manager.send.unactivated", user_id=chat_id, reason=str(e))
            except Exception as e:
                log_error("notification_manager.send.failed", user_id=chat_id, reason=str(e))
        return sent

    def gen_control_bot_link(self, payload: str = "default") -> str:
        return f"https://t.me/{self._control_bot_username}?start={payload}"

    def gen_notification_bot_link(self, payload: str = "default") -> str:
        return f"https://t.me/{self._notification_bot_username}?start={payload}"

    def gen_meeting_link(self, meeting_id: int) -> str:
        return self.gen_control_bot_link(payload=f"meeting_{meeting_id}")

    def gen_approve_discard_meeting_request_reply_markup(self, meeting_id: int, lang: str = "en"):
        approve_button = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_APPROVE", lang),
            callback_data=f"approve_{meeting_id}",
        )
        discard_button = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_DISCARD", lang),
            callback_data=f"discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[approve_button, discard_button]])

    def gen_confirm_approve_meeting_reply_markup(self, meeting_id: int, lang: str = "en"):
        cancel_approve = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"cancel_approve_{meeting_id}",
        )
        confirm_approve = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CONFIRM_APPROVE", lang),
            callback_data=f"confirm_approve_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[cancel_approve, confirm_approve]])

    def gen_confirm_discard_meeting_reply_markup(self, meeting_id: int, lang: str = "en"):
        confirm_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CONFIRM_DISCARD", lang),
            callback_data=f"confirm_discard_{meeting_id}",
        )
        cancel_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"cancel_discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[confirm_discard, cancel_discard]])

    def gen_cancel_discard_meeting_reply_markup(self, meeting_id: int, lang: str = "en"):
        cancel_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"cancel_discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[cancel_discard]])

    def gen_approve_discard_update_request_reply_markup(self, meeting_id: int, lang: str = "en"):
        approve_button = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_APPROVE", lang),
            callback_data=f"update_approve_{meeting_id}",
        )
        discard_button = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_DISCARD", lang),
            callback_data=f"update_discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[approve_button, discard_button]])

    def gen_confirm_approve_update_reply_markup(self, meeting_id: int, lang: str = "en"):
        cancel_approve = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"update_cancel_approve_{meeting_id}",
        )
        confirm_approve = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CONFIRM_APPROVE", lang),
            callback_data=f"update_confirm_approve_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[cancel_approve, confirm_approve]])

    def gen_confirm_discard_update_reply_markup(self, meeting_id: int, lang: str = "en"):
        confirm_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CONFIRM_DISCARD", lang),
            callback_data=f"update_confirm_discard_{meeting_id}",
        )
        cancel_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"update_cancel_discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[confirm_discard, cancel_discard]])

    def gen_cancel_discard_update_reply_markup(self, meeting_id: int, lang: str = "en"):
        cancel_discard = InlineKeyboardButton(
            text=self._localize_text_id("NOTIF_BTN_CANCEL", lang),
            callback_data=f"update_cancel_discard_{meeting_id}",
        )
        return InlineKeyboardMarkup(inline_keyboard=[[cancel_discard]])

    def _localize_reply_markup(self, reply_markup: ReplyMarkup, lang: str) -> InlineKeyboardMarkup | None:
        if reply_markup is None:
            return None
        if callable(reply_markup):
            return reply_markup(lang)
        return reply_markup

    def _localize_text_id(self, text_id: str, lang: str, **kwargs) -> str:
        l10n = NOTIFICATION_L10NS.get(lang, NOTIFICATION_L10NS["en"])
        return l10n.format_value(text_id, normalize_l10n_kwargs(kwargs))

    def _localize_format(self, text: TextIDForm, lang: str) -> str:
        """Localizes and formats a TextIDForm message for a given language"""
        return self._localize_text_id(text[0], lang, **text[1])
