from aiogram import Bot, Dispatcher, types, executor
from CONSTANTS import HELP_COMMAND, START_MESSAGE, TOKEN_API


bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(text=HELP_COMMAND)


@dp.message_handler(commands=['start'])
async def help_command(message: types.Message):
    first_name = message.from_user.first_name
    username = message.from_user.username
    await message.answer(text=START_MESSAGE(first_name))
    await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp)
