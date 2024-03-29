from main import *


#
#
##
# #
# ##
# # #
# # ##
# # # #
# # # ##
# # # # # |----------| РЕГИСТРАЦИЯ begin
# # # ##
# # # #
# # ##
# # #
# ##
# #
##
#


@dp.message_handler(commands=['register'])
async def register(message: types.Message):
    await message.delete()
    user_id = message.from_user.id
    if is_user_registered(user_id):
        await bot.send_message(
            user_id,
            text="Вы уже зарегистрированы",
            reply_markup=InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text=emoji.emojize("Заново :counterclockwise_arrows_button:"),
                                     callback_data="reopen_registration_form"),
                InlineKeyboardButton(text=emoji.emojize("Информация:information:"), callback_data="user_info")
            )
        )
    else:
        user_data[user_id] = {}
        msg = await bot.send_message(message.from_user.id, text=REGISTRATION_MESSAGE_2)
        user_data[user_id]["message_id"] = msg.message_id


def is_user_registered(user_id):
    return user_id in users


@dp.callback_query_handler(lambda call: call.data == 'user_info')
async def show_user_info(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_info = users[user_id]
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Информация о вас:\n"
             f"ФИО: {user_info['name']}\n"
             f"Дата рождения: {user_info['dob']}\n"
             f"Номер телефона: {user_info['phone']}\n"
             f"Пол: {user_info['sex']}")
    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(lambda c: c.data == "reopen_registration_form")
async def reopen_registration_form(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id] = {}
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    msg = await bot.send_message(callback_query.message.chat.id, text=REGISTRATION_MESSAGE_2)
    user_data[user_id]["message_id"] = msg.message_id


#
##
# #
# ##
# # #
# ##
# #
##
#

def load_users():
    users = {}
    with open("USERS.txt", "r") as file:
        lines = file.readlines()

    user_data = {}
    for line in lines:
        line = line.strip()
        if line.startswith("User ID:"):
            user_id = int(line.split(":")[1].strip())
            users[user_id] = {}
            user_data = users[user_id]
        elif line:
            key, value = line.split(":", 1)
            user_data[key.strip()] = value.strip()

    return users


users = load_users()


def update_user_file():
    with open("USERS.txt", "w") as file:
        for user_id, user_info in users.items():
            file.write(f"User ID: {user_id}\n")
            for key, value in user_info.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")


def write_user_data_to_csv(user_id, user_info, username):
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['User ID', 'Username', 'Name', 'Date of Birth', 'Phone', 'Sex'])

    with open(csv_file, "r", newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        rows = list(csv_reader)

    updated = False
    for i, row in enumerate(rows):
        if row and row[0] == str(user_id):
            rows[i] = [user_id, username, user_info['name'], user_info['dob'], user_info['phone'], user_info['sex']]
            updated = True
            break

    if not updated:
        rows.append([user_id, username, user_info['name'], user_info['dob'], user_info['phone'], user_info['sex']])

    with open(csv_file, "w", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerows(rows)


#
#
# #
# # # funcs
# #
#
#


async def update_and_edit_message(chat_id, message_id, new_text):
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)


async def delete_and_send_new_message(message, text):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    new_message = await bot.send_message(chat_id=message.chat.id, text=text)
    return new_message.message_id


async def delete_and_edit_previous_message(message, new_text):
    user_id = message.from_user.id
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=user_data[user_id]["message_id"], text=new_text)


#
#
# #
# # # funcs
# #
#
#


# ----- NAME
@dp.message_handler(lambda message: message.from_user.id in user_data and "name" not in user_data[message.from_user.id])
async def process_name(message: types.Message):
    user_id = message.from_user.id
    user_name = message.text.strip()
    user_data[user_id]["name"] = user_name
    await delete_and_edit_previous_message(message, REGISTRATION_MESSAGE_3)


# ----- DATE OF BIRTH
@dp.message_handler(lambda message: message.from_user.id in user_data and "dob" not in user_data[message.from_user.id])
async def process_dob(message: types.Message):
    user_id = message.from_user.id
    dob = message.text.strip()
    user_data[user_id]["dob"] = dob
    await delete_and_edit_previous_message(message, REGISTRATION_MESSAGE_4)


# ----- PHONE
@dp.message_handler(
    lambda message: message.from_user.id in user_data and "phone" not in user_data[message.from_user.id])
async def process_phone(message: types.Message):
    user_id = message.from_user.id
    phone = message.text.strip()
    user_data[user_id]["phone"] = phone
    await delete_and_edit_previous_message(message, REGISTRATION_MESSAGE_5)


# ----- SEX
@dp.message_handler(lambda message: message.from_user.id in user_data and "sex" not in user_data[message.from_user.id])
async def process_sex(message: types.Message):
    username = message.from_user.username
    user_id = message.from_user.id
    sex = message.text.strip()
    user_data[user_id]["sex"] = sex

    users[user_id] = user_data[user_id]

    update_user_file()
    write_user_data_to_csv(user_id, user_data[user_id], username)

    current_user_data = [user_id, username, user_data[user_id]['name'], user_data[user_id]['dob'],
                         user_data[user_id]['phone'], user_data[user_id]['sex']]

    confirm_keyboard = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton(text=emoji.emojize("Заново :counterclockwise_arrows_button:"),
                             callback_data="reopen_registration_form"),
        InlineKeyboardButton(text=emoji.emojize("Все верно :check_mark_button:"),
                             callback_data="confirm_yes")
    )
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await bot.edit_message_text(
        chat_id=message.chat.id, message_id=user_data[user_id]["message_id"],
        text=f"Проверь информацию о себе:\n"
             f"ФИО: {user_data[user_id]['name']}\n"
             f"Дата рождения: {user_data[user_id]['dob']}\n"
             f"Номер телефона: {user_data[user_id]['phone']}\n"
             f"Пол: {sex}",
        reply_markup=confirm_keyboard
    )
    update_user_in_google_sheets(user_id, current_user_data, sheet_id, 'Лист1')


@dp.callback_query_handler(lambda c: c.data == "confirm_yes")
async def confirm_yes(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]["REGISTERED"] = True
    del user_data[user_id]["message_id"]
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=CONFIRM_REGISTRATION_MSG)


from google_sheet import *

#
#
##
# #
# ##
# # #
# # ##
# # # #
# # # ##
# # # # # |----------| РЕГИСТРАЦИЯ end
# # # ##
# # # #
# # ##
# # #
# ##
# #
##
#
#
