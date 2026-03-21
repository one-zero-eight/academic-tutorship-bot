# Bot Features and Texts Inventory

## Section 1: Features of bot

### Subsec 1.1: Students Features

- [ ] `/start` opens root screen and renders student greeting with `{first_name}`.
- [ ] Verify root greeting multiline composition:
  - line 1: `Hello there, {first_name} 👋`
  - line 2: `Me, ArThur, will help you to keep track of upcoming AT meetings`
- [ ] Edge case: student who is also tutor sees tutor appendix on start.
- [ ] Edge case: student who is also admin sees admin appendix on start.
- [ ] Open `📚 Upcoming Meetings` from root.
- [ ] Verify meeting list screen title `Upcoming Meetings`.
- [ ] Edge case: no meetings available (empty scrolling list behavior).
- [ ] Edge case: many meetings (scroll/pager behavior in scrolling group).
- [ ] Open specific meeting from list and check meeting info rendering.
- [ ] Meeting info: validate title/discipline/date/duration/room/tutor fields.
- [ ] Meeting info edge case: description absent (no description block shown).
- [ ] Meeting info edge case: description present (blockquote rendered).
- [ ] If available, click `Tutor Profile` from meeting info.
- [ ] Edge case: `Tutor Profile` hidden when tutor profile cannot be shown.
- [ ] If available, click `To Your Profile` from meeting info.
- [ ] Return path works via `Back` from meeting info to meetings list.
- [ ] Open `🧑‍🏫 Tutors` from root.
- [ ] Verify tutors list title `🧑‍🏫 Here are all of your Tutors!`.
- [ ] Edge case: no tutors available.
- [ ] Open tutor profile from list and validate profile details.
- [ ] Tutor profile edge case: `about` is absent (no about block).
- [ ] Tutor profile edge case: `about` exists (blockquote shown).
- [ ] Tutor profile edge case: multiple disciplines displayed with bullets.
- [ ] Return via `Back` to tutors list and then to root.
- [ ] Open `⚙️ Settings` from root.
- [ ] Verify settings title and relevant disciplines list rendering.
- [ ] Verify notification bot hyperlink is rendered and clickable.
- [ ] Notification state edge case: `Activate bot ☝️ to receive notifications` visible for unactivated.
- [ ] Notification state edge case: `Unblock the bot ☝️ to receive notifications` visible for blocked.
- [ ] Toggle `Notifications: {receive_notifications}` and verify state update.
- [ ] Open `📚 Change disciplines` from settings.
- [ ] Verify selected disciplines list screen and list rendering.
- [ ] Click `Choose other` and enter discipline picker in multi-select mode.
- [ ] Discipline picker flow: Choose Program -> Choose Acadmic Year -> Choose Disciplines.
- [ ] Discipline picker edge case: use `Back` to previous step and preserve selected values.
- [ ] Discipline picker edge case: use `Close` in multi mode and return correctly.
- [ ] Submit discipline changes and verify reflected in settings list.
- [ ] Authentication flow (if account not bound):
  - open bind screen
  - click `Connect Telegram 🔗`
  - click `Check Connected ✅`
- [ ] Authentication edge case: repeated `Check Connected ✅` before binding.

### Subsec 1.2: Tutor Features

- [ ] `/start` as tutor shows tutor appendix text.
- [ ] Open `🧑‍🏫 Your Meetings` from root.
- [ ] Verify meetings type hub title `Meetings`.
- [ ] Verify conditional type actions visibility: `See Created`, `See Approving`, `See Announced`, `See Closed`.
- [ ] Open each meeting type list and verify title `{meetings_type} Meetings`.
- [ ] Open `Create New` from meetings type hub.
- [ ] In create screen verify title/discipline placeholders and CTA gating:
  - `Create ✅` appears only when form is valid
  - blank button placeholder appears when cannot create
- [ ] Click `Title` and enter meeting title in input step.
- [ ] Click `Discipline` and pick discipline via discipline picker.
- [ ] Complete creation flow and verify meeting appears in relevant list.
- [ ] Open meeting info and verify action visibility by status:
  - `Change Info`
  - `Send for Approval`
  - `Announce`
  - `Finish`
  - `Close`
  - `Attendance`
  - `Cancel Meeting`
- [ ] Open `Change Info` utility dialog.
- [ ] Verify utility actions in change dialog:
  - `Set Title`
  - `Set Description`
  - `Set Room`
  - `Set Date`
  - `Set Duration`
- [ ] Edge case: date/time edit flow (`Set Date` -> `Enter new Time`) with invalid/valid time format.
- [ ] Edge case: duration format validation (`hh:mm`).
- [ ] Verify `Back` navigation from every change substate to init.
- [ ] Open `Send for Approval` confirmation and confirm/cancel behavior.
- [ ] Open `Announce` confirmation and confirm/cancel behavior.
- [ ] Open `Finish` confirmation and confirm/cancel behavior.
- [ ] Open `Cancel Meeting` confirmation and verify warning text.
- [ ] Edge case: `interesting_to_students` warning about student notification visibility.
- [ ] Open `Attendance` utility dialog from meeting info.
- [ ] Attendance utility checks:
  - `Resend File`
  - `Add email`
  - `Download File`
  - `Back`
- [ ] Attendance edge case: resend with wrong file type.
- [ ] Attendance edge case: add malformed email.
- [ ] Attendance close flow (`Close` state): upload attendance file to close meeting.
- [ ] Open `🧑‍🏫 Your Profile` from root.
- [ ] Verify tutor self-profile header (`🧑‍🏫 Your Tutor's Profile`).
- [ ] Open and update `Profile Name`.
- [ ] Open and update `About`.
- [ ] Open `Disciplines` and adjust selections through discipline picker multi flow.
- [ ] Submit profile disciplines and verify reflected in profile text.
- [ ] Use `Back`/`Cancel` paths from every profile edit step.

### Subsec 1.3: Admin Features

- [ ] `/start` as admin shows admin appendix text.
- [ ] Open `⚙️ Meetings Control` from root.
- [ ] Verify meetings hub/list/create flow works for admin as for tutor.
- [ ] Open any meeting info and verify admin info block exists:
  - `Status: <b>{status.name}</b>`
  - `Attendance: <b>{attendance_count}</b>`
- [ ] In `Change Info` utility dialog verify admin-only action `Assign Tutor` is visible.
- [ ] `Assign Tutor` flow: pick tutor from list and submit assignment input.
- [ ] Verify admin can open tutor profile and own profile control shortcuts when available.
- [ ] Verify admin can execute announcement/approval/finish/cancel actions according to status guards.
- [ ] Open `Attendance` utility dialog as admin and test resend/add-email/download flow.
- [ ] Open `⚙️ Tutors Control` from root.
- [ ] Verify tutors admin list title `Tutors List` and scrolling behavior.
- [ ] Click `Add New` and verify add flow prompt `Share contact of the new Tutor`.
- [ ] Add tutor edge case: invalid contact payload.
- [ ] Open tutor info card and verify identity fields render:
  - `Tutor [{id}] Info`
  - `{full_name}`
  - `@{username}`
  - `telegram id: <code>{telegram_id}</code>`
- [ ] Use `Dismiss` to remove tutor and verify list updates.
- [ ] From tutor info, test `Profile` and `Edit Profile` entry points (depending on ownership flags).

---

## Section 2: Texts of bot

Notes:
- English column contains current code text/template.
- Russian column is intentionally left blank for future translation.
- Composite widgets (`MeetingInfoText`, `TutorProfileText`) are represented with fully combined templates.

### Subsec 2.1: Student Texts

| Text Identifier | English | Russian |
|---|---|---|
| ROOT_START_STUDENT | Hello there, {first_name} 👋<br>Me, ArThur, will help you to keep track of upcoming AT meetings |  |
| ROOT_START_TUTOR_APPENDIX | 🧑‍🏫 <i>Honorable tutor you are</i> |  |
| ROOT_START_ADMIN_APPENDIX | 👑 <i>And admin panel is also available for you</i> |  |
| ROOT_BTN_UPCOMING_MEETINGS | 📚 Upcoming Meetings |  |
| ROOT_BTN_TUTORS | 🧑‍🏫 Tutors |  |
| ROOT_BTN_SETTINGS | ⚙️ Settings |  |
| STUDENT_MEETINGS_LIST_TITLE | Upcoming Meetings |  |
| COMMON_BTN_BACK | Back |  |
| STUDENT_MEETING_BTN_TUTOR_PROFILE | Tutor Profile |  |
| STUDENT_MEETING_BTN_TO_YOUR_PROFILE | To Your Profile |  |
| TUTOR_LIST_TITLE_FOR_STUDENTS | 🧑‍🏫 Here are all of your Tutors! |  |
| TUTOR_PROFILE_HEADER_STUDENT_VIEW | 🧑‍🏫 Tutor's Profile |  |
| TUTOR_PROFILE_PROFILE_NAME_LINE | <b>{profile_name}</b> |  |
| TUTOR_PROFILE_USERNAME_LINE | @{username} |  |
| TUTOR_PROFILE_DISCIPLINES_HEADER | 📚 Disciplines: |  |
| TUTOR_PROFILE_DISCIPLINE_ITEM | - <b>[{discipline[language]} {discipline[year]}y] {discipline[name]}</b> |  |
| TUTOR_PROFILE_ABOUT_BLOCK | <blockquote>{about}</blockquote> |  |
| SETTINGS_TITLE | ⚙️ Settings️ |  |
| SETTINGS_RELEVANT_DISCIPLINES_TITLE | 📚 Relevant disciplines: |  |
| SETTINGS_DISCIPLINE_ITEM | - [{item[language]} {item[year]}y] {item[name]} |  |
| SETTINGS_NOTIFICATIONS_LINK | 🔗 <i><a href='{notification_bot_link}'>link to Notifications Bot</a></i> |  |
| SETTINGS_NOTIF_UNACTIVATED | Activate bot ☝️ to receive notifications |  |
| SETTINGS_NOTIF_BLOCKED | Unblock the bot ☝️ to receive notifications |  |
| SETTINGS_NOTIF_TOGGLE | Notifications: {receive_notifications} |  |
| SETTINGS_BTN_CHANGE_DISCIPLINES | 📚 Change disciplines |  |
| SETTINGS_DISCIPLINES_TITLE | 📚 Selected Disciplines |  |
| SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER | Choose other |  |
| SETTINGS_DISCIPLINES_BTN_SUBMIT | Submit |  |
| DISCIPLINE_PICKER_LANGUAGE_TITLE | Choose Program |  |
| DISCIPLINE_PICKER_YEAR_TITLE | Choose Acadmic Year |  |
| DISCIPLINE_PICKER_DISCIPLINE_TITLE | Choose Discipline |  |
| DISCIPLINE_PICKER_DISCIPLINES_TITLE | Choose Disciplines |  |
| DISCIPLINE_PICKER_BTN_CANCEL | Cancel |  |
| DISCIPLINE_PICKER_BTN_CLOSE | Close |  |
| AUTH_BIND_INSTRUCTION | To proceed, please connect your telegram with your InNoHassle account by pressing the button "Connect Telegram 🔗"<br><br>After that press "Check Connected ✅" |  |
| AUTH_BTN_CONNECT_TELEGRAM | Connect Telegram 🔗 |  |
| AUTH_BTN_CHECK_CONNECTED | Check Connected ✅ |  |
| MEETING_INFO_TEMPLATE_STUDENT | ℹ️ Meeting Information<br><br><b>{title}</b><br>[{d_lang} {d_year}y] {d_name}<br><br>📆 Date: <b>{date}</b><br>⏱️ Duration: <b>{duration}</b><br>📍 Room: <b>{room}</b><br>🧑‍🏫 Tutor: @{tutor_username}<br><br>Description:<br><blockquote>{description}</blockquote> |  |

### Subsec 2.2: Tutor Texts

| Text Identifier | English | Russian |
|---|---|---|
| ROOT_TUTOR_APPENDIX | 🧑‍🏫 <i>Honorable tutor you are</i> |  |
| ROOT_BTN_YOUR_MEETINGS | 🧑‍🏫 Your Meetings |  |
| ROOT_BTN_YOUR_PROFILE | 🧑‍🏫 Your Profile |  |
| MEETINGS_TYPE_TITLE | Meetings |  |
| MEETINGS_BTN_CREATE_NEW | Create New |  |
| MEETINGS_BTN_SEE_CREATED | See Created |  |
| MEETINGS_BTN_SEE_APPROVING | See Approving |  |
| MEETINGS_BTN_SEE_ANNOUNCED | See Announced |  |
| MEETINGS_BTN_SEE_CLOSED | See Closed |  |
| MEETINGS_LIST_TITLE | {meetings_type} Meetings |  |
| MEETING_CREATE_TITLE | New Meeting |  |
| MEETING_CREATE_FIELD_TITLE | Title: {title} |  |
| MEETING_CREATE_FIELD_DISCIPLINE | Discipline: {discipline_name} |  |
| MEETING_CREATE_BTN_TITLE | Title |  |
| MEETING_CREATE_BTN_DISCIPLINE | Discipline |  |
| MEETING_CREATE_BTN_SUBMIT | Create ✅ |  |
| MEETING_CREATE_ENTER_TITLE_TITLE | Create New Meeting |  |
| MEETING_CREATE_ENTER_TITLE_PROMPT | Enter Title: |  |
| MEETING_INFO_BTN_CHANGE_INFO | Change Info |  |
| MEETING_INFO_BTN_SEND_FOR_APPROVAL | Send for Approval |  |
| MEETING_INFO_BTN_ANNOUNCE | Announce |  |
| MEETING_INFO_BTN_FINISH | Finish |  |
| MEETING_INFO_BTN_CLOSE | Close |  |
| MEETING_INFO_BTN_ATTENDANCE | Attendance |  |
| MEETING_INFO_BTN_CANCEL_MEETING | Cancel Meeting |  |
| MEETING_CONFIRM_SEND_FOR_APPROVAL_TITLE | Are you surely ready to send "{title}" for approval? |  |
| MEETING_CONFIRM_SEND_FOR_APPROVAL_APPENDIX | After approval, the meeting will be <u>announced automatically</u>. |  |
| MEETING_CONFIRM_SEND_FOR_APPROVAL_BTN | Send for Approval 📩 |  |
| MEETING_CONFIRM_ANNOUNCE_TITLE | Are you surely ready to announce "{title}"? |  |
| MEETING_CONFIRM_ANNOUNCE_BTN | Announce 📣 |  |
| MEETING_CONFIRM_FINISH_TITLE | Are you surely ready to finish "{title}"? |  |
| MEETING_CONFIRM_FINISH_BTN | Finish ☑️ |  |
| MEETING_CONFIRM_DELETE_TITLE | Do you really want to cancel "{title}"? |  |
| MEETING_CONFIRM_DELETE_APPENDIX | This action cannot be undone and the meeting will be deleted. |  |
| MEETING_CONFIRM_DELETE_STUDENT_NOTIFY | The notification will be sent to students 💌. |  |
| MEETING_CONFIRM_DELETE_BTN | Cancel Meeting 🗑️ |  |
| CHANGE_INFO_BTN_SET_TITLE | Set Title |  |
| CHANGE_INFO_BTN_SET_DESCRIPTION | Set Description |  |
| CHANGE_INFO_BTN_SET_ROOM | Set Room |  |
| CHANGE_INFO_BTN_SET_DATE | Set Date |  |
| CHANGE_INFO_BTN_SET_DURATION | Set Duration |  |
| CHANGE_SET_TITLE_PROMPT | Enter new Title for "{title}" |  |
| CHANGE_SET_DESCRIPTION_PROMPT | Enter new Description for "{title}" |  |
| CHANGE_SET_ROOM_PROMPT | Enter new Room for "{title}" |  |
| CHANGE_SET_DATE_PROMPT | Enter new Date for "{title}" |  |
| CHANGE_SET_TIME_PROMPT | Enter new Time for "{title}" |  |
| CHANGE_SET_TIME_FORMAT_HINT | Adhere to format 00:00, e.g. 20:32 |  |
| CHANGE_SET_DURATION_PROMPT | Enter new Duration for "{title}" |  |
| CHANGE_SET_DURATION_FORMAT_HINT | In format "hh:mm" |  |
| ATTENDANCE_BTN_RESEND_FILE | Resend File |  |
| ATTENDANCE_BTN_ADD_EMAIL | Add email |  |
| ATTENDANCE_BTN_DOWNLOAD_FILE | Download File |  |
| ATTENDANCE_RESEND_TITLE | Resend attendance file for "{title}" |  |
| ATTENDANCE_CLOSE_TITLE | Send attendance file to close "{title}" |  |
| ATTENDANCE_ADD_EMAIL_PROMPT | Enter email of a person to add 👤 |  |
| TUTOR_PROFILE_HEADER_TUTOR_VIEW | 🧑‍🏫 Your Tutor's Profile |  |
| TUTOR_PROFILE_CONTROL_BTN_NAME | Profile Name |  |
| TUTOR_PROFILE_CONTROL_BTN_ABOUT | About |  |
| TUTOR_PROFILE_CONTROL_BTN_DISCIPLINES | Disciplines |  |
| TUTOR_PROFILE_SET_NAME_PROMPT | Enter Profile Name |  |
| TUTOR_PROFILE_SET_NAME_HINT | This name will be awailable to students |  |
| TUTOR_PROFILE_SET_ABOUT_PROMPT | Write something about you |  |
| TUTOR_PROFILE_SET_ABOUT_HINT | This will be awailable to students |  |
| TUTOR_PROFILE_SELECT_DISCIPLINES_TITLE | Selected Disciplines |  |
| TUTOR_PROFILE_BTN_CHOOSE_OTHER | Choose other |  |
| TUTOR_PROFILE_BTN_SUBMIT | Submit |  |
| NOTIF_TUTOR_PROMOTED_FOR_TUTOR | You've been promoted to being a tutor!<br><br>- Restart the bot (<a href="https://t.me/academic_notifications_bot?start=promoted_tutor">click here</a>)<br>- Fill up your tutor profile |  |
| NOTIF_TUTOR_DISMISSED_FOR_TUTOR | You've been dismissed from being a tutor<br><br>Your tutor profile won't be shown to students anymore |  |
| NOTIF_TUTOR_ASSIGNED_FOR_TUTOR | You have been assigned to meeting "{title}"!<br>- Date & time: {datetime}<br>- Room: {room}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_TUTOR_CHANGED_FOR_NEW_TUTOR | You have been assigned as the new tutor for meeting "{title}".<br>- Date & time: {datetime}<br>- Room: {room}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_TUTOR_CHANGED_FOR_OLD_TUTOR | You are no longer the tutor for meeting "{title}". |  |
| NOTIF_MEETING_FINISHED | Meeting has finished!<br>"{title}"<br><br>‼️ Remember to upload the attendance file<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_CLOSED_FOR_TUTOR | Meeting has been closed by the admin.<br>"{title}"<br>👥 Attendance count: {attendance_count}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |

### Subsec 2.3: Admin Texts

| Text Identifier | English | Russian |
|---|---|---|
| ROOT_ADMIN_APPENDIX | 👑 <i>And admin panel is also available for you</i> |  |
| ROOT_BTN_MEETINGS_CONTROL | ⚙️ Meetings Control |  |
| ROOT_BTN_TUTORS_CONTROL | ⚙️ Tutors Control |  |
| CHANGE_INFO_BTN_ASSIGN_TUTOR | Assign Tutor |  |
| CHANGE_ASSIGN_TUTOR_TITLE | Assign Tutor to "{title}" |  |
| CHANGE_ASSIGN_TUTOR_HINT | Here's the list of all tutors for reference |  |
| TUTORS_ADMIN_LIST_TITLE | Tutors List |  |
| TUTORS_ADMIN_BTN_ADD_NEW | Add New |  |
| TUTORS_ADMIN_INFO_TITLE | Tutor [{id}] Info |  |
| TUTORS_ADMIN_INFO_FULL_NAME | {full_name} |  |
| TUTORS_ADMIN_INFO_USERNAME | @{username} |  |
| TUTORS_ADMIN_INFO_TELEGRAM_ID | telegram id: <code>{telegram_id}</code> |  |
| TUTORS_ADMIN_BTN_DISMISS | Dismiss |  |
| TUTORS_ADMIN_BTN_PROFILE | Profile |  |
| TUTORS_ADMIN_BTN_EDIT_PROFILE | Edit Profile |  |
| TUTORS_ADMIN_ADD_PROMPT | Share contact of the new Tutor |  |
| MEETING_INFO_ADMIN_STATUS | Status: <b>{status.name}</b> |  |
| MEETING_INFO_ADMIN_ATTENDANCE | Attendance: <b>{attendance_count}</b> |  |
| NOTIF_BOT_STARTED | <a href="{link}">Academic Tutorship Bot</a> has been started 🚀 |  |
| NOTIF_BOT_SHUTDOWN | <a href="{link}">Academic Tutorship Bot</a> has been shut down 💤 |  |
| NOTIF_MEETING_UPDATED_TITLE | Changed title for meeting "{old_title}"<br>- New title: "{title}"<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_UPDATED_ROOM | Changed room for meeting "{title}"<br>- New room: {room}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_UPDATED_DATETIME | Changed date for meeting "{title}"<br>- New date & time: {datetime}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_UPDATED_TUTOR | Changed tutor for meeting "{title}"<br>- New tutor: @{username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_TUTOR_PROMOTED_FOR_ADMINS | The student {full_name} @{username} was promoted to being a tutor |  |
| NOTIF_TUTOR_DISMISSED_FOR_ADMINS | The student {full_name} @{username} is dismissed from being a tutor |  |
| NOTIF_TUTOR_ASSIGNED_FOR_ADMINS | Tutor @{username} assigned to meeting "{title}"<br>- Date & time: {datetime}<br>- Room: {room}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_TUTOR_CHANGED_FOR_ADMINS | Tutor changed for meeting "{title}"<br>- Old tutor: @{old_username}<br>- New tutor: @{new_username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_CLOSED_FOR_ADMINS | Meeting has been closed by the tutor.<br>"{title}"<br><br>👥 Attendance count: {attendance_count} |  |
| NOTIF_MEETING_APPROVE_REQUEST | Meeting "{title}" is awaiting approval.<br>- Date & time: {datetime}<br>- Room: {room}<br>- Tutor: @{username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_CONFIRM_APPROVE_APPENDIX | The meeting will be <u>automatically announced to students</u>. Are you sure? |  |
| NOTIF_MEETING_APPROVED | Meeting "{title}" has been approved!<br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_DISCARDED | Meeting "{title}" has been discarded<br><br>Reason:<br><blockquote>{reason}</blockquote><br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_CANCELLED_FOR_USERS | Meeting "{title}" has been cancelled 😞<br><br>Sorry for the inconvenience. We hope to see you in other meetings! |  |
| NOTIF_MEETING_REMINDER | Reminder: Meeting "{title}" is upcoming!<br>- Date & time: {datetime}<br>- Room: {room}<br>- Tutor: @{username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_ANNOUNCED | New meeting upcoming!<br>"{title}"<br>- Date & time: {datetime}<br>- Room: {room}<br>- Tutor: @{username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
| NOTIF_MEETING_STARTED | Meeting has started!<br>"{title}"<br>- Room: {room}<br>- Tutor: @{username}<br><br>🔗 <a href="{link}">Click to see the details</a> |  |
