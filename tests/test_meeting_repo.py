from datetime import datetime

import pytest
from sqlalchemy import insert

from src.db.repositories import MeetingRepository
from src.db.schema import meeting
from src.domain.models import MeetingStatus


async def _create_closed_meeting(db, datetime_: datetime | None) -> int:
    async with db.engine.begin() as conn:
        result = await conn.execute(
            insert(meeting)
            .values(title="Test meeting", status=MeetingStatus.CLOSED.value, datetime=datetime_)
            .returning(meeting.c.id)
        )
        return result.scalar_one()


@pytest.mark.asyncio
async def test_get_list_filters_by_datetime_bounds(db, meeting_repo: MeetingRepository):
    inside = await _create_closed_meeting(db, datetime(2026, 9, 1, 12, 0))
    await _create_closed_meeting(db, datetime(2026, 8, 14, 23, 59))
    await _create_closed_meeting(db, datetime(2027, 1, 1, 0, 0))
    await _create_closed_meeting(db, None)

    meetings = await meeting_repo.get_list(
        MeetingStatus.CLOSED,
        datetime_from=datetime(2026, 8, 15),
        datetime_to=datetime(2026, 12, 31, 23, 59, 59, 999999),
    )

    assert [m.id for m in meetings] == [inside]


@pytest.mark.asyncio
async def test_get_list_without_datetime_bounds_is_unfiltered(db, meeting_repo: MeetingRepository):
    ids = [
        await _create_closed_meeting(db, datetime(2026, 9, 1, 12, 0)),
        await _create_closed_meeting(db, datetime(2027, 1, 1, 0, 0)),
        await _create_closed_meeting(db, None),
    ]

    meetings = await meeting_repo.get_list(MeetingStatus.CLOSED)

    assert sorted(m.id for m in meetings) == sorted(ids)
