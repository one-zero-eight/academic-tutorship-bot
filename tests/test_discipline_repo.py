from datetime import datetime, timedelta

import pytest
from sqlalchemy import insert

from src.config import settings as app_settings
from src.db.repositories import DisciplineRepository, MeetingRepository, StudentRepository, TutorRepository
from src.db.repositories.discipline import DisciplineInUseError
from src.db.schema import meeting
from src.domain.models import Meeting, MeetingStatus
from tests.fixtures import *


async def _create_meeting(db, discipline_id: int, status: MeetingStatus) -> int:
    async with db.engine.begin() as conn:
        result = await conn.execute(
            insert(meeting)
            .values(title="Test meeting", discipline_id=discipline_id, status=status.value)
            .returning(meeting.c.id)
        )
        return result.scalar_one()


@pytest.mark.asyncio
async def test_exists_returns_false_after_deletion(discipline_repo: DisciplineRepository):
    created = await discipline_repo.create("EN", 1, 1, "Vanishing")

    assert await discipline_repo.exists(created.id) is True

    await discipline_repo.delete(id=created.id)

    assert await discipline_repo.exists(created.id) is False


@pytest.mark.asyncio
async def test_delete_unused_discipline(discipline_repo: DisciplineRepository):
    created = await discipline_repo.create("EN", 1, 1, "Unused")

    deleted = await discipline_repo.delete(id=created.id)

    assert deleted is not None
    assert deleted.id == created.id
    assert await discipline_repo.get_full_list() == []


@pytest.mark.asyncio
async def test_delete_discipline_detaches_created_and_closed_meetings(
    db, discipline_repo: DisciplineRepository, meeting_repo: MeetingRepository
):
    discipline = await discipline_repo.create("EN", 1, 1, "Detachable")
    created_id = await _create_meeting(db, discipline.id, MeetingStatus.CREATED)
    closed_id = await _create_meeting(db, discipline.id, MeetingStatus.CLOSED)

    deleted = await discipline_repo.delete(id=discipline.id)

    assert deleted is not None
    assert await discipline_repo.get_full_list() == []
    assert (await meeting_repo.get(created_id)).discipline is None
    assert (await meeting_repo.get(closed_id)).discipline is None
    assert [m.id for m in await meeting_repo.get_list(MeetingStatus.CREATED)] == [created_id]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [MeetingStatus.APPROVING, MeetingStatus.ANNOUNCED, MeetingStatus.CONDUCTING, MeetingStatus.FINISHED],
)
async def test_delete_discipline_blocks_in_flight_meetings(
    db, discipline_repo: DisciplineRepository, meeting_repo: MeetingRepository, status: MeetingStatus
):
    discipline = await discipline_repo.create("EN", 1, 1, "In use")
    blocked_id = await _create_meeting(db, discipline.id, status)

    with pytest.raises(DisciplineInUseError) as exc_info:
        await discipline_repo.delete(id=discipline.id)

    assert exc_info.value.discipline.id == discipline.id
    assert [meeting.id for meeting in exc_info.value.meetings] == [blocked_id]
    assert exc_info.value.meetings[0].title == "Test meeting"
    assert exc_info.value.meetings[0].status == status
    assert [d.id for d in await discipline_repo.get_full_list()] == [discipline.id]
    meeting_ = await meeting_repo.get(blocked_id)
    assert meeting_.discipline is not None
    assert meeting_.discipline.id == discipline.id


@pytest.mark.asyncio
async def test_delete_discipline_removes_student_and_tutor_links(
    db,
    discipline_repo: DisciplineRepository,
    student_repo: StudentRepository,
    tutor_repo: TutorRepository,
    monkeypatch,
):
    monkeypatch.setattr(app_settings, "admins", [])
    discipline = await discipline_repo.create("EN", 1, 1, "Linked")
    student = await student_repo.create(
        telegram_id=100,
        first_name="Test",
        last_name="Student",
        username="teststudent",
        email_="test.student@innopolis.university",
    )
    await student_repo.set_relevant_disciplines(student.telegram_id, [discipline.id])
    await tutor_repo.create(student.id)
    await tutor_repo.set_disciplines(student.id, [discipline])

    await discipline_repo.delete(id=discipline.id)

    assert await student_repo.get_relevant_disciplines(student.telegram_id) == []
    assert await tutor_repo.get_disciplines(student.id) == []


def test_meeting_requires_discipline_to_move_forward():
    meeting_ = Meeting(
        id=1,
        title="No discipline",
        discipline=None,
        creator_id=None,
        room="101",
        **{"datetime": datetime.now() + timedelta(days=1)},
        tutor_id=1,
    )

    with pytest.raises(ValueError, match="discipline is not set"):
        meeting_.announce()
    with pytest.raises(ValueError, match="discipline is not set"):
        meeting_.set_approving()
