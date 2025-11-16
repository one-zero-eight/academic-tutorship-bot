from datetime import datetime

from pydantic import BaseModel

# Meeting Status
CREATED = 0
ANNOUNCED = 1
CONDUCTING = 2
FINISHED = 3
CLOSED = 4


class Meeting(BaseModel):
    """Meeting (Recap, Individual, etc)"""

    # Status of a Meeting
    status: int = CREATED
    # Meeting id in Database
    id: int
    # Meaningful Title (creation required)
    title: str

    # Description of the Meeting
    description: str | None = None
    # Date of the Meeting (seconds since epoch)
    date: int | None = None
    # Duration of the Meeting (seconds)
    duration: int | None = None
    # Assigned Tutor user_id in Database
    tutor_id: int | None = None
    # Assigned Tutor username in Database
    tutor_username: str | None = None
    # Room for the Meeting (any string)
    room: str | None = None

    @property
    def date_human(self) -> str:
        if self.date:
            return datetime.fromtimestamp(self.date).strftime("%d.%m.%y")
        else:
            return "-.-.-"


class User(BaseModel):
    """User (Student or Tutor)"""

    # User id in Database
    id: int
    # Flag if the User is tutor
    is_tutor: bool
