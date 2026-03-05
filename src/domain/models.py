from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum

from email_validator import validate_email


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
class Email(str):
    ALLOWED_DOMAINS = [
        "innopolis.university",
        "innopolis.ru",
    ]

    value: str

    def __post_init__(self):
        email_info = validate_email(self.value)
        if email_info.domain not in self.ALLOWED_DOMAINS:
            raise ValueError(f'"{self.value}" is not in innopolis domain')


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
    _duration: int = 5400  # 01:30
    "Duration of the Meeting (seconds)"
    room: str | None = None
    "Room for the Meeting (any string)"

    # Essential for closing
    _attendance: list[Email] | None = None
    "List of emails of attendees"

    def __repr__(self) -> str:
        return (
            f"Meeting(id={self.id}, status={self.status.name}, "
            f"title={self.title}, date={self.date_human}, "
            f"duration={self.duration}, room={self.room}, "
            f"tutor={self.tutor}"
            ")"
        )

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
        if self.status != MeetingStatus.ANNOUNCED:
            raise ValueError("Cannot Conduct Meeting: it is not in ANNOUNCED status")
        self._status = MeetingStatus.CONDUCTING

    def finish(self):
        if self.status != MeetingStatus.CONDUCTING:
            raise ValueError("Cannot Finish Meeting: it is not in CONDUCTING status")
        self._status = MeetingStatus.FINISHED

    def adjust_duration_to_now(self):
        """Sets duration to the difference between `self.date` and `datetime.now`"""
        if not self.date:
            raise ValueError("No meeting.date")
        date_obj = datetime.fromtimestamp(self.date)
        real_duration = datetime.now() - date_obj
        self.duration = int(real_duration.total_seconds())

    def close(self, attendance: list[Email]):
        if self.status != MeetingStatus.FINISHED:
            raise ValueError("Cannot Close Meeting: it is not in FINISHED status")
        self._attendance = attendance
        self._status = MeetingStatus.CLOSED

    @property
    def status(self) -> MeetingStatus:
        "Status of the Meeting"
        return self._status

    @property
    def duration(self) -> int:
        "Duration of the Meeting (seconds)"
        return self._duration

    @duration.setter
    def duration(self, value: int):
        if value is not None and value <= 0:
            raise ValueError("Duration must be positive")
        self._duration = value

    @property
    def attendance(self) -> list[Email] | None:
        "List of emails of attendees"
        return self._attendance

    @property
    def date_human(self) -> str:
        if self.date:
            return datetime.fromtimestamp(self.date).strftime("%d.%m.%y %H:%M")
        else:
            return "--.--.---- --:--"

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

    def __repr__(self) -> str:
        return f"Tutor(id={self.id}, tg_id={self.tg_id}, username={self.username}, ...)"

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


class TutorProfile:
    id: int
    "ID in database, same as Tutor.id"
    full_name: str
    "Real name"
    _username: str | None
    "Telegram username (without @)"
    discipline: str
    "Teaching discipline"
    photo_id: str | None
    "Telegram ID of profile photo"
    about: str | None
    "Description by him/herself"

    def __repr__(self) -> str:
        return f"TutorProfile(id={self.id}, full_name={self.full_name}, ...)"

    def __init__(
        self, id: int, full_name: str, username: str | None, discipline: str, photo_id: str | None, about: str | None
    ):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.discipline = discipline
        self.photo_id = photo_id
        self.about = about

    @property
    def username(self) -> str | None:
        return self._username

    @username.setter
    def username(self, value: str | None):
        if value:
            self._username = value.lstrip("@")
        else:
            self._username = None
