COMMON_BTN_BACK = Back
COMMON_BTN_CANCEL = Cancel
COMMON_BTN_SUBMIT = Submit
COMMON_BTN_CLOSE = Close

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
SETTINGS_BTN_CHANGE_DISCIPLINES = 📚 Change Disciplines

SETTINGS_DISCIPLINES_TITLE = 📚 Selected Disciplines
SETTINGS_DISCIPLINES_BTN_CHOOSE = Choose
SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER = Choose other


DISCIPLINE_PICKER_LANGUAGE_TITLE = Choose Program
DISCIPLINE_PICKER_YEAR_TITLE = Choose Academic Year
DISCIPLINE_PICKER_DISCIPLINE_TITLE = Choose Discipline
DISCIPLINE_PICKER_DISCIPLINES_TITLE = Choose Disciplines


STUDENT_MEETINGS_LIST_TITLE = Upcoming Meetings
STUDENT_MEETING_BTN_TUTOR_PROFILE = Academic Tutor Profile
STUDENT_MEETING_BTN_TO_YOUR_PROFILE = To Your Profile
TUTOR_LIST_TITLE_FOR_STUDENTS = 🧑‍🏫 Here are all Academic Tutors!
TUTOR_PROFILE_HEADER_STUDENT_VIEW = 🧑‍🏫 Academic Tutor's Profile
TUTOR_PROFILE_PROFILE_NAME_LINE = <b>{$profile_name}</b>
TUTOR_PROFILE_USERNAME_LINE = @{$username}
TUTOR_PROFILE_DISCIPLINES_HEADER = 📚 Disciplines:
TUTOR_PROFILE_DISCIPLINE_ITEM = - <b>[{$discipline[language]} {$discipline[year]}y] {$discipline[name]}</b>
TUTOR_PROFILE_ABOUT_BLOCK = <blockquote>{$about}</blockquote>
AUTH_BIND_INSTRUCTION =
    To proceed, please, connect your Telegram with your InNoHassle Account by pressing the button "Connect Telegram 🔗"

    After that, press "Check Connection ✅"
AUTH_BTN_CONNECT_TELEGRAM = Connect Telegram 🔗
AUTH_BTN_CHECK_CONNECTED = Check Connection ✅
MEETING_INFO_TEMPLATE_STUDENT =
    ℹ️ Meeting Information

    <b>{$title}</b>
    {"["}{$d_lang} {$d_year}y] {$d_name}

    📆 Date: <b>{$date}</b>
    ⏱️ Duration: <b>{$duration}</b>
    📍 Room: <b>{$room}</b>
    🧑‍🏫 Academic Tutor: @{$tutor_username}

    Description:
    <blockquote>{$description}</blockquote>
MEETINGS_TYPE_TITLE = Meetings
MEETINGS_BTN_CREATE_NEW = Create New
MEETINGS_BTN_SEE_CREATED = See Created
MEETINGS_BTN_SEE_APPROVING = See Approving
MEETINGS_BTN_SEE_ANNOUNCED = See Announced
MEETINGS_BTN_SEE_CLOSED = See Closed
MEETINGS_LIST_TITLE = {$meetings_type} Meetings
MEETING_CREATE_TITLE = New Meeting
MEETING_CREATE_FIELD_TITLE = Title: {$title}
MEETING_CREATE_FIELD_DISCIPLINE = Discipline: {$discipline_name}
MEETING_CREATE_BTN_TITLE = Title
MEETING_CREATE_BTN_DISCIPLINE = Discipline
MEETING_CREATE_BTN_SUBMIT = Create ✅
MEETING_CREATE_ENTER_TITLE_TITLE = Create New Meeting
MEETING_CREATE_ENTER_TITLE_PROMPT = Enter Title:
MEETING_INFO_BTN_CHANGE_INFO = Change Info
MEETING_INFO_BTN_SEND_FOR_APPROVAL = Send for Approval
MEETING_INFO_BTN_ANNOUNCE = Announce
MEETING_INFO_BTN_FINISH = Finish
MEETING_INFO_BTN_CLOSE = Close
MEETING_INFO_BTN_ATTENDANCE = Attendance
MEETING_INFO_BTN_CANCEL_MEETING = Cancel Meeting
MEETING_CONFIRM_SEND_FOR_APPROVAL_TITLE = Are you sure that you want to send "{$title}" for approval?
MEETING_CONFIRM_SEND_FOR_APPROVAL_APPENDIX = After approval, the meeting will be <u>announced automatically</u>.
MEETING_CONFIRM_SEND_FOR_APPROVAL_BTN = Send for Approval 📩
MEETING_CONFIRM_ANNOUNCE_TITLE = Are you sure that you want to announce "{$title}"?
MEETING_CONFIRM_ANNOUNCE_BTN = Announce 📣
MEETING_CONFIRM_FINISH_TITLE = Are you sure that you want to finish "{$title}"?
MEETING_CONFIRM_FINISH_BTN = Finish ☑️
MEETING_CONFIRM_DELETE_TITLE = Are you sure that you want to cancel "{$title}"?
MEETING_CONFIRM_DELETE_APPENDIX = This action cannot be undone and the meeting will be deleted.
MEETING_CONFIRM_DELETE_STUDENT_NOTIFY = The notification will be sent to students 💌
MEETING_CONFIRM_DELETE_BTN = Cancel Meeting 🗑️
CHANGE_INFO_BTN_SET_TITLE = Set Title
CHANGE_INFO_BTN_SET_DESCRIPTION = Set Description
CHANGE_INFO_BTN_SET_ROOM = Set Room
CHANGE_INFO_BTN_SET_DATE = Set Date
CHANGE_INFO_BTN_SET_DURATION = Set Duration
CHANGE_SET_TITLE_PROMPT = Enter new Title for "{$title}"
CHANGE_SET_DESCRIPTION_PROMPT = Enter new Description for "{$title}"
CHANGE_SET_ROOM_PROMPT = Enter new Room for "{$title}"
CHANGE_SET_DATE_PROMPT = Enter new Date for "{$title}"
CHANGE_SET_TIME_PROMPT = Enter new Time for "{$title}"
CHANGE_SET_TIME_FORMAT_HINT = Adhere to format 00:00, e.g. 20:32
CHANGE_SET_DURATION_PROMPT = Enter new Duration for "{$title}"
CHANGE_SET_DURATION_FORMAT_HINT = In format "hh:mm"
ATTENDANCE_BTN_RESEND_FILE = Resend File
ATTENDANCE_BTN_ADD_EMAIL = Add email
ATTENDANCE_BTN_DOWNLOAD_FILE = Download File
ATTENDANCE_RESEND_TITLE = Resend attendance file for "{$title}"
ATTENDANCE_CLOSE_TITLE = Send attendance file to close "{$title}"
ATTENDANCE_ADD_EMAIL_PROMPT = Enter the email to add 👤
TUTOR_PROFILE_HEADER_TUTOR_VIEW = 🧑‍🏫 Your Academic Tutor's Profile
TUTOR_PROFILE_CONTROL_BTN_NAME = Profile Name
TUTOR_PROFILE_CONTROL_BTN_ABOUT = About
TUTOR_PROFILE_CONTROL_BTN_DISCIPLINES = Disciplines
TUTOR_PROFILE_SET_NAME_PROMPT = Enter Profile Name
TUTOR_PROFILE_SET_NAME_HINT = This name will be available to students
TUTOR_PROFILE_SET_ABOUT_PROMPT = Write something about yourself
TUTOR_PROFILE_SET_ABOUT_HINT = This will be available to students
TUTOR_PROFILE_SELECT_DISCIPLINES_TITLE = Selected Disciplines
TUTOR_PROFILE_BTN_CHOOSE_OTHER = Choose other
TUTOR_PROFILE_BTN_SUBMIT = Submit
NOTIF_TUTOR_PROMOTED_FOR_TUTOR =
    You've been promoted to an Academic Tutor!

    - Restart the bot (<a href="{$link}">click here</a>)
    - Fill up your Academic Tutor profile"
NOTIF_TUTOR_DISMISSED_FOR_TUTOR =
    You've been dismissed from being an Academic Tutor.

    Your Academic Tutor profile won't be shown to students anymore.
NOTIF_TUTOR_ASSIGNED_FOR_TUTOR =
    You have been assigned to meeting "{$title}"!

    - Date & time: {$datetime}
    - Room: {$room}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_TUTOR_CHANGED_FOR_NEW_TUTOR =
    You have been assigned as the new Academic Tutor for meeting "{$title}".
    - Date & time: {$datetime}
    - Room: {$room}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_TUTOR_CHANGED_FOR_OLD_TUTOR = You are no longer the Academic Tutor for meeting "{$title}".
NOTIF_MEETING_FINISHED =
    Meeting has finished!
    "{$title}"

    ‼️ Remember to upload the attendance file

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_CLOSED_FOR_TUTOR =
    Meeting has been closed by the admin.
    "{$title}"
    👥 Attendance count: {$attendance_count}

    🔗 <a href="{$link}">Click to see the details</a>
CHANGE_INFO_BTN_ASSIGN_TUTOR = Assign Academic Tutor
CHANGE_ASSIGN_TUTOR_TITLE = Assign Academic Tutor to "{$title}"
CHANGE_ASSIGN_TUTOR_HINT = Here's the list of all Academic Tutors:
TUTORS_ADMIN_LIST_TITLE = Academic Tutors List
TUTORS_ADMIN_BTN_ADD_NEW = Add New
TUTORS_ADMIN_INFO_TITLE = Academic Tutor [{$id}] Info
TUTORS_ADMIN_INFO_FULL_NAME = {$full_name}
TUTORS_ADMIN_INFO_USERNAME = @{$username}
TUTORS_ADMIN_INFO_TELEGRAM_ID = Telegram ID: <code>{$telegram_id}</code>
TUTORS_ADMIN_BTN_DISMISS = Dismiss
TUTORS_ADMIN_BTN_PROFILE = Profile
TUTORS_ADMIN_BTN_EDIT_PROFILE = Edit Profile
TUTORS_ADMIN_ADD_PROMPT = Share contact of the new Academic Tutor
MEETING_INFO_ADMIN_STATUS = Status: <b>{$status.name}</b>
MEETING_INFO_ADMIN_ATTENDANCE = Attendance: <b>{$attendance_count}</b>
NOTIF_BOT_STARTED = <a href="{$link}">Academic Tutorship Bot</a> has been started 🚀
NOTIF_BOT_SHUTDOWN = <a href="{$link}">Academic Tutorship Bot</a> has been shut down 💤
NOTIF_MEETING_UPDATED_TITLE =
    Changed title for meeting "{$old_title}"
    - New title: "{$title}"

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_UPDATED_ROOM =
    Changed room for meeting "{$title}"
    - New room: {$room}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_UPDATED_DATETIME =
    Changed date for meeting "{$title}"
    - New date & time: {$datetime}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_UPDATED_TUTOR =
    Changed tutor for meeting "{$title}"
    - New tutor: @{$username}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_TUTOR_PROMOTED_FOR_ADMINS = The student {$full_name} @{$username} was promoted to being an Academic Tutor
NOTIF_TUTOR_DISMISSED_FOR_ADMINS = The student {$full_name} @{$username} is dismissed from being an Academic Tutor
NOTIF_TUTOR_ASSIGNED_FOR_ADMINS =
    Academic Tutor @{$username} assigned to meeting "{$title}"
    - Date & time: {$datetime}
    - Room: {$room}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_TUTOR_CHANGED_FOR_ADMINS =
    Academic Tutor changed for meeting "{$title}"
    - Old Academic Tutor: @{$old_username}
    - New Academic Tutor: @{$new_username}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_CLOSED_FOR_ADMINS =
    Meeting has been closed by the tutor.
    "{$title}"

    👥 Attendance count: {$attendance_count}
NOTIF_MEETING_APPROVE_REQUEST =
    Meeting "{$title}" is awaiting approval.
    - Date & time: {$datetime}
    - Room: {$room}
    - Academic Tutor: @{$username}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_CONFIRM_APPROVE_APPENDIX = The meeting will be <u>automatically announced to students</u>. Are you sure?
NOTIF_MEETING_APPROVED =
Meeting "{$title}" has been approved!
🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_DISCARDED =
    Meeting "{$title}" has been discarded

    Reason:
    <blockquote>{$reason}</blockquote>

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_CANCELLED_FOR_USERS =
    Meeting "{$title}" has been cancelled 😞
    Sorry for the inconvenience. We hope to see you in other meetings!
NOTIF_MEETING_REMINDER =
    Reminder: Meeting "{$title}" is upcoming!
    - Date & time: {$datetime}
    - Room: {$room}
    - Academic Tutor: @{$username}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_ANNOUNCED =
    New meeting upcoming!
    "{$title}"
    - Date & time: {$datetime}
    - Room: {$room}
    - Academic Tutor: @{$username}

    🔗 <a href="{$link}">Click to see the details</a>
NOTIF_MEETING_STARTED =
    Meeting has started!
    "{$title}"
    - Room: {$room}
    - Academic Tutor: @{$username}

    🔗 <a href="{$link}">Click to see the details</a>
GUIDE_INIT_TEXT =
    Hello student!
    My name is ArThur, I am the bot of Academic Tutorship (AT for short).

    The system helps to keep track of meetings (recaps, consultations) on various university disciplines of your choice.
GUIDE_BTN_NEXT = Next ➡️
GUIDE_DISCIPLINES_TEXT =
    You may choose the disciplines you're interested in.

    Or skip and do that later in ⚙️ <b>Settings</b>.
GUIDE_DISCIPLINES_NONE_SELECTED = 📚 No disciplines selected yet
GUIDE_DISCIPLINES_SELECTED_TITLE = 📚 Selected Disciplines
GUIDE_DISCIPLINES_ITEM = - [{$item[language]} {$item[year]}y] {$item[name]}
GUIDE_BTN_CHOOSE = Choose
GUIDE_BTN_CHOOSE_OTHER = Choose other
GUIDE_BTN_BACK = ⬅️ Back
GUIDE_BTN_SKIP = Skip ➡️
GUIDE_NOTIFICATIONS_TEXT =
    A huge part of my value is sending notifications about upcoming meetings.

    We deliver notifications in a different bot.
    Please, activate it 👇 to continue:
    🔗 <a href="{$link}"><i>Academic Notifications Bot</i></a>

    (you may later block notifications in ⚙️ Settings)
GUIDE_BTN_FINISH = Finish guide 🎉
