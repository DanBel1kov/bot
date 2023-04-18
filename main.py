from aiogram import Bot, Dispatcher, types, executor

TOKEN_API = "6156845668:AAG7Esqiw1MT9VBX0qZRnfMEmtCDYag3i-U"

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo_upper(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp)
