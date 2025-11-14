from aiogram.types import KeyboardButton, KeyboardButtonRequestUsers, ReplyKeyboardMarkup

request_users = KeyboardButtonRequestUsers(
    request_id=0,
    user_is_bot=False,
    request_username=True,
    max_quantity=1,
)

CHOOSE_USER_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Choose User 👤", request_users=request_users)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

del request_users
