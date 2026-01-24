from typing import TypedDict

from src.domain.models import Email, Meeting, MeetingStatus, Tutor


class TutorDTO(TypedDict):
    id: int
    tg_id: int

    username: str | None
    first_name: str | None
    last_name: str | None


class MeetingDTO(TypedDict):
    id: int
    title: str
    status: int

    tutor: TutorDTO | None
    description: str | None
    room: str | None
    date: int | None
    duration: int
    attendance: list[str] | None


def tutor_to_dto(tutor: Tutor | None) -> TutorDTO | None:
    if tutor is not None:
        return TutorDTO(
            id=tutor.id,
            tg_id=tutor.tg_id,
            username=tutor.username,
            first_name=tutor.first_name,
            last_name=tutor.last_name,
        )


def dto_to_tutor(dto: TutorDTO | None) -> Tutor | None:
    if dto is not None:
        return Tutor(
            id=dto["id"],
            tg_id=dto["tg_id"],
            username=dto["username"],
            first_name=dto["first_name"],
            last_name=dto["last_name"],
        )


def meeting_to_dto(meeting: Meeting | None) -> MeetingDTO | None:
    if meeting is not None:
        return MeetingDTO(
            id=meeting.id,
            title=meeting.title,
            status=meeting.status.value,
            tutor=tutor_to_dto(meeting.tutor) if meeting.tutor else None,
            description=meeting.description,
            room=meeting.room,
            date=meeting.date,
            duration=meeting.duration,
            attendance=[e.value for e in meeting.attendance] if meeting.attendance else None,
        )


def dto_to_meeting(dto: MeetingDTO | None) -> Meeting | None:
    # The process is a bit manual due to the private attributes
    if dto is not None:
        meeting = Meeting(
            id=dto["id"],
            title=dto["title"],
        )
        meeting._status = MeetingStatus(dto["status"])
        if dto["attendance"]:
            meeting._attendance = [Email(e) for e in dto["attendance"]]
        meeting.description = dto["description"]
        meeting.room = dto["room"]
        meeting.date = dto["date"]
        meeting.duration = dto["duration"]
        if tutor := dto_to_tutor(dto["tutor"]):
            meeting.assign_tutor(tutor)
        return meeting
