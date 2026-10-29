import calendar
import io
from collections.abc import Callable

import pandas as pd
import xlsxwriter
from xlsxwriter.color import Color
from xlsxwriter.worksheet import Worksheet

from src.domain.models import Meeting, MeetingStatus, Tutor, TutorWithEmail

ORDINAL = {1: "st", 2: "nd", 3: "rd", 4: "th"}

MONTH_COLORS = []


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

        self.mean_meetings_count = sum(self.meetings_count_per_tutor) / len(self.tutors) if self.tutors else 0.0
        self.sus_list = [t for i, t in enumerate(self.tutors) if self.meetings_count_per_tutor[i] == 0]

        attendance_counts = [len(a) for a in self.attendance]
        all_attendees = [email for meeting_attendance in self.attendance for email in meeting_attendance]
        unique_attendees = list(set(all_attendees))
        self.avg_attendance = sum(attendance_counts) / len(attendance_counts) if attendance_counts else 0.0
        self.total_involved_students = sum(attendance_counts)
        self.unique_involved_students = len(unique_attendees)
        self.maximal_attendance = max(attendance_counts, default=0)

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
            if meetings_count == 0:
                ipts = 0
            elif meetings_count >= self.mean_meetings_count:
                ipts = round(self.max_ipts)
            else:
                ipts = round(meetings_count / self.mean_meetings_count * self.max_ipts)
            self.ipts_per_tutor.append(ipts)
            self.scaled_points_per_tutor.append(round(ipts / ratio))


class CellFormats:
    def __init__(self, workbook: xlsxwriter.Workbook):
        gray_bg = {"bg_color": Color("#BEBEBE")}
        self.red_bg_borders = workbook.add_format({"border": 1, "bg_color": Color("#fc4e4e")})
        self.yellow_bg_borders = workbook.add_format({"border": 1, "bg_color": Color("#f9fc4e")})
        self.gray_bg = workbook.add_format(gray_bg)
        self.darker_gray_bg_borders = workbook.add_format({"bg_color": Color("#9F9F9F"), "border": 1})
        self.green_bg = workbook.add_format({"bg_color": Color("#a0fc99")})
        self.borders = workbook.add_format({"border": 1})
        self.gray_bg_borders = workbook.add_format({**gray_bg, "border": 1})
        self.month_bg = [
            workbook.add_format({"border": 1, "bg_color": Color("#35a85b")}),  # Jan
            workbook.add_format({"border": 1, "bg_color": Color("#4f9ded")}),  # Feb
            workbook.add_format({"border": 1, "bg_color": Color("#f2b84b")}),  # Mar
            workbook.add_format({"border": 1, "bg_color": Color("#d96ad9")}),  # Apr
            workbook.add_format({"border": 1, "bg_color": Color("#4fc3b3")}),  # May
            workbook.add_format({"border": 1, "bg_color": Color("#f07a6a")}),  # Jun
            workbook.add_format({"border": 1, "bg_color": Color("#8e7df2")}),  # Jul
            workbook.add_format({"border": 1, "bg_color": Color("#c4d94f")}),  # Aug
            workbook.add_format({"border": 1, "bg_color": Color("#f29c4b")}),  # Sep
            workbook.add_format({"border": 1, "bg_color": Color("#6ab0f0")}),  # Oct
            workbook.add_format({"border": 1, "bg_color": Color("#e06a8d")}),  # Nov
            workbook.add_format({"border": 1, "bg_color": Color("#7cc96f")}),  # Dec
        ]
        self.month_darker_bg = [
            workbook.add_format({"border": 1, "bg_color": Color("#2a8448")}),  # Jan
            workbook.add_format({"border": 1, "bg_color": Color("#3f7dc0")}),  # Feb
            workbook.add_format({"border": 1, "bg_color": Color("#c8923c")}),  # Mar
            workbook.add_format({"border": 1, "bg_color": Color("#af55af")}),  # Apr
            workbook.add_format({"border": 1, "bg_color": Color("#3d9a8e")}),  # May
            workbook.add_format({"border": 1, "bg_color": Color("#c06054")}),  # Jun
            workbook.add_format({"border": 1, "bg_color": Color("#7163c2")}),  # Jul
            workbook.add_format({"border": 1, "bg_color": Color("#9cad3f")}),  # Aug
            workbook.add_format({"border": 1, "bg_color": Color("#c67d3c")}),  # Sep
            workbook.add_format({"border": 1, "bg_color": Color("#558cc0")}),  # Oct
            workbook.add_format({"border": 1, "bg_color": Color("#b05570")}),  # Nov
            workbook.add_format({"border": 1, "bg_color": Color("#629f58")}),  # Dec
        ]


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

    filtered = [(m, a) for m, a in zip(meetings, attendance, strict=True) if m.discipline is not None]
    meetings = [m for m, _ in filtered]
    attendance = [a for _, a in filtered]

    data = FullSpreadsheetData(tutors, meetings, attendance, max_ipts, max_pts)

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    formats = CellFormats(workbook)

    _create_tracking_sheet(workbook, data, formats)
    _create_attendance_sheet(workbook, data, formats)
    _create_exporting_sheet(workbook, data, formats)

    workbook.close()
    return buffer


def _create_tracking_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData, formats: CellFormats):
    worksheet = workbook.add_worksheet("Tracking Sheet")
    after_tutors_i = __fill_tracking_sheet_tutors(worksheet, data, formats)
    __fill_tracking_sheet_meetings(worksheet, data, formats, after_tutors_i)
    worksheet.autofit()


def _create_attendance_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData, formats: CellFormats):
    worksheet = workbook.add_worksheet("Attendance Sheet")
    __fill_attendance_sheet_meetings(worksheet, data, formats)
    worksheet.autofit()


def _create_exporting_sheet(workbook: xlsxwriter.Workbook, data: FullSpreadsheetData, formats: CellFormats):
    worksheet = workbook.add_worksheet("Exporting Sheet")
    after_tutors_i = __fill_exporting_sheet_tutors(worksheet, data, formats)
    __fill_exporting_sheet_constants(worksheet, data, formats, after_tutors_i + 1)
    __fill_exporting_sheet_sus_list(worksheet, data, formats, after_tutors_i + 1)
    __fill_exporting_sheet_statistics(worksheet, data, formats, after_tutors_i + 5)
    worksheet.autofit()
    worksheet.set_column_pixels(1, after_tutors_i + 1, 64)


def __fill_exporting_sheet_constants(
    worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats, initial_col: int
):
    CONSTANTS = [
        ("Mean value", round(data.mean_meetings_count, 3)),
        ("MAX_PTS", data.max_pts),
        ("MAX_IPTS", data.max_ipts),
    ]

    for col, (title, value) in enumerate(CONSTANTS, start=initial_col):
        worksheet.write(1, col, title, formats.gray_bg_borders)
        worksheet.write(2, col, value, formats.borders)


def __fill_exporting_sheet_sus_list(
    worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats, initial_col: int
):
    worksheet.write(5, initial_col + 1, "Sus List", formats.gray_bg_borders)
    for row, tutor in enumerate(data.sus_list, start=6):
        worksheet.merge_range(row, initial_col, row, initial_col + 2, tutor.email, formats.borders)


def __fill_exporting_sheet_statistics(
    worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats, initial_col: int
):
    STATISTICS = [
        ("Total # of recaps", len(data.meetings)),
        ("Average Attendance", data.avg_attendance),
        ("Involved Tutors", data.involved_tutors),
        ("Unique Involved Students", data.unique_involved_students),
        ("Total Involved Students", data.total_involved_students),
        ("Maximal Attendance", data.maximal_attendance),
    ]

    worksheet.merge_range(4, initial_col, 4, initial_col + 1, "Statistics", formats.darker_gray_bg_borders)
    for row, (name, value) in enumerate(STATISTICS, start=5):
        worksheet.write(row, initial_col, name, formats.gray_bg_borders)
        worksheet.write(row, initial_col + 1, value, formats.borders)

    worksheet.merge_range(
        row + 1, initial_col, row + 1, initial_col + 1, "Top 3 Students (Attendance)", formats.darker_gray_bg_borders
    )
    for row, (email, attendance) in enumerate(data.top_students_by_attendance[:3], start=row + 2):
        worksheet.write(row, initial_col, email, formats.borders)
        worksheet.write(row, initial_col + 1, attendance, formats.borders)


def __fill_tracking_sheet_tutors(worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats) -> int:
    """Fill data table with tutors info, return index of next column after the table"""

    ADDITIONAL_COLUMNS = [
        ("Recap points", data.recap_points_per_tutor),
        ("Tentative points", data.tentative_points_per_tutor),
        ("Compensation", [0 for _ in range(len(data.tutors))]),
    ]

    return __add_tutors_list(worksheet, data, formats, ADDITIONAL_COLUMNS, freeze=True)


def __add_tutors_list(
    worksheet: Worksheet,
    data: FullSpreadsheetData,
    formats: CellFormats,
    additional_columns: list[tuple[str, list]],
    *,
    freeze: bool = False,
) -> int:
    DEFAULT_COLUMNS = [
        "ID",
        "Telegram name",
        "Profile name",
        "Telegram alias",
        "Innopolis e-mail",
    ]
    for i, title in enumerate(DEFAULT_COLUMNS):
        worksheet.merge_range(0, i, 2, i, title, formats.gray_bg_borders)

    for i, (title, _data) in enumerate(additional_columns, start=i + 1):
        worksheet.merge_range(0, i, 2, i, title, formats.gray_bg_borders)

    width = len(DEFAULT_COLUMNS) + len(additional_columns)
    if freeze:
        worksheet.freeze_panes(0, width)

    for i, tutor in enumerate(data.tutors):
        row_i = i + 3
        if data.recap_points_per_tutor[i] == 0:
            if data.tentative_points_per_tutor[i] > 0:
                tutor_format = formats.yellow_bg_borders
            else:
                tutor_format = formats.red_bg_borders
        else:
            tutor_format = formats.borders

        worksheet.write(
            row_i, 0, tutor.id, tutor_format if tutor_format != formats.borders else formats.gray_bg_borders
        )
        worksheet.write(row_i, 1, tutor.full_name, tutor_format)
        worksheet.write(row_i, 2, tutor.profile_name, tutor_format)
        worksheet.write(row_i, 3, f"@{tutor.username}", tutor_format)
        worksheet.write(row_i, 4, tutor.email, tutor_format)
        for j, (title, _data) in enumerate(additional_columns):
            worksheet.write(row_i, 5 + j, _data[i], tutor_format)

    return width


def __fill_tracking_sheet_meetings(
    worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats, initial_col: int
):
    worksheet.merge_range(0, initial_col, 2, initial_col, "AT Bot Recaps", formats.gray_bg_borders)

    for i, count in enumerate(data.meetings_count_per_tutor, start=3):
        worksheet.write(i, initial_col, count, formats.borders)

    def func(worksheet: Worksheet, data: FullSpreadsheetData, col: int, m: Meeting):
        try:
            if m.tutor_id is not None:
                tutor_i = data.id_per_tutor.index(m.tutor_id)
                worksheet.write(tutor_i + 3, col, "TRUE", formats.green_bg)
        except ValueError:
            pass

    __add_horizontal_meeting_list(worksheet, data, formats, initial_col + 1, func)


def __add_horizontal_meeting_list(
    worksheet: Worksheet,
    data: FullSpreadsheetData,
    formats: CellFormats,
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
                worksheet, formats, month, year, acad_year, start_col=prev_month_year_col, end_col=col - 1
            )
            prev_month_year_col = col

        worksheet.write(1, col, m.title, formats.month_bg[m_month - 1])
        worksheet.write(2, col, m.datetime_.strftime("%d.%m.%Y"), formats.month_bg[m_month - 1])

        # YOUR CODE HERE
        func(worksheet, data, col, m)
        # END OF YOUR CODE

        (month, year, acad_year) = (m_month, m_year, m_acad_year)

    __write_meeting_month_year_heading(worksheet, formats, month, year, acad_year, prev_month_year_col, col)


def __write_meeting_month_year_heading(
    worksheet: Worksheet, formats: CellFormats, month: int, year: int, acad_year: int, start_col: int, end_col: int
):
    month_year_title = __get_month_year_title(month, acad_year, year)
    if start_col == end_col:
        worksheet.write(0, start_col, month_year_title, formats.month_darker_bg[month - 1])
    else:
        worksheet.merge_range(0, start_col, 0, end_col, month_year_title, formats.month_darker_bg[month - 1])


def __get_month_year_title(month: int, acad_year: int, current_year: int) -> str:
    month_name = calendar.month_name[month]
    suffix = ORDINAL.get(acad_year, "")
    return f"{month_name}, {current_year} ({acad_year}{suffix} Year)"


def __fill_attendance_sheet_meetings(worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats):

    def func(worksheet: Worksheet, data: FullSpreadsheetData, col: int, m: Meeting):
        mi = data.meetings.index(m)
        m_attendance = data.attendance[mi]
        month = m.datetime_.month if m.datetime_ else 1
        worksheet.write(3, col, len(m_attendance), formats.month_darker_bg[month - 1])
        START_FROM = 4
        for row, attendee_email in enumerate(m_attendance, start=START_FROM):
            if row - START_FROM in [0, len(m_attendance) - 1]:
                row_format = formats.month_darker_bg[month - 1]
            else:
                row_format = None
            worksheet.write(row, col, attendee_email, row_format)

    __add_horizontal_meeting_list(worksheet, data, formats, 0, func)


def __fill_exporting_sheet_tutors(worksheet: Worksheet, data: FullSpreadsheetData, formats: CellFormats) -> int:
    ADDITIONAL_COLUMNS = [
        ("Scaled Points", data.scaled_points_per_tutor),
        ("IPTS", data.ipts_per_tutor),
    ]
    return __add_tutors_list(worksheet, data, formats, ADDITIONAL_COLUMNS)


def create_minimal_spreadsheet(tutors: list[Tutor], meetings: list[Meeting]) -> io.BytesIO:
    """Creates xlsx spreadsheet with data in format:

    Academic Tutor | Number of Meetings | Total Attendance

    Returns the xlsx file in `io.BytesIO`
    """

    meetings = [m for m in meetings if m.discipline is not None]

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
