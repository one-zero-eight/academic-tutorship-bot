from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum


class UserStatus(StrEnum):
    student = "student"
    tutor = "tutor"
    admin = "admin"


class MeetingStatus(IntEnum):
    CREATED = 0
    ANNOUNCED = 1
    CONDUCTING = 2
    FINISHED = 3
    CLOSED = 4


@dataclass(frozen=True)
class InnoEmail(str):
    value: str

    def __post_init__(self):
        if not self.value.endswith("@innopolis.university"):
            raise ValueError(f"Invalid email: {self.value}")


class Meeting:
    """Meeting (Recap, Individual, etc)"""

    # Essential for creation
    id: int
    "Meeting id in Database"
    title: str
    "Meaningful Title (creation required)"
    _status: MeetingStatus = MeetingStatus.CREATED

    # Essential for announcement
    date: int | None = None
    "Date of the Meeting (seconds since epoch)"
    tutor: "Tutor | None" = None
    "Tutor conducting the Meeting"

    # Optional for announcement
    description: str | None = None
    "Description of the Meeting"
    _duration: int | None = None
    "Duration of the Meeting (seconds)"
    room: str | None = None
    "Room for the Meeting (any string)"

    # Essential for closing
    _attendance: list[InnoEmail] | None = None
    "List of emails of attendees"

    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title

    def assign_tutor(self, tutor: "Tutor"):
        self.tutor = tutor

    def announce(self):
        "To announce, date and tutor must be set"
        self._check_for_announce()
        self._status = MeetingStatus.ANNOUNCED

    def conduct(self):
        if self.status is not MeetingStatus.ANNOUNCED:
            raise ValueError("Cannot Conduct Meeting: it is not in ANNOUNCED status")
        self._status = MeetingStatus.CONDUCTING

    def finish(self):
        if self.status is not MeetingStatus.CONDUCTING:
            raise ValueError("Cannot Finish Meeting: it is not in CONDUCTING status")
        self._status = MeetingStatus.FINISHED

    def close(self, attendance: list[InnoEmail]):
        if self.status is not MeetingStatus.FINISHED:
            raise ValueError("Cannot Close Meeting: it is not in FINISHED status")
        self._attendance = attendance
        self._status = MeetingStatus.CLOSED

    @property
    def status(self) -> MeetingStatus:
        "Status of the Meeting"
        return self._status

    @property
    def duration(self) -> int | None:
        "Duration of the Meeting (seconds)"
        return self._duration

    @duration.setter
    def duration(self, value: int | None):
        if value is not None and value <= 0:
            raise ValueError("Duration must be positive")
        self._duration = value

    @property
    def attendance(self) -> list[InnoEmail] | None:
        "List of emails of attendees"
        return self._attendance

    @property
    def date_human(self) -> str:
        if self.date:
            return datetime.fromtimestamp(self.date).strftime("%d.%m.%y %H:%M")
        else:
            return "-.-.- -:-"

    def _check_for_announce(self):
        if self.status is not MeetingStatus.CREATED:
            raise ValueError("Cannot Announce Meeting: it is not in CREATED status")
        if self.date is None:
            raise ValueError("Cannot Announce Meeting: date is not set")
        if self.date < int(datetime.now().timestamp()):
            raise ValueError("Cannot Announce Meeting: date is in the past")
        if self.tutor is None:
            raise ValueError("Cannot Announce Meeting: tutor is not set")


class Tutor:
    id: int
    "ID in Database"
    tg_id: int
    "Telegram ID"

    _username: str | None = None
    "Telegram username"
    first_name: str | None = None
    "Telegram first name"
    last_name: str | None = None
    "Telegram last name"

    def __init__(
        self,
        id: int,
        tg_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ):
        self.id = id
        self.tg_id = tg_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    @property
    def username(self) -> str | None:
        return self._username

    @username.setter
    def username(self, value: str | None):
        if value:
            self._username = value.lstrip("@")
        else:
            self._username = None

    @property
    def full_name(self) -> str:
        name_parts = [self.first_name, self.last_name]
        return " ".join(part for part in name_parts if part)
