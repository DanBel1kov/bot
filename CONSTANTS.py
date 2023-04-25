

API_TOKEN = "5942173865:AAF6goSFqJACn02FGPK9gMy_J8-tAFjrrHs"
CHAT_ID = "@syetnoibot"
CHANNEL_ID = -1001738772333
CHANNEL_LINK = 'https://t.me/ggrtcvnjj'

HELP_COMMAND = """
/start - перезапуск бота
/help - список команд
/register - пройти регистрацию 
               """


def START_MESSAGE(name):
    return "Привет, {}! {}".format(name, INTRO_TEXT)


INTRO_TEXT = """
Крутое вступительное сообщение которое мне лень придумывать! 
Для полного списка команд напиши мне /help
             """

NOT_SUBSCRIBED_MESSAGE = """
Для доступа к функционалу бота подпишитесь на группу
                         """
NOT_SUBSCRIBED_MESSAGE2 = """
Для продолжения вы должны подписаться на группу
                         """

BANNED_TEXT = """
К сожалению, вы не соблюдали правила сообщества и поэтому доступ к боту вам запрещен.
              """

REGISTRATION_MESSAGE_1 = """
                         """
REGISTRATION_MESSAGE_2 = """
Для регистрации расскажи мне немного о себе:

Как тебя зовут?
(ФИО как в паспорте)
                         """
REGISTRATION_MESSAGE_3 = """
Когда у тебя день рождения
(формат: YYYY-MM-DD)
                         """
REGISTRATION_MESSAGE_4 = """
Ваш номер телефона
(формат: +70007777777)
                         """
REGISTRATION_MESSAGE_5 = """
Твой пол
(М/Ж)
                         """

CONFIRM_REGISTRATION_MSG = ("Спасибо, теперь вы есть в базе!")
