import os
import logging
from aiogram import *
from readusers import readdata
from CONSTANTS import *
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import *
from aiogram.contrib.middlewares.logging import LoggingMiddleware


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

dp.middleware.setup(LoggingMiddleware())

user_data = readdata()
#user_data = {}
file_name = "USERS.txt"
ADMINS = [832935844]
# registered_users = []
CUR_STATE = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.delete()
    first_name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    await message.answer(text=START_MESSAGE(first_name))


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.delete()
    await message.answer(text=HELP_COMMAND)


#
#
# #
# # # ПРОВЕРКА ПОДПИСКИ begin
# #
#
#

def check_channel_subscription(chat_member):
    if chat_member['status'] != 'left':
        return True
    else:
        return False


def banned(chat_member):
    if chat_member['status'] == 'kicked':
        return True
    else:
        return False


class ChannelMembershipMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        first_name = message.from_user.first_name
        username = message.from_user.username
        user_id = message.from_user.id
        if message.text and message.text.startswith('/start'):
            return True

        chat_member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)

        if check_channel_subscription(chat_member):
            if banned(chat_member):
                await message.answer(text=BANNED_TEXT)
                bot.stop_polling()
                return False
            else:
                return True
        else:
            keyboard = InlineKeyboardMarkup(row_width=2).add(

                InlineKeyboardButton(text="Группа", url=CHANNEL_LINK),
                InlineKeyboardButton(text= ('готово'),
                                     callback_data="verify_subscription")
            )
            await message.answer(text=NOT_SUBSCRIBED_MESSAGE, reply_markup=keyboard)
            bot.stop_polling()
            return False


dp.middleware.setup(ChannelMembershipMiddleware())


@dp.callback_query_handler(lambda c: c.data == "verify_subscription")
async def verify_subscription(callback_query: types.CallbackQuery):
    chat_member = await bot.get_chat_member(CHANNEL_ID, callback_query.from_user.id)
    if check_channel_subscription(chat_member):
        await bot.send_message(callback_query.message.chat.id,
                               text=("Я вижу что ты в теме"))
    else:
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Verify Subscription", callback_data="verify_subscription"))
        await callback_query.answer(text=NOT_SUBSCRIBED_MESSAGE2, show_alert=True)


#
#
# #
# # # ПРОВЕРКА ПОДПИСКИ end
# #
#
#


#
#
# #
# # # РЕГИСТРАЦИЯ begin
# #
#
#

def update_user_file(user_id, user_info, username):
    if not os.path.exists(file_name):
        with open(file_name, "w") as file:
            pass

    with open(file_name, "r") as file:
        lines = file.readlines()

    updated_lines = []
    found = False
    skip_line = False
    for line in lines:
        if line.startswith(f"User ID: {user_id}"):
            found = True

            updated_lines.append(
                f"User ID:{user_id}\n"
                f"Username:@{username}\n"
                f"Name:{user_info['name']}\n"
                f"Date of Birth:{user_info['dob']}\n"
                f"Phone:{user_info['phone']}\n"
                f"Sex:{user_info['sex']}\n\n")
            skip_line = True
        elif skip_line and line.strip():
            continue
        else:
            skip_line = False
            updated_lines.append(line)

    if not found:
        updated_lines.append(
            f"User ID:{user_id}\n"
            f"Username:@{username}\n"
            f"Name:{user_info['name']}\n"
            f"Date of Birth:{user_info['dob']}\n"
            f"Phone:{user_info['phone']}\n"
            f"Sex:{user_info['sex']}\n\n\n")

    with open(file_name, "w") as file:
        file.writelines(updated_lines)


@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await bot.send_message(message.from_user.id, text=REGISTRATION_MESSAGE_2)


@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def process_name(message: types.Message):
    user_id = message.from_user.id
    user_name = message.text.strip()
    user_data[user_id]["name"] = user_name
    await message.answer(text=REGISTRATION_MESSAGE_3)


@dp.message_handler(lambda message: message.from_user.id in user_data and "dob" not in user_data[message.from_user.id])
async def process_dob(message: types.Message):
    user_id = message.from_user.id
    dob = message.text.strip()
    user_data[user_id]["dob"] = dob
    await message.answer(text=REGISTRATION_MESSAGE_4)


@dp.message_handler(
    lambda message: message.from_user.id in user_data and "phone" not in user_data[message.from_user.id])
async def process_dob(message: types.Message):
    user_id = message.from_user.id
    phone = message.text.strip()
    user_data[user_id]["phone"] = phone
    await message.answer(text=REGISTRATION_MESSAGE_5)


@dp.message_handler(lambda message: message.from_user.id in user_data and "sex" not in user_data[message.from_user.id])
async def process_sex(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id
    sex = message.text.strip()
    user_data[user_id]["sex"] = sex
    print(len(user_data))
    update_user_file(user_id, user_data[user_id], username)

    confirm_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text = ("Все верно "), callback_data="confirm_yes"),
        InlineKeyboardButton(text= ("Начать заново"),
                             callback_data="confirm_no")
    )

    await message.answer(
        f"Проверь информацию о себе:\n"
        f"ФИО: {user_data[user_id]['name']}\n"
        f"Дата рождения: {user_data[user_id]['dob']}\n"
        f"Номер телефона: {user_data[user_id]['phone']}\n"
        f"Пол: {sex}",
        reply_markup=confirm_keyboard
    )


@dp.callback_query_handler(lambda c: c.data == "confirm_yes")
async def confirm_yes(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    #del user_data[user_id]
    await bot.send_message(callback_query.message.chat.id, text=CONFIRM_REGISTRATION_MSG)


@dp.callback_query_handler(lambda c: c.data == "confirm_no")
async def confirm_no(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id] = {}
    await bot.send_message(callback_query.message.chat.id, text=REGISTRATION_MESSAGE_2)


#
#
# #
# # # РЕГИСТРАЦИЯ end
# #
#
#

@dp.message_handler(lambda message: message.from_user.id not in CUR_STATE, commands=['post'])
async def post(message: types.Message):
    if message.from_user.id not in ADMINS:
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        CUR_STATE[message.from_user.id] = 'posting_text'
        await bot.send_message(message.from_user.id, "Отправьте текст")


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'posting_text')
async def readmsg(msg: types.Message):
    message = msg.text
    print(len(user_data))
    for user_id in user_data:
        print(user_id)
        await bot.send_message(user_id, message)
    await bot.send_message(msg.from_user.id, "пост отправлен")
    CUR_STATE.pop(msg.from_user.id)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
