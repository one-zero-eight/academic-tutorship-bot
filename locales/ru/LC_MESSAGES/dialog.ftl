COMMON_BTN_BACK = Назад
COMMON_BTN_CANCEL = Отмена
COMMON_BTN_SUBMIT = Подтвердить


AUTH_BIND_INSTRUCTION =
    Чтобы продолжить, пожалуйста, свяжи Telegram с аккаунтом InNoHassle, нажав кнопку "Подключить Telegram 🔗"

    После этого нажми "Проверить подключение ✅"
AUTH_BTN_CONNECT_TELEGRAM = Подключить Telegram 🔗
AUTH_BTN_CHECK_CONNECTED = Проверить подключение ✅


GUIDE_INIT_TEXT =
    Привет, студент!
    Меня зовут АрТур, и я бот Academic Tutorship (в сокращении - AT).

    Эта система упрощает работу со встречами (разборами, консультациями) по различным университетским дисциплинам.
GUIDE_DISCIPLINES_TEXT =
    Ты можешь выбрать дисциплины, в которых ты заинтересован(-а).

    Или можешь пропустить этот шаг и позднее изменить выбор в ⚙️ <b>Настройках</b>.
GUIDE_DISCIPLINES_NONE_SELECTED = 📚 Ты еще не выбрал(-а) ни одну дисциплину
GUIDE_DISCIPLINES_SELECTED_TITLE = 📚 Выбранные дисциплины
GUIDE_NOTIFICATIONS_TEXT =
    Большая часть моей ответственности – это отправка уведомлений о предстоящих встречах.

    Мы отправляем уведомления через другого бота.
    Пожалуйста, активируй его 👇 , чтобы продолжить:
    🔗 <a href="{link}"><i>Academic Notifications Bot</i></a>

    (в дальнейшем ты сможешь заблокировать уведомления в ⚙️ Настройках)
GUIDE_BTN_NEXT = Дальше ➡️
GUIDE_BTN_BACK = ⬅️ Назад
GUIDE_BTN_SKIP = Пропустить ➡️
GUIDE_BTN_FINISH = Завершить знакомство 🎉


ROOT_START_STUDENT =
    Привет-привет, {$first_name}! 👋
    Меня зовут АрТур, и я буду помогать тебе следить за предстоящими встречами Academic Tutorship
ROOT_START_TUTOR_APPENDIX = 🧑‍🏫 <i>Ты доблестный Academic Tutor</i>
ROOT_START_ADMIN_APPENDIX = 👑 <i>Ваше Величество, у Вас есть полный доступ к боту</i>

ROOT_BTN_UPCOMING_MEETINGS = 📚 Предстоящие встречи
ROOT_BTN_TUTORS = 🧑‍🏫 Academic Tutors
ROOT_BTN_SETTINGS = ⚙️ Настройки

ROOT_BTN_YOUR_MEETINGS = 🧑‍🏫 Твои встречи
ROOT_BTN_YOUR_PROFILE = 🧑‍🏫 Твой профиль

ROOT_BTN_MEETINGS_CONTROL = ⚙️ Управление встречами
ROOT_BTN_TUTORS_CONTROL = ⚙️ Academic Tutors

SETTINGS_HEADING =
    ⚙️ Настройки

    📚 Актуальные дисциплины:

SETTINGS_DISCIPLINE_ITEM =  - [{$language} {$year}г] {$name}
SETTINGS_NOTIFICATIONS_LINK = 🔗 <i><a href='{$notification_bot_link}'>ссылка на Notifications Bot</a></i>
SETTINGS_NOTIF_UNACTIVATED = Активируй бота ☝️ для получения уведомлений
SETTINGS_NOTIF_BLOCKED = Разблокируй бота ☝️ для получения уведомлений

SETTINGS_NOTIF_TOGGLE = Уведомления: {$receive_notifications}
SETTINGS_BTN_CHANGE_DISCIPLINES = 📚 Поменять дисциплины

SETTINGS_DISCIPLINES_TITLE = 📚 Выбранные дисциплины
SETTINGS_DISCIPLINES_BTN_CHOOSE = Выбрать
SETTINGS_DISCIPLINES_BTN_CHOOSE_OTHER = Выбрать другие


DISCIPLINE_PICKER_LANGUAGE_TITLE = Выбери программу
DISCIPLINE_PICKER_YEAR_TITLE = Выбери курс
DISCIPLINE_PICKER_DISCIPLINE_TITLE = Выбери дисциплину
DISCIPLINE_PICKER_DISCIPLINES_TITLE = Выбери дисциплины


MEETINGS_TYPE_TITLE = Встречи
MEETINGS_BTN_CREATE_NEW = Создать новую
MEETINGS_BTN_SEE_CREATED = Созданные встречи
MEETINGS_BTN_SEE_APPROVING = Встречи на согласовании
MEETINGS_BTN_SEE_ANNOUNCED = Объявленные встречи
MEETINGS_BTN_SEE_CLOSED = Закрытые встречи

MEETINGS_LIST_CREATED_TITLE = Созданные встречи
MEETINGS_LIST_APPROVING_TITLE = Встречи на согласовании
MEETINGS_LIST_ANNOUNCED_TITLE = Объявленные встречи
MEETINGS_LIST_CLOSED_TITLE = Закрытые встречи

MEETING_CREATE_TITLE =
    Создать новую встречу
    Название: {$title}
    Дисциплина: {$discipline_name}

MEETING_CREATE_BTN_TITLE = Название
MEETING_CREATE_BTN_DISCIPLINE = Дисциплина
MEETING_CREATE_BTN_SUBMIT = Создать ✅

MEETING_CREATE_ENTER_TITLE_TITLE =
    Создать новую встречу
    Дисциплина: {$discipline_name}
    Введите название:

MEETING_INFO_HEADER = ℹ️ Информация о встрече
MEETING_INFO_TITLE_LINE = <b>{$title}</b>
MEETING_INFO_DISCIPLINE_LINE = [{$d_lang} {$d_year}г] {$d_name}
MEETING_INFO_DATE_LINE = 📆 Дата: <b>{$date}</b>
MEETING_INFO_DURATION_LINE = ⏱️ Длительность: <b>{$duration}</b>
MEETING_INFO_ROOM_LINE = 📍 Аудитория: <b>{$room}</b>
MEETING_INFO_TUTOR_LINE = 🧑‍🏫 Academic Tutor: @{$tutor_username}
MEETING_INFO_ADMIN_STATUS_LINE = Статус: <b>{$status_name}</b>
MEETING_INFO_ADMIN_ATTENDANCE_LINE = Посещаемость: <b>{$attendance_count}</b>
MEETING_INFO_DESCRIPTION_HEADER = Описание:
MEETING_INFO_DESCRIPTION_BLOCK = <blockquote>{$description}</blockquote>

MEETING_INFO_BTN_CHANGE_INFO = Изменить информацию
MEETING_INFO_BTN_SEND_FOR_APPROVAL = Отправить на согласование
MEETING_INFO_BTN_ANNOUNCE = Объявить
MEETING_INFO_BTN_FINISH = Завершить
MEETING_INFO_BTN_CLOSE = Закрыть
MEETING_INFO_BTN_ATTENDANCE = Посещаемость
MEETING_INFO_BTN_CANCEL_MEETING = Отменить встречу

MEETING_CONFIRM_SEND_FOR_APPROVAL_TITLE =
    Ты уверен(-а), что хочешь отправить "{$title}" на согласование?
    После согласования, встреча будет <u>объявлена автоматически</u>.
MEETING_CONFIRM_SEND_FOR_APPROVAL_BTN = Отправить на согласование 📩

MEETING_CONFIRM_ANNOUNCE_TITLE = Ты уверен(-а), что хочешь объявить "{$title}"?
MEETING_CONFIRM_ANNOUNCE_BTN = Объявить 📣

MEETING_CONFIRM_FINISH_TITLE = Ты уверен(-а), что хочешь завершить "{$title}"?
MEETING_CONFIRM_FINISH_BTN = Завершить ☑️

MEETING_CONFIRM_DELETE_TITLE =
    Ты уверен(-а), что хочешь отменить "{$title}"?
    Это действие необратимо, и встреча будет удалена.
MEETING_CONFIRM_DELETE_STUDENT_NOTIF_APPENDIX = Уведомление будет отправлено студентам 💌
MEETING_CONFIRM_DELETE_BTN = Отменить встречу 🗑️

STUDENT_MEETINGS_LIST_TITLE = Предстоящие встречи
STUDENT_MEETING_BTN_TUTOR_PROFILE = Профиль Academic Tutor
STUDENT_MEETING_BTN_TO_YOUR_PROFILE = К профилю


CHANGE_INFO_BTN_SET_TITLE = Название
CHANGE_INFO_BTN_SET_DESCRIPTION = Описание
CHANGE_INFO_BTN_SET_ROOM = Аудитория
CHANGE_INFO_BTN_SET_DATE = Дата
CHANGE_INFO_BTN_SET_DURATION = Длительность
CHANGE_INFO_BTN_ASSIGN_TUTOR = Academic Tutor

CHANGE_SET_TITLE_PROMPT = Введи новое название для "{$title}"
CHANGE_SET_DESCRIPTION_PROMPT = Введи новое описание для "{$title}"
CHANGE_SET_ROOM_PROMPT = Введи новую аудиторию для "{$title}"
CHANGE_SET_DATE_PROMPT = Выбери новую дату для "{$title}"
CHANGE_SET_TIME_PROMPT =
    Введи новое время для "{$title}"
    Следуй формату 00:00, например 20:32
CHANGE_SET_DURATION_PROMPT =
    Введи новую длительность для "{$title}"
    В формате "чч:мм", например 01:30
CHANGE_ASSIGN_TUTOR_TITLE =
    Назначение Academic Tutor для "{$title}"
    Вот список Academic Tutors:


ATTENDANCE_BTN_RESEND_FILE = Отправить файл повторно
ATTENDANCE_BTN_ADD_EMAIL = Добавить электронную почту
ATTENDANCE_BTN_DOWNLOAD_FILE = Скачать файл
ATTENDANCE_RESEND_TITLE = Повторно отправь посещаемость для "{title}"
ATTENDANCE_CLOSE_TITLE = Отправь посещаемость для "{title}"
ATTENDANCE_ADD_EMAIL_PROMPT = Введи электронную почту для добавления 👤


TUTOR_LIST_TITLE_FOR_STUDENTS = 🧑‍🏫 Вот are all Academic Tutors!

TUTOR_PROFILE_HEADER_STUDENT_VIEW = 🧑‍🏫 Academic Tutor's Profile
TUTOR_PROFILE_PROFILE_NAME_LINE = <b>{$profile_name}</b>
TUTOR_PROFILE_USERNAME_LINE = @{$username}
TUTOR_PROFILE_DISCIPLINES_HEADER = 📚 Disciplines:
TUTOR_PROFILE_DISCIPLINE_ITEM = - <b>[{$discipline[language]} {$discipline[year]}y] {$discipline[name]}</b>
TUTOR_PROFILE_ABOUT_BLOCK = <blockquote>{$about}</blockquote>
