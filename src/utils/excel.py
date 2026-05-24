import io

import pandas as pd

from src.domain.models import Meeting, Tutor


def create_minimal_spreadsheet(tutors: list[Tutor], meetings: list[Meeting]) -> io.BytesIO:
    """Creates xlsx spreadsheet with data in format:

    Academic Tutor | Number of Meetings | Total Attendance

    Returns the xlsx file in `io.BytesIO`
    """

    tutor_usernames = [f"@{t.username}" if t.username else "-" for t in tutors]
    tutor_full_names = [t.full_name for t in tutors]
    tutor_profile_names = [t.profile_name for t in tutors]
    meetings_count_per_tutor = []
    for tutor in tutors:
        count = 0
        for meeting in meetings:
            count += meeting.tutor_id == tutor.id
        meetings_count_per_tutor.append(count)

    df = pd.DataFrame(
        {
            "AT TG Username": tutor_usernames,
            "AT TG Name": tutor_full_names,
            "AT Profile Name": tutor_profile_names,
            "# of Meetings": meetings_count_per_tutor,
        }
    )

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")

    return buffer
