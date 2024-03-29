import os
import logging
from aiogram import *
# from aiogram import Bot
from CONSTANTS import *
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import *
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from readusers import *
from post import *
import re

API_TOKEN = ""
CHAT_ID = ""

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

dp.middleware.setup(LoggingMiddleware())


def is_valid_phone_number(phone_number):
    pattern = r'^\+\d{11}$'

    if re.match(pattern, phone_number):
        return True
    else:
        return False


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # await message.delete()
    first_name = message.from_user.first_name
    username = message.from_user.username
    user_id = message.from_user.id
    await message.answer(text=START_MESSAGE(first_name))


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.delete()
    await message.answer(text=HELP_COMMAND)




#
# # ПРОВЕРКА ПОДПИСКИ begin
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
# # ПРОВЕРКА ПОДПИСКИ end
#






#
# # РЕГИСТРАЦИЯ begin
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
                f"Sex:{user_info['sex']}\n")
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
            f"Sex:{user_info['sex']}\n")

    with open(file_name, "w") as file:
        file.writelines(updated_lines)


@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    user_id = message.from_user.id
    if str(user_id) not in user_data:
        user_data[user_id] = {}
        await bot.send_message(message.from_user.id, text=REGISTRATION_MESSAGE_2)
    else:
        await bot.send_message(message.from_user.id, text='Вы уже зарегистрированы')


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

    if is_valid_phone_number(phone):
        user_data[user_id]["phone"] = phone
        await message.answer(text=REGISTRATION_MESSAGE_5)
    else:
        await bot.send_message(message.from_user.id, text="Неправильный формат ввода. Попробуйте еще раз")


@dp.message_handler(lambda message: message.from_user.id in user_data and "sex" not in user_data[message.from_user.id])
async def process_sex(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id
    sex = message.text.strip()
    user_data[user_id]["sex"] = sex
    update_user_file(user_id, user_data[user_id], username)

    confirm_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text=("Все верно "), callback_data="confirm_yes"),
        InlineKeyboardButton(text=("Начать заново"),
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
    # await bot.send_message(message.from_user.id, str(message.from_user.id))
    if message.from_user.id not in user_data and str(message.from_user.id) not in user_data:
        await bot.send_message(message.from_user.id, "Для начала работы с ботом вам необходимо прописать /register")
    elif (message.from_user.id not in ADMINS) and admins_on:
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        CUR_STATE[message.from_user.id] = 'posting_text'
        await bot.send_message(message.from_user.id, "Отправьте текст")


# @dp.message_handler(
#     lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'posting_text')
# async def readmsg(msg: types.Message):
#     message = msg.text
#     print(len(user_data))
#     for user_id in user_data:
#         print(user_id)
#         await bot.send_message(user_id, message)
#     await bot.send_message(msg.from_user.id, "пост отправлен")
#     CUR_STATE.pop(msg.from_user.id)

async def delete_and_edit_previous_message(message, new_text):
    user_id = str(message.from_user.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # print(user_data)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=user_data[user_id]["message_id"], text=new_text)


# @dp.message_handler(lambda message: message.from_user.id not in CUR_STATE, commands=['post'])
# async def post(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         # await delete_and_edit_previous_message(message, "У вас нет прав")
#         await bot.send_message(message.from_user.id, "У вас нет прав")
#     else:
#         CUR_STATE[message.from_user.id] = 'posting_text'
#         await bot.send_message(message.from_user.id, "Отправьте текст")
#         # await delete_and_edit_previous_message(message, "Отправьте текст")


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'posting_text')
async def readmsg(msg: types.Message):
    CUR_MESSAGE.append(msg.text)
    CUR_STATE[msg.from_user.id] = 'posting_photo'
    # await delete_and_edit_previous_message(msg, "А теперь пришлите фото")
    await bot.send_message(msg.from_user.id, 'А теперь пришлите фото')


@dp.message_handler(lambda message: CUR_STATE[message.from_user.id] == 'posting_photo',
                    content_types=types.ContentType.PHOTO)
async def loadTxt(msg: types.Message):
    photo = msg.photo[-1].file_id
    for user_id in user_data:
        await bot.send_photo(user_id, photo=photo)
        await bot.send_message(user_id, CUR_MESSAGE[0])
    await bot.send_message(msg.from_user.id, "Пост отправлен!")
    CUR_STATE.pop(msg.from_user.id)
    CUR_MESSAGE.clear()


#
#
# for annonce
#
#

@dp.message_handler(lambda message: message.from_user.id not in CUR_STATE, commands=['announce'])
async def post(message: types.Message):
    # await message.delete()
    if ((message.from_user.id not in ADMINS) and admins_on) or str(message.from_user.id) not in user_data:
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        CUR_STATE[message.from_user.id] = 'posting_text_anonce'
        await bot.send_message(message.from_user.id, "Отправьте текст")


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'posting_text_anonce')
async def readmsg(msg: types.Message):
    #await msg.delete()
    CUR_STATE[msg.from_user.id] = 'waiting_for_rates'
    annonce[msg.from_user.id] = {'text': msg.text}
    await bot.send_message(msg.from_user.id, 'Введите количество тарифов')


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'waiting_for_rates')
async def readmsg(msg: types.Message):
    annonce[msg.from_user.id]['numberOfRates'] = int(msg.text)
    if annonce[msg.from_user.id]['numberOfRates'] > 4:
        await bot.send_message(msg.from_user.id, 'Максимальное количество тарифов равно 4\n Введите корректное число')
    else:
        annonce[msg.from_user.id]['rates'] = {}
        CUR_STATE[msg.from_user.id] = 'waiting_for_rates2'
        await bot.send_message(msg.from_user.id, 'Введите все тарифы через запятую')


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'waiting_for_rates2')
async def readmsg(msg: types.Message):
    listOfRates = msg.text.split(',')
    if len(listOfRates) != annonce[msg.from_user.id]['numberOfRates']:
        await bot.send_message(msg.from_user.id, "Введите правильное количество тарифов")
    else:
        annonce[msg.from_user.id]['allRates'] = listOfRates
        annonce[msg.from_user.id]['curInd'] = 0
        for rate in listOfRates:
            annonce[msg.from_user.id]['rates'][rate] = []
        await bot.send_message(msg.from_user.id, 'Введите описание 1 тарифа')
        CUR_STATE[msg.from_user.id] = 'waiting_for_rates3'


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'waiting_for_rates3' and
                    annonce[message.from_user.id]['curInd'] != (len(annonce[message.from_user.id]) - 1))
async def readmsg(msg: types.Message):
    text = msg.text
    curRate = annonce[msg.from_user.id]['allRates'][annonce[msg.from_user.id]['curInd']]
    annonce[msg.from_user.id]['rates'][curRate].append(text)
    await bot.send_message(msg.from_user.id, 'Введите цену тарифа {}'.format(curRate))
    CUR_STATE[msg.from_user.id] = 'waiting_for_price'


@dp.message_handler(lambda msg: msg.from_user.id in CUR_STATE and CUR_STATE[msg.from_user.id] == 'waiting_for_price')
async def readmsg(msg: types.Message):
    text = msg.text
    curRate = annonce[msg.from_user.id]['allRates'][annonce[msg.from_user.id]['curInd']]
    annonce[msg.from_user.id]['rates'][curRate].append(text)
    if curRate != annonce[msg.from_user.id]['allRates'][-1]:
        annonce[msg.from_user.id]['curInd'] += 1
        curRate = annonce[msg.from_user.id]['allRates'][annonce[msg.from_user.id]['curInd']]
        await bot.send_message(msg.from_user.id, 'Введите описание тарифа {}'.format(curRate))
        CUR_STATE[msg.from_user.id] = 'waiting_for_rates3'
    else:
        CUR_STATE[msg.from_user.id] = 'finishing'

        await bot.send_message(msg.from_user.id, "Пришлите фото для аннонса")


@dp.message_handler(lambda msg: msg.from_user.id in CUR_STATE and CUR_STATE[msg.from_user.id] == 'finishing',
                    content_types=types.ContentType.PHOTO)
async def readmsg(msg: types.Message):
    photo = msg.photo[-1].file_id
    annonce[msg.from_user.id]['photo'] = photo
    nRates = annonce[msg.from_user.id]['numberOfRates']

    for user_id in user_data:
        if nRates == 1:
            await bot.send_photo(user_id, photo, caption=annonce[msg.from_user.id]['text'],
                                 reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                          callback_data='first'))
                                 )
            # await bot.send_message(msg.from_user.id, annonce[msg.from_user.id]['text'],
            #                        reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
            #                            InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
            #                                                 callback_data='first'))
            #                        )
        elif nRates == 2:
            await bot.send_photo(user_id, photo, caption=annonce[msg.from_user.id]['text'],
                                 reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                          callback_data='first'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                          callback_data='second'))
                                 )
        elif nRates == 3:
            await bot.send_photo(user_id, photo, caption=annonce[msg.from_user.id]['text'],
                                 reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                          callback_data='first'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                          callback_data='second'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][2]),
                                                          callback_data='third'))
                                 )
        elif nRates == 4:
            await bot.send_photo(user_id, photo, caption=annonce[msg.from_user.id]['text'],
                                 reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                          callback_data='first'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                          callback_data='second'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][2]),
                                                          callback_data='third'),
                                     InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][3]),
                                                          callback_data='fourth'))
                                 )
    await bot.send_message(msg.from_user.id, f"Анонс был отправлен {len(user_data)}" +  ("людям!" if len(user_data) > 1 else 'человеку!'))


@dp.callback_query_handler(lambda call: call.data == 'Rates')
async def readmsg(msg: types.Message):
    nRates = annonce[msg.from_user.id]['numberOfRates']

    if nRates == 1:
        await bot.send_photo(msg.from_user.id, annonce[msg.from_user.id]['photo'],
                             caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'))
                             )
    elif nRates == 2:
        await bot.send_photo(msg.from_user.id, annonce[msg.from_user.id]['photo'],
                             caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                      callback_data='second'))
                             )
    elif nRates == 3:
        await bot.send_photo(msg.from_user.id, annonce[msg.from_user.id]['photo'],
                             caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                      callback_data='second'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][2]),
                                                      callback_data='third'))
                             )
    elif nRates == 4:
        await bot.send_photo(msg.from_user.id, annonce[msg.from_user.id]['photo'],
                             caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                      callback_data='second'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][2]),
                                                      callback_data='third'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][3]),
                                                      callback_data='fourth'))
                             )


@dp.callback_query_handler(lambda call: call.data == 'first')
async def readmsg(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id,
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][0]][
                               0] + '\n\nЦена: ' +
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][0]][1],
                           reply_markup=InlineKeyboardMarkup(row_width=2).add(
                               InlineKeyboardButton(text="Подтвердить",
                                                    callback_data='Purchase'),
                               InlineKeyboardButton(text="Назад",
                                                    callback_data='Rates'))
                           )


@dp.callback_query_handler(lambda call: call.data == 'second')
async def readmsg(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id,
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][1]][0])
    await bot.send_message(call.from_user.id,
                           'Цена: ' +
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][1]][1],
                           reply_markup=InlineKeyboardMarkup(row_width=2).add(
                               InlineKeyboardButton(text="Подтвердить",
                                                    callback_data='Purchase'),
                               InlineKeyboardButton(text="Назад",
                                                    callback_data='Rates'))
                           )


@dp.callback_query_handler(lambda call: call.data == 'third')
async def readmsg(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id,
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][2]][0])
    await bot.send_message(call.from_user.id,
                           'Цена: ' + annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][2]][1])


@dp.callback_query_handler(lambda call: call.data == 'fourth')
async def readmsg(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id,
                           annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][3]][0])
    await bot.send_message(call.from_user.id,
                           'Цена: ' + annonce[call.from_user.id]['rates'][annonce[call.from_user.id]['allRates'][3]][1])


@dp.callback_query_handler(lambda call: call.data == 'Purchase')
async def readmsg(call: types.CallbackQuery):
    if call.from_user.id not in visitors:
        await bot.send_message(call.from_user.id, "Тариф выбран!\nЖдем вас на мероприятии")
        visitors.add(call.from_user.id)
        CUR_STATE.pop(call.from_user.id)
    else:
        await bot.send_message(call.from_user.id, "Вы уже выбрали тариф")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)


# # Start the polling
# import asyncio
#
# loop = asyncio.get_event_loop()
# task = loop.create_task(dp.start_polling())
