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
# # # # # |----------| ПРОВЕРКА ПОДПИСКИ begin
# # # ##
# # # #
# # ##
# # #
# ##
# #
##
#
#


class CancelHandler(Exception):
    pass


def is_subscribed(chat_member):
    return chat_member['status'] != 'left'


def is_banned(chat_member):
    return chat_member['status'] == 'kicked'


class ChannelMembershipMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.text and message.text.startswith('/start'):
            return True

        chat_member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)

        if is_subscribed(chat_member):
            return True
        elif is_banned(chat_member):
            await message.delete()
            await message.answer(text=BANNED_TEXT)
            raise CancelHandler()
        else:
            await message.delete()
            keyboard = InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton(text="Группа", url=CHANNEL_LINK),
                InlineKeyboardButton(text=emoji.emojize('готово :check_mark_button:'),
                                     callback_data="verify_subscription")
            )
            await message.answer(text=NOT_SUBSCRIBED_MESSAGE, reply_markup=keyboard)
            raise CancelHandler()


dp.middleware.setup(ChannelMembershipMiddleware())


@dp.callback_query_handler(lambda c: c.data == "verify_subscription")
async def verify_subscription(callback_query: types.CallbackQuery):
    chat_member = await bot.get_chat_member(CHANNEL_ID, callback_query.from_user.id)
    if is_subscribed(chat_member):
        await bot.send_message(callback_query.message.chat.id,
                               text=emoji.emojize("Я вижу что ты в теме :winking_face:"))
    else:
        InlineKeyboardMarkup().add(InlineKeyboardButton("Verify Subscription", callback_data="verify_subscription"))
        await callback_query.answer(text=NOT_SUBSCRIBED_MESSAGE2, show_alert=True)


@dp.errors_handler(exception=CancelHandler)
async def handle_cancel_handler():
    return True

#
#
##
# #
# ##
# # #
# # ##
# # # #
# # # ##
# # # # # |----------| ПРОВЕРКА ПОДПИСКИ end
# # # ##
# # # #
# # ##
# # #
# ##
# #
##
#
#
