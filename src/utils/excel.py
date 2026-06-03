import calendar
import io
from collections.abc import Callable

import pandas as pd
import xlsxwriter
from xlsxwriter.worksheet import Worksheet

from src.domain.models import Meeting, MeetingStatus, Tutor, TutorWithEmail

ORDINAL = {1: "st", 2: "nd", 3: "rd", 4: "th"}


class FullSpreadsheetData:
    tutors: list[TutorWithEmail]
    meetings: list[Meeting]
    attendance: list[list[str]]
    max_ipts: float
    max_pts: float

    id_per_tutor: list[int]
    username_per_tutor: list[str | None]
    full_name_per_tutor: list[str]
    profile_name_per_tutor: list[str | None]
    email_per_tutor: list[str]

    meetings_count_per_tutor: list[int]
    total_attendance_count_per_tutor: list[int]
    unique_attendance_count_per_tutor: list[int]
    recap_points_per_tutor: list[int]
    tentative_points_per_tutor: list[int]
    ipts_per_tutor: list[int]
    scaled_points_per_tutor: list[int]
    sus_list: list[TutorWithEmail]

    mean_meetings_count: float
    avg_attendance: float
    involved_tutors: int
    total_involved_students: int
    unique_involved_students: int
    maximal_attendance: int

    top_students_by_attendance: list[tuple[str, int]]

    def __init__(
        self,
        tutors: list[TutorWithEmail],
        meetings: list[Meeting],
        attendance: list[list[str]],
        max_ipts: float,
        max_pts: float,
    ):
        self.tutors = sorted(tutors, key=lambda t: t.id)
        self.meetings = meetings
        self.attendance = attendance
        self.max_ipts = max_ipts
        self.max_pts = max_pts
        self.__calculate_derivatives()

    def __calculate_derivatives(self):
        self.id_per_tutor = [t.id for t in self.tutors]
        self.username_per_tutor = [f"@{t.username}" for t in self.tutors]
        self.full_name_per_tutor = [t.full_name for t in self.tutors]
        self.profile_name_per_tutor = [t.profile_name for t in self.tutors]
        self.email_per_tutor = [t.email for t in self.tutors]

        self.meetings_count_per_tutor = []
        self.total_attendance_count_per_tutor = []
        self.unique_attendance_count_per_tutor = []
        self.recap_points_per_tutor = []
        self.tentative_points_per_tutor = []

        for tutor in self.tutors:
            recap_points = 0
            tentative_points = 0
            total_attendance = 0
            unique_attendance = set()
            count = 0
            for i, meeting in enumerate(self.meetings):
                if meeting.status != MeetingStatus.CLOSED:
                    continue
                if meeting.tutor_id == tutor.id:
                    count += 1
                    recap_points += len(self.attendance[i]) > 0
                    tentative_points += len(self.attendance[i]) == 0
                    total_attendance += len(self.attendance[i])
                    unique_attendance.update(self.attendance[i])

            self.meetings_count_per_tutor.append(count)
            self.total_attendance_count_per_tutor.append(total_attendance)
            self.unique_attendance_count_per_tutor.append(len(unique_attendance))
            self.recap_points_per_tutor.append(recap_points)
            self.tentative_points_per_tutor.append(tentative_points)

        self.mean_meetings_count = sum(self.meetings_count_per_tutor) / len(self.tutors)
        self.sus_list = [t for i, t in enumerate(self.tutors) if self.meetings_count_per_tutor[i] == 0]

        attendance_counts = [len(a) for a in self.attendance]
        all_attendees = [email for meeting_attendance in self.attendance for email in meeting_attendance]
        unique_attendees = list(set(all_attendees))
        self.avg_attendance = sum(attendance_counts) / len(attendance_counts)
        self.total_involved_students = sum(attendance_counts)
        self.unique_involved_students = len(unique_attendees)
        self.maximal_attendance = max(attendance_counts)

        self.involved_tutors = len(self.tutors) - len(self.sus_list)

        student_counts = {}
        for email in all_attendees:
            student_counts[email] = student_counts.get(email, 0) + 1

        students_attendances = []
        for email in unique_attendees:
            students_attendances.append((email, student_counts[email]))

        self.top_students_by_attendance = sorted(students_attendances, key=lambda s: s[1])

        self.ipts_per_tutor = []
        self.scaled_points_per_tutor = []

        ratio = self.max_ipts / self.max_pts

        for i, t in enumerate(self.tutors):
            meetings_count = self.meetings_count_per_tutor[i]
            if meetings_count >= self.mean_meetings_count:
                ipts = round(self.max_ipts)
            elif meetings_count > 0:
                ipts = round(meetings_count / self.mean_meetings_count * self.max_ipts)
            else:
                ipts = 0
            self.ipts_per_tutor.append(ipts)
            self.scaled_points_per_tutor.append(round(ipts / ratio))


def create_full_spreadsheet(
    tutors: list[TutorWithEmail],
    meetings: list[Meeting],
    attendance: list[list[str]],
    max_ipts: int,
    max_pts: int,
) -> io.BytesIO:
    """Creates xlsx spreadsheet with data in format:

    `Complicated format`

    Returns the xlsx file in `io.BytesIO`
    """

    data = FullSpreadsheetData(tutors, meetings, attendance, max_ipts, max_pts)

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    _create_tracking_sheet(workbook, data)
    _create_attendance_sheet(workbook, data)
    _create_exporting_sheet(workbook, data)

    workbook.close()
    return buffer


def _create_tracking_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData):
    worksheet = workbook.add_worksheet("Tracking Sheet")
    after_tutors_i = __fill_tracking_sheet_tutors(worksheet, data)
    __fill_tracking_sheet_meetings(worksheet, data, after_tutors_i)
    worksheet.autofit()


def _create_attendance_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData):
    worksheet = workbook.add_worksheet("Attendance Sheet")
    __fill_attendance_sheet_meetings(worksheet, data)
    worksheet.autofit()


def _create_exporting_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData):
    worksheet = workbook.add_worksheet("Exporting Sheet")
    after_tutors_i = __fill_exporting_sheet_tutors(worksheet, data)
    __fill_exporting_sheet_constants(worksheet, data, after_tutors_i + 1)
    __fill_exporting_sheet_sus_list(worksheet, data, after_tutors_i + 1)
    __fill_exporting_sheet_statistics(worksheet, data, after_tutors_i + 5)
    worksheet.autofit()


def __fill_exporting_sheet_constants(worksheet: Worksheet, data: FullSpreadsheetData, initial_col: int):
    CONSTANTS = [
        ("Mean value", round(data.mean_meetings_count, 3)),
        ("MAX_PTS", data.max_pts),
        ("MAX_IPTS", data.max_ipts),
    ]

    for col, (title, value) in enumerate(CONSTANTS, start=initial_col):
        worksheet.write(1, col, title)
        worksheet.write(2, col, value)


def __fill_exporting_sheet_sus_list(worksheet: Worksheet, data: FullSpreadsheetData, initial_col: int):
    worksheet.write(5, initial_col + 1, "Sus List")
    for row, tutor in enumerate(data.sus_list, start=6):
        worksheet.merge_range(row, initial_col, row, initial_col + 2, tutor.email)


def __fill_exporting_sheet_statistics(worksheet: Worksheet, data: FullSpreadsheetData, initial_col: int):
    STATISTICS = [
        ("Total # of recaps", len(data.meetings)),
        ("Average Attendance", data.avg_attendance),
        ("Involved Tutors", data.involved_tutors),
        ("Unique Involved Students", data.unique_involved_students),
        ("Total Involved Students", data.total_involved_students),
        ("Maximal Attendance", data.maximal_attendance),
    ]

    worksheet.merge_range(4, initial_col, 4, initial_col + 1, "Statistics")
    for row, (name, value) in enumerate(STATISTICS, start=5):
        worksheet.write(row, initial_col, name)
        worksheet.write(row, initial_col + 1, value)

    worksheet.merge_range(row + 1, initial_col, row + 1, initial_col + 1, "Top 3 Students (Attendance)")
    for row, (email, attendance) in enumerate(data.top_students_by_attendance[:3], start=row + 2):
        worksheet.write(row, initial_col, email)
        worksheet.write(row, initial_col + 1, attendance)


def __fill_tracking_sheet_tutors(worksheet: Worksheet, data: FullSpreadsheetData) -> int:
    """Fill data table with tutors info, return index of next column after the table"""

    ADDITIONAL_COLUMNS = [
        ("Recap points", data.recap_points_per_tutor),
        ("Tentative points", data.tentative_points_per_tutor),
        ("Compensation", [0 for _ in range(len(data.tutors))]),
    ]

    return __add_tutors_list(worksheet, data, ADDITIONAL_COLUMNS, freeze=True)


def __add_tutors_list(
    worksheet: Worksheet, data: FullSpreadsheetData, additional_columns: list[tuple[str, list]], *, freeze: bool = False
) -> int:
    DEFAULT_COLUMNS = [
        "ID",
        "Telegram name",
        "Profile name",
        "Telegram alias",
        "Innopolis e-mail",
    ]
    for i, title in enumerate(DEFAULT_COLUMNS):
        worksheet.merge_range(0, i, 2, i, title)

    for i, (title, _data) in enumerate(additional_columns, start=i + 1):
        worksheet.merge_range(0, i, 2, i, title)

    width = len(DEFAULT_COLUMNS) + len(additional_columns)
    if freeze:
        worksheet.freeze_panes(0, width)

    for i, tutor in enumerate(data.tutors):
        row_i = i + 3
        worksheet.write(row_i, 0, tutor.id)
        worksheet.write(row_i, 1, tutor.full_name)
        worksheet.write(row_i, 2, tutor.profile_name)
        worksheet.write(row_i, 3, f"@{tutor.username}")
        worksheet.write(row_i, 4, tutor.email)
        for j, (title, _data) in enumerate(additional_columns):
            worksheet.write(row_i, 5 + j, _data[i])

    return width


def __fill_tracking_sheet_meetings(worksheet: Worksheet, data: FullSpreadsheetData, initial_col: int):
    worksheet.merge_range(0, initial_col, 2, initial_col, "AT Bot Recaps")

    for i, count in enumerate(data.meetings_count_per_tutor, start=3):
        worksheet.write(i, initial_col, count)

    def func(worksheet: Worksheet, data: FullSpreadsheetData, col: int, m: Meeting):
        try:
            if m.tutor_id is not None:
                tutor_i = data.id_per_tutor.index(m.tutor_id)
                worksheet.write(tutor_i + 3, col, "TRUE")
        except ValueError:
            pass

    __add_horizontal_meeting_list(worksheet, data, initial_col + 1, func)


def __add_horizontal_meeting_list(
    worksheet: Worksheet,
    data: FullSpreadsheetData,
    initial_col: int,
    func: Callable[[Worksheet, FullSpreadsheetData, int, Meeting], None],
):
    """
    Adds horizontal meetings list, sorted by date, categorized by month + academic year.

    Pass in `func` to do something on each meeting addition to spreadsheet.
    The func should receive (worksheet, sheet_data, sheet_column, meeting), see signature.
    """

    def sorting_key_by__year_month_acad_year(m: Meeting):
        assert m.datetime_
        return (m.datetime_.year, m.datetime_.month, m.discipline.year)

    meetings_with_date = filter(lambda m: m.datetime_ is not None, data.meetings)
    sorted_meetings = sorted(meetings_with_date, key=sorting_key_by__year_month_acad_year)

    if not sorted_meetings:
        return

    prev_month_year_col = initial_col

    first_m = sorted_meetings[0]
    assert first_m.datetime_
    (month, year, acad_year) = (first_m.datetime_.month, first_m.datetime_.year, first_m.discipline.year)

    for col, m in enumerate(sorted_meetings, start=initial_col):
        assert m.datetime_
        assert m.tutor_id

        (m_month, m_year, m_acad_year) = (m.datetime_.month, m.datetime_.year, m.discipline.year)

        if (month, year, acad_year) != (m_month, m_year, m_acad_year):
            __write_meeting_month_year_heading(
                worksheet, month, year, acad_year, start_col=prev_month_year_col, end_col=col - 1
            )
            prev_month_year_col = col

        worksheet.write(1, col, m.title)
        worksheet.write(2, col, m.datetime_.strftime("%d.%m.%Y"))

        # YOUR CODE HERE
        func(worksheet, data, col, m)
        # END OF YOUR CODE

        (month, year, acad_year) = (m_month, m_year, m_acad_year)

    __write_meeting_month_year_heading(worksheet, month, year, acad_year, prev_month_year_col, col)


def __write_meeting_month_year_heading(
    worksheet: Worksheet, month: int, year: int, acad_year: int, start_col: int, end_col: int
):
    month_year_title = __get_month_year_title(month, acad_year, year)
    if start_col == end_col:
        worksheet.write(0, start_col, month_year_title)
    else:
        worksheet.merge_range(0, start_col, 0, end_col, month_year_title)


def __get_month_year_title(month: int, acad_year: int, current_year: int) -> str:
    month_name = calendar.month_name[month]
    suffix = ORDINAL.get(acad_year, "")
    return f"{month_name}, {current_year} ({acad_year}{suffix} Year)"


def __fill_attendance_sheet_meetings(worksheet: Worksheet, data: FullSpreadsheetData):

    def func(worksheet: Worksheet, data: FullSpreadsheetData, col: int, m: Meeting):
        mi = data.meetings.index(m)
        m_attendance = data.attendance[mi]
        worksheet.write(3, col, len(m_attendance))
        for row, attendee_email in enumerate(m_attendance, start=4):
            worksheet.write(row, col, attendee_email)

    __add_horizontal_meeting_list(worksheet, data, 0, func)


def __fill_exporting_sheet_tutors(worksheet: Worksheet, data: FullSpreadsheetData) -> int:
    ADDITIONAL_COLUMNS = [
        ("Scaled Points", data.scaled_points_per_tutor),
        ("IPTS", data.ipts_per_tutor),
    ]
    return __add_tutors_list(worksheet, data, ADDITIONAL_COLUMNS)


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
