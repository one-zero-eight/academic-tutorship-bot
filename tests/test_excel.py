import io
import re
import zipfile
from datetime import datetime

import pytest

from src.domain.models import Discipline, Meeting, MeetingStatus, TutorWithEmail
from src.utils import excel

DISCIPLINE = Discipline(id=1, name="Math", year=1, semester=1, language="EN")


def _tutor(tutor_id: int = 1) -> TutorWithEmail:
    return TutorWithEmail(
        id=tutor_id,
        telegram_id=100 + tutor_id,
        email=f"tutor{tutor_id}@innopolis.university",
        username=f"tutor{tutor_id}",
        first_name="Test",
        last_name="Tutor",
    )


def _meeting(meeting_id: int, discipline: Discipline | None, tutor_id: int = 1) -> Meeting:
    return Meeting(
        id=meeting_id,
        title=f"Meeting {meeting_id}",
        discipline=discipline,
        creator_id=None,
        status=MeetingStatus.CLOSED,
        **{"datetime": datetime(2026, 3, 10, 12, 0)},
        room="101",
        tutor_id=tutor_id,
    )


def _sheet_strings(buffer: io.BytesIO) -> list[str]:
    with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
        shared_strings = archive.read("xl/sharedStrings.xml").decode()
    return re.findall(r"<t[^>]*>(.*?)</t>", shared_strings, re.S)


def test_no_meetings_gives_zero_stats():
    data = excel.FullSpreadsheetData([_tutor()], [], [], max_ipts=10, max_pts=10)

    assert data.mean_meetings_count == 0.0
    assert data.avg_attendance == 0.0
    assert data.maximal_attendance == 0
    assert data.ipts_per_tutor == [0]


def test_no_tutors_gives_zero_mean():
    data = excel.FullSpreadsheetData([], [], [], max_ipts=10, max_pts=10)

    assert data.mean_meetings_count == 0.0
    assert data.ipts_per_tutor == []


def test_discipline_less_meetings_do_not_break_export():
    meetings = [_meeting(1, discipline=None)]

    buffer = excel.create_full_spreadsheet([_tutor()], meetings, [[]], max_ipts=10, max_pts=10)

    assert isinstance(buffer, io.BytesIO)
    assert buffer.getvalue()


def test_meetings_without_discipline_are_excluded():
    meetings = [_meeting(1, DISCIPLINE), _meeting(2, discipline=None)]
    attendance = [["student@innopolis.university"], []]

    buffer = excel.create_full_spreadsheet([_tutor()], meetings, attendance, max_ipts=10, max_pts=10)
    strings = " | ".join(_sheet_strings(buffer))

    assert "Meeting 1" in strings
    assert "Meeting 2" not in strings


@pytest.mark.parametrize("meetings", [[], [_meeting(1, discipline=None)]])
def test_export_without_usable_meetings(meetings):
    """Regression: filtered-out meetings must not cause ZeroDivisionError."""
    attendance = [[] for _ in meetings]

    buffer = excel.create_full_spreadsheet([_tutor()], meetings, attendance, max_ipts=10, max_pts=10)

    assert buffer.getvalue()
