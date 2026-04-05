from datetime import datetime
from enum import IntEnum, StrEnum

from pydantic import BaseModel, EmailStr, Field, computed_field


class UserStatus(StrEnum):
    student = "student"
    tutor = "tutor"
    admin = "admin"


class MeetingStatus(IntEnum):
    CREATED = 0
    APPROVING = 1
    ANNOUNCED = 2
    CONDUCTING = 3
    FINISHED = 4
    CLOSED = 5


class NotificationBotStatus(IntEnum):
    ACTIVATED = 0
    UNACTIVATED = 1
    BLOCKED = 2


class Settings(BaseModel):
    receive_notifications: bool = True


class Student(BaseModel):
    id: int
    telegram_id: int
    language: str = "en"
    email: EmailStr
    settings: Settings
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    "Telegram username (without @)"
    is_admin: bool = False
    notification_bot_status: NotificationBotStatus = NotificationBotStatus.UNACTIVATED
    "Status of notification bot: whether it was activated, was not, or was blocked by user"
    saw_guide: bool = False
    "Whether the user has seen the guide message on first interaction with bot"

    @computed_field
    @property
    def full_name(self) -> str:
        name_parts = [self.first_name, self.last_name]
        return " ".join(part for part in name_parts if part)


class Photo(BaseModel):
    id: int
    telegram_file_id: str
    file_path: str


class Discipline(BaseModel):
    id: int
    name: str
    year: int
    language: str


class Tutor(BaseModel):
    id: int
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_name: str | None = None
    about: str | None = None
    photo: Photo | None = None

    @computed_field
    @property
    def full_name(self) -> str:
        name_parts = [self.first_name, self.last_name]
        return " ".join(part for part in name_parts if part)


class Meeting(BaseModel):
    id: int
    title: str
    discipline: Discipline
    creator_id: int | None
    created_at: datetime = Field(default_factory=datetime.now)
    status: MeetingStatus = MeetingStatus.CREATED
    duration: int = 5400
    description: str | None = None
    room: str | None = None
    datetime_: datetime | None = Field(None, alias="datetime")
    tutor_id: int | None = None

    def assign_tutor(self, tutor: "Tutor"):
        self.tutor_id = tutor.id

    def announce(self):
        self._check_for_announce()
        self.status = MeetingStatus.ANNOUNCED

    def set_approving(self):
        self._check_for_approval()
        if self.status != MeetingStatus.CREATED:
            raise ValueError("Cannot Send for Approval: it is not in CREATED status")
        self.status = MeetingStatus.APPROVING

    def discard_approval(self):
        if self.status != MeetingStatus.APPROVING:
            raise ValueError("Cannot Discard Approval: it is not in APPROVING status")
        self.status = MeetingStatus.CREATED

    def approve(self):
        if self.status != MeetingStatus.APPROVING:
            raise ValueError("Cannot Approve Meeting: it is not in APPROVING status")
        self.status = MeetingStatus.ANNOUNCED

    def conduct(self):
        if self.status != MeetingStatus.ANNOUNCED:
            raise ValueError("Cannot Conduct Meeting: it is not in ANNOUNCED status")
        self.status = MeetingStatus.CONDUCTING

    def finish(self):
        if self.status != MeetingStatus.CONDUCTING:
            raise ValueError("Cannot Finish Meeting: it is not in CONDUCTING status")
        self.status = MeetingStatus.FINISHED

    def adjust_duration_to_now(self):
        """Sets duration to the difference between `self.date` and `datetime.now`"""
        if not self.datetime_:
            raise ValueError("No meeting.date")
        real_duration = datetime.now() - self.datetime_
        self.duration = int(real_duration.total_seconds())

    def close(self):
        if self.status != MeetingStatus.FINISHED:
            raise ValueError("Cannot Close Meeting: it is not in FINISHED status")
        self.status = MeetingStatus.CLOSED

    @computed_field
    @property
    def duration_human(self) -> str:
        if self.duration:
            d = self.duration
            return f"{d // 3600:02d}:{(d % 3600) // 60:02d}"
        else:
            return "--:--"

    def _check_for_announce(self):
        if self.status != MeetingStatus.CREATED:
            raise ValueError("Cannot Announce Meeting: it is not in CREATED status")
        if self.room is None:
            raise ValueError("Cannot Announce Meeting: room is not set")
        if self.datetime_ is None:
            raise ValueError("Cannot Announce Meeting: date is not set")
        if self.datetime_ <= datetime.now():
            raise ValueError("Cannot Announce Meeting: date is in the past")
        if self.tutor_id is None:
            raise ValueError("Cannot Announce Meeting: tutor is not set")

    def _check_for_approval(self):
        if self.status != MeetingStatus.CREATED:
            raise ValueError("Cannot Send for Approval: it is not in CREATED status")
        if self.room is None:
            raise ValueError("Cannot Send for Approval: room is not set")
        if self.datetime_ is None:
            raise ValueError("Cannot Send for Approval: date is not set")
        if self.datetime_ <= datetime.now():
            raise ValueError("Cannot Send for Approval: date is in the past")
        if self.tutor_id is None:
            raise ValueError("Cannot Send for Approval: tutor is not set")


class Attendance(BaseModel):
    meeting_id: int
    emails: list[EmailStr] = []


class MeetingUpdate(BaseModel):
    id: int
    room: str | None = None
    datetime_: datetime | None = Field(None, alias="datetime")
