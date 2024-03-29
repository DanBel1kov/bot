from main import *

annonce = {}

ADMINS = [832935844]
CUR_STATE = {}
CUR_MESSAGE = []

user_data = readdata()


async def delete_and_edit_previous_message(message, new_text):
    user_id = str(message.from_user.id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    print(user_data)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=user_data[user_id]["message_id"], text=new_text)


@dp.message_handler(lambda message: message.from_user.id not in CUR_STATE, commands=['post'])
async def post(message: types.Message):
    if message.from_user.id not in ADMINS:
        # await delete_and_edit_previous_message(message, "У вас нет прав")
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        CUR_STATE[message.from_user.id] = 'posting_text'
        await bot.send_message(message.from_user.id, "Отправьте текст")
        # await delete_and_edit_previous_message(message, "Отправьте текст")


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
    # await bot.delete_message()
    photo = msg.photo[-1].file_id
    await bot.send_photo(msg.from_user.id, photo=photo)  # TODO add posting for all users
    await bot.send_message(msg.from_user.id, CUR_MESSAGE[0])
    CUR_STATE.pop(msg.from_user.id)


#
#
# for annonce
#
#

@dp.message_handler(lambda message: message.from_user.id not in CUR_STATE, commands=['annonce'])
async def post(message: types.Message):
    await message.delete()
    if message.from_user.id not in ADMINS:
        await bot.send_message(message.from_user.id, "У вас нет прав")
    else:
        CUR_STATE[message.from_user.id] = 'posting_text_anonce'
        await bot.send_message(message.from_user.id, "Отправьте текст")


@dp.message_handler(
    lambda message: message.from_user.id in CUR_STATE and CUR_STATE[message.from_user.id] == 'posting_text_anonce')
async def readmsg(msg: types.Message):
    await msg.delete()
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



    if nRates == 1:

        await bot.send_photo(msg.from_user.id, photo, caption=annonce[msg.from_user.id]['text'],
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
        await bot.send_photo(msg.from_user.id, photo, caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                      callback_data='second'))
                             )
    elif nRates == 3:
        await bot.send_photo(msg.from_user.id, photo, caption=annonce[msg.from_user.id]['text'],
                             reply_markup=InlineKeyboardMarkup(row_width=nRates).add(
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][0]),
                                                      callback_data='first'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][1]),
                                                      callback_data='second'),
                                 InlineKeyboardButton(text="{}".format(annonce[msg.from_user.id]['allRates'][2]),
                                                      callback_data='third'))
                             )
    elif nRates == 4:
        await bot.send_photo(msg.from_user.id, photo, caption=annonce[msg.from_user.id]['text'],
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
                               InlineKeyboardButton(text="Оплатить",
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
                               InlineKeyboardButton(text="Оплатить",
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
    await bot.send_message(call.from_user.id, "Тариф выбран!")
    CUR_STATE.pop(call.from_user.id)
