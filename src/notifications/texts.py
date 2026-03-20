BOT_STARTED = """
<a href="{link}">Academic Tutorship Bot</a> has been started 🚀
"""

BOT_SHUTDOWN = """
<a href="{link}">Academic Tutorship Bot</a> has been shut down 💤
"""

MEETING_UPDATED_TITLE = """
Changed title for meeting "{old_title}"
- New title: "{title}"

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_UPDATED_ROOM = """
Changed room for meeting "{title}"
- New room: {room}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_UPDATED_DATETIME = """
Changed date for meeting "{title}"
- New date & time: {datetime}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_UPDATED_TUTOR = """
Changed tutor for meeting "{title}"
- New tutor: @{username}

🔗 <a href="{link}">Click to see the details</a>
"""
"Text for when new tutor is assigned to meeting, for all interested students (must be formatted)"


TUTOR_PROMOTED_FOR_ADMINS = """
The student {full_name} @{username} was promoted to being a tutor
"""
"Text for admins about tutor promotion (must be formatted)"


TUTOR_PROMOTED_FOR_TUTOR = """
You've been promoted to being a tutor!

- Restart the bot (<a href="https://t.me/academic_notifications_bot?start=promoted_tutor">click here</a>)
- Fill up your tutor profile
"""
"Text for the tutor about his promotion"


TUTOR_DISMISSED_FOR_ADMINS = """
The student {full_name} @{username} is dismissed from being a tutor
"""
"Text for admins about tutor dismission (must be formatted)"


TUTOR_DISMISSED_FOR_TUTOR = """
You've been dismissed from being a tutor

Your tutor profile won't be shown to students anymore
"""
"Text for the tutor about his dismission"


TUTOR_ASSIGNED_FOR_ADMINS = """
Tutor @{username} assigned to meeting "{title}"
- Date & time: {datetime}
- Room: {room}

🔗 <a href="{link}">Click to see the details</a>
"""

TUTOR_ASSIGNED_FOR_TUTOR = """
You have been assigned to meeting "{title}"!
- Date & time: {datetime}
- Room: {room}

🔗 <a href="{link}">Click to see the details</a>
"""

TUTOR_CHANGED_FOR_ADMINS = """
Tutor changed for meeting "{title}"
- Old tutor: @{old_username}
- New tutor: @{new_username}

🔗 <a href="{link}">Click to see the details</a>
"""

TUTOR_CHANGED_FOR_NEW_TUTOR = """
You have been assigned as the new tutor for meeting "{title}".
- Date & time: {datetime}
- Room: {room}

🔗 <a href="{link}">Click to see the details</a>
"""

TUTOR_CHANGED_FOR_OLD_TUTOR = """
You are no longer the tutor for meeting "{title}".
"""

TUTOR_CHANGED_FOR_STUDENTS = """
Changed tutor for meeting "{title}"
- New tutor: @{new_username}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_CANCELLED = """
Meeting "{title}" has been cancelled.
"""

MEETING_REMINDER = """
Reminder: Meeting "{title}" is upcoming!
- Date & time: {datetime}
- Room: {room}
- Tutor: @{username}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_ANNOUNCED = """
New meeting upcoming!
"{title}"
- Date & time: {datetime}
- Room: {room}
- Tutor: @{username}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_STARTED = """
Meeting has started!
"{title}"
- Room: {room}
- Tutor: @{username}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_FINISHED = """
Meeting has finished!
"{title}"

‼️ Remember to upload the attendance file

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_CLOSED_FOR_ADMINS = """
Meeting has been closed by the tutor.
"{title}"

👥 Attendance count: {attendance_count}
"""

MEETING_CLOSED_FOR_TUTOR = """
Meeting has been closed by the admin.
"{title}"
👥 Attendance count: {attendance_count}

🔗 <a href="{link}">Click to see the details</a>
"""


MEETING_APPROVE_REQUEST = """
Meeting "{title}" is awaiting approval.
- Date & time: {datetime}
- Room: {room}
- Tutor: @{username}

🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_CONFIRM_APPROVE_APPENDIX = "The meeting will be <u>automatically announced to students</u>. Are you sure?"


MEETING_APPROVED = """
Meeting "{title}" has been approved!
🔗 <a href="{link}">Click to see the details</a>
"""

MEETING_DISCARDED = """
Meeting "{title}" has been discarded

Reason:
{reason}

🔗 <a href="{link}">Click to see the details</a>
"""
