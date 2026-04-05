COMMON_BTN_BACK = Back
COMMON_BTN_CANCEL = Cancel
COMMON_BTN_SUBMIT = Submit
COMMON_BTN_CLOSE = Close
COMMON_BTN_DISCARD = Discard


AUTH_BIND_INSTRUCTION =
    To proceed, please, connect your Telegram with your InNoHassle Account by pressing the button "Connect Telegram 🔗"

    After that, press "Check Connection ✅"
AUTH_BTN_CONNECT_TELEGRAM = Connect Telegram 🔗
AUTH_BTN_CHECK_CONNECTED = Check Connection ✅

GUIDE_LANGUAGE_TEXT =
    Before we start, choose your language:
GUIDE_LANGUAGE_BTN_EN = English 🇬🇧
GUIDE_LANGUAGE_BTN_RU = Русский 🇷🇺


GUIDE_INIT_TEXT =
    Hello, student!
    My name is ArThur, I am the bot of Academic Tutorship (AT for short).

    The system helps to keep track of meetings (recaps, consultations) on various university disciplines of your choice.
GUIDE_DISCIPLINES_TEXT =
    You may choose the disciplines you're interested in.

    Or skip and do that later in ⚙️ <b>Settings</b>.
GUIDE_DISCIPLINES_NONE_SELECTED = 📚 No disciplines selected yet
GUIDE_DISCIPLINES_SELECTED_TITLE = 📚 Selected Disciplines
GUIDE_NOTIFICATIONS_TEXT =
    A huge part of my value is sending notifications about upcoming meetings.

    We deliver notifications in a different bot.
    Please, activate it 👇 to continue:
    🔗 <a href="{$link}"><i>Academic Notifications Bot</i></a>

    (you may later block notifications in ⚙️ <b>Settings</b>)
GUIDE_BTN_NEXT = Next ➡️
GUIDE_BTN_BACK = ⬅️ Back
GUIDE_BTN_SKIP = Skip ➡️
GUIDE_BTN_FINISH = Finish guide 🎉


ROOT_START_STUDENT =
    Hello there, {$first_name}! 👋
    I'm ArThur, and I will help you to keep track of upcoming Academic Tutorship meetings
ROOT_START_TUTOR_APPENDIX = 🧑‍🏫 <i>Honorable Academic Tutor you are</i>
ROOT_START_ADMIN_APPENDIX = 👑 <i>Your Majesty, you have full bot access</i>

ROOT_BTN_UPCOMING_MEETINGS = 📚 Upcoming Meetings
ROOT_BTN_TUTORS = 🧑‍🏫 Academic Tutors
ROOT_BTN_SETTINGS = ⚙️ Settings

ROOT_BTN_YOUR_MEETINGS = 🧑‍🏫 Your Meetings
ROOT_BTN_YOUR_PROFILE = 🧑‍🏫 Your Profile

ROOT_BTN_MEETINGS_CONTROL = ⚙️ Meetings Control
ROOT_BTN_TUTORS_CONTROL = ⚙️ Academic Tutors


SETTINGS_HEADING =
    ⚙️ Settings️

    📚 Relevant Disciplines:

SETTINGS_DISCIPLINE_ITEM = - [{$language} {$year}y] {$name}
SETTINGS_NOTIFICATIONS_LINK = 🔗 <i><a href='{$notification_bot_link}'>link to Notifications Bot</a></i>
SETTINGS_NOTIF_UNACTIVATED = Activate bot ☝️ to receive notifications
SETTINGS_NOTIF_BLOCKED = Unblock the bot ☝️ to receive notifications

SETTINGS_NOTIF_TOGGLE = Notifications: {$receive_notifications}
SETTINGS_LANG_TOGGLE = Language: {$current_language}
SETTINGS_BTN_CHANGE_DISCIPLINES = 📚 Change Disciplines

SETTINGS_DISCIPLINES_TITLE = 📚 Selected Disciplines
SETTINGS_DISCIPLINES_BTN_CHOOSE = Choose
SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER = Choose other


DISCIPLINE_PICKER_LANGUAGE_TITLE = Choose Program
DISCIPLINE_PICKER_YEAR_TITLE = Choose Academic Year
DISCIPLINE_PICKER_DISCIPLINE_TITLE = Choose Discipline
DISCIPLINE_PICKER_DISCIPLINES_TITLE = Choose Disciplines


MEETINGS_TYPE_TITLE = Meetings
MEETINGS_BTN_CREATE_NEW = Create New
MEETINGS_BTN_SEE_CREATED = See Created
MEETINGS_BTN_SEE_APPROVING = See Approving
MEETINGS_BTN_SEE_ANNOUNCED = See Announced
MEETINGS_BTN_SEE_CLOSED = See Closed

MEETINGS_LIST_CREATED_TITLE = Created Meetings
MEETINGS_LIST_APPROVING_TITLE = Approving Meetings
MEETINGS_LIST_ANNOUNCED_TITLE = Announced Meetings
MEETINGS_LIST_CLOSED_TITLE = Closed Meetings

MEETING_CREATE_TITLE =
    Create New Meeting
    Title: {$title}
    Discipline: {$discipline_name}

MEETING_CREATE_BTN_TITLE = Title
MEETING_CREATE_BTN_DISCIPLINE = Discipline
MEETING_CREATE_BTN_SUBMIT = Create ✅

MEETING_CREATE_ENTER_TITLE_TITLE =
    Create New Meeting
    Discipline: {$discipline_name}
    Enter Title:

MEETING_INFO_HEADER = ℹ️ Meeting Information
MEETING_INFO_TITLE_LINE = <b>{$title}</b>
MEETING_INFO_DISCIPLINE_LINE = [{$d_lang} {$d_year}y] {$d_name}
MEETING_INFO_DATE_LINE = 📆 Date: <b>{$date}</b>
MEETING_INFO_DURATION_LINE = ⏱️ Duration: <b>{$duration}</b>
MEETING_INFO_ROOM_LINE = 📍 Room: <b>{$room}</b>
MEETING_INFO_TUTOR_LINE = 🧑‍🏫 Tutor: @{$tutor_username}
MEETING_INFO_ADMIN_STATUS_LINE = Status: <b>{$status_name}</b>
MEETING_INFO_ADMIN_ATTENDANCE_LINE = Attendance: <b>{$attendance_count}</b>
MEETING_INFO_DESCRIPTION_HEADER = Description:
MEETING_INFO_DESCRIPTION_BLOCK = <blockquote>{$description}</blockquote>

MEETING_INFO_BTN_CHANGE_INFO = Change Info
MEETING_INFO_BTN_SEND_FOR_APPROVAL = Send for Approval
MEETING_INFO_BTN_ANNOUNCE = Announce
MEETING_INFO_BTN_FINISH = Finish
MEETING_INFO_BTN_CLOSE = Close
MEETING_INFO_BTN_ATTENDANCE = Attendance
MEETING_INFO_BTN_CANCEL_MEETING = Cancel Meeting

MEETING_CONFIRM_SEND_FOR_APPROVAL_TITLE =
    Are you sure that you want to send "{$title}" for approval?
    After approval, the meeting will be <u>announced automatically</u>.
MEETING_CONFIRM_SEND_FOR_APPROVAL_BTN = Send for Approval 📩

MEETING_CONFIRM_ANNOUNCE_TITLE = Are you sure that you want to announce "{$title}"?
MEETING_CONFIRM_ANNOUNCE_BTN = Announce 📣

MEETING_CONFIRM_FINISH_TITLE = Are you sure that you want to finish "{$title}"?
MEETING_CONFIRM_FINISH_BTN = Finish ☑️

MEETING_CONFIRM_DELETE_TITLE =
    Are you sure that you want to cancel "{$title}"?
    This action cannot be undone and the meeting will be deleted.
MEETING_CONFIRM_DELETE_STUDENT_NOTIF_APPENDIX = The notification will be sent to students 💌
MEETING_CONFIRM_DELETE_BTN = Cancel Meeting 🗑️

STUDENT_MEETINGS_LIST_TITLE = Upcoming Meetings
STUDENT_MEETING_BTN_TUTOR_PROFILE = Academic Tutor Profile
STUDENT_MEETING_BTN_TO_YOUR_PROFILE = To Your Profile


CHANGE_INFO_BTN_SET_TITLE = Title
CHANGE_INFO_BTN_TITLE_DISCIPLINE = Title & Discipline
CHANGE_INFO_BTN_SET_DESCRIPTION = Description
CHANGE_INFO_BTN_SET_ROOM = Room
CHANGE_INFO_BTN_SET_DATE = Date
CHANGE_INFO_BTN_DATE_ROOM = Date & Room
CHANGE_INFO_BTN_SET_DURATION = Duration
CHANGE_INFO_BTN_ASSIGN_TUTOR = Academic Tutor

CHANGE_SET_TITLE_PROMPT = Enter new Title for "{$title}"
CHANGE_SET_DESCRIPTION_PROMPT = Enter new Description for "{$title}"
CHANGE_SET_ROOM_PROMPT = Enter new Room for "{$title}"
CHANGE_SET_DATE_PROMPT = Enter new Date for "{$title}"
CHANGE_SET_TIME_PROMPT =
    Enter new Time for "{$title}"
    Adhere to format 00:00, e.g. 20:32
CHANGE_SET_DURATION_PROMPT =
    Enter new Duration for "{$title}"
    In format "hh:mm"
CHANGE_ASSIGN_TUTOR_TITLE =
    Assign Academic Tutor to "{$title}"
    Here's the list of all Academic Tutors:


ATTENDANCE_BTN_RESEND_FILE = Resend File
ATTENDANCE_BTN_ADD_EMAIL = Add email
ATTENDANCE_BTN_DOWNLOAD_FILE = Download File
ATTENDANCE_RESEND_TITLE = Resend attendance file for "{$title}"
ATTENDANCE_CLOSE_TITLE = Send attendance file to close "{$title}"
ATTENDANCE_ADD_EMAIL_PROMPT = Enter the email to add 👤


TUTORS_ADMIN_LIST_TITLE = Academic Tutors List
TUTORS_ADMIN_INFO =
    Academic Tutor [{$id}] Info
    {$full_name}
    @{$username}
    Telegram ID: <code>{$telegram_id}</code>
TUTORS_ADMIN_BTN_ADD_NEW = Add New
TUTORS_ADMIN_BTN_DISMISS = Dismiss
TUTORS_ADMIN_BTN_PROFILE = Profile
TUTORS_ADMIN_BTN_EDIT_PROFILE = Edit Profile
TUTORS_ADMIN_ADD_PROMPT = Share contact of the new Academic Tutor


TUTOR_LIST_TITLE_FOR_STUDENTS = 🧑‍🏫 Here are all Academic Tutors!

TUTOR_PROFILE_HEADER_STUDENT_VIEW = 🧑‍🏫 Academic Tutor's Profile
TUTOR_PROFILE_PROFILE_NAME_LINE = <b>{$profile_name}</b>
TUTOR_PROFILE_USERNAME_LINE = @{$username}
TUTOR_PROFILE_DISCIPLINES_HEADER = 📚 Disciplines:
TUTOR_PROFILE_ABOUT_BLOCK = <blockquote>{$about}</blockquote>


TUTOR_PROFILE_LIST_TITLE = 🧑‍🏫 Here are all of your Academic Tutors!
TUTOR_PROFILE_HEADER_TUTOR_VIEW = 🧑‍🏫 Your Academic Tutor's Profile
TUTOR_PROFILE_CONTROL_BTN_NAME = Profile Name
TUTOR_PROFILE_CONTROL_BTN_ABOUT = About
TUTOR_PROFILE_CONTROL_BTN_DISCIPLINES = Disciplines
TUTOR_PROFILE_SET_NAME =
    Enter Profile Name
    This name will be available to students
TUTOR_PROFILE_SET_ABOUT =
    Write something about yourself
    This will be available to students
TUTOR_PROFILE_SELECT_DISCIPLINES_TITLE = Selected Disciplines


MEETING_UPDATE_HEADER = Updates in meeting:
MEETING_UPDATE_DATETIME_LINE = - Date: {$datetime}
MEETING_UPDATE_ROOM_LINE = - Room: {$room}

MEETING_UPDATE_BACK_HEADER =
    You have some unsaved changes, discard them or go back?
MEETING_UPDATE_SAVE_HEADER =
    ☝️ The meetings was already announced so date & room update should be approved by head of AT.
    Send the request?
MEETING_UPDATE_BTN_SAVE = Save 💾
MEETING_UPDATE_BTN_SEND = Send
