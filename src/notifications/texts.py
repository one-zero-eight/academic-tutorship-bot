MEETING_UPDATED_ROOM = """
Changed room for meeting {title}
- New room: {room}
"""

MEETING_UPDATED_DATETIME = """
Changed date for meeting {title}
- New date & time: {datetime}
"""

MEETING_UPDATED_TUTOR = """
Changed tutor for meeting {title}
- New tutor: @{username}
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
Tutor @{username} assigned to meeting '{title}'
- Date & time: {datetime}
- Room: {room}
"""

TUTOR_ASSIGNED_FOR_TUTOR = """
You have been assigned to meeting '{title}'!
- Date & time: {datetime}
- Room: {room}
Please check your schedule.
"""

TUTOR_CHANGED_FOR_ADMINS = """
Tutor changed for meeting '{title}'
- Old tutor: @{old_username}
- New tutor: @{new_username}
"""

TUTOR_CHANGED_FOR_NEW_TUTOR = """
You have been assigned as the new tutor for meeting '{title}'.
- Date & time: {datetime}
- Room: {room}
Please check your schedule.
"""

TUTOR_CHANGED_FOR_OLD_TUTOR = """
You are no longer the tutor for meeting '{title}'.
"""

MEETING_CANCELLED = """
Meeting '{title}' has been cancelled.
"""

MEETING_REMINDER = """
Reminder: Meeting '{title}' is upcoming!
- Date & time: {datetime}
- Room: {room}
"""

# TODO:
# - Meeting Announced
# - Meeting Started (for everyone)
# - Meeting Finished (for everyone)
#     - for tutors, reminder to send the attendance file (with link?)
# - Meeting Closed (for admins)
