import telebot
from telebot import types
import webbrowser
import qrcode
import requests
from datetime import datetime
from pyowm import OWM
from pyowm.utils.config import get_default_config
from currency_converter import CurrencyConverter


def get_weather(city):
    """Функция возвращает погоду в городе"""

    language = get_default_config()
    language["language"] = "ru"
    owm = OWM('23232775d430e5fe2ac9a9c2cbdb8410', language)

    manager = owm.weather_manager()

    try:
        place = manager.weather_at_place(city)

        weather = place.weather
        result_of_weather = f"""
Сейчас на улице: {weather.detailed_status}
Облачность: {weather.clouds}%
Текущая температура: {weather.temperature("celsius").get("temp")} градусов
Максимальная температура: {weather.temperature("celsius").get("temp_max")} градусов
Минимальная температура: {weather.temperature("celsius").get("temp_min")} градусов
Сейчас ощущается: {weather.temperature("celsius").get("feels_like")} градусов  
Скорость ветра: {weather.wind()["speed"]}м/c
"""
    except:
        return "Некорректный ввод города(("


    return result_of_weather

def get_data():
    """Функция возвращает цена покупки и продажи битка"""

    request = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = request.json()

    # цена продажи/покупки битка
    sell_price = round(response["btc_usd"]["sell"], 2)
    buy_price = round(response["btc_usd"]["buy"], 2)

    return f"{datetime.now().strftime('%d/%b/%Y %H:%M')}\nSell price: {sell_price}\nBuy price: {buy_price}"

def main():
    bot = telebot.TeleBot("6271994553:AAGJx3KkAONcDibJMaAdRgzYOw2P_YqPz-g")
    currency = CurrencyConverter()
    ANSWER = 0

    def choose_currency(message):
        global ANSWER

        try:
            ANSWER = int(message.text.strip())
        except ValueError:
            bot.send_message(message.chat.id, "Некорректный ввод. Введите сумму:")
            bot.register_next_step_handler(message, choose_currency)

            # чтобы следующий код не выполнялся
            return

        if ANSWER > 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            button_1 = types.InlineKeyboardButton("USD/EUR", callback_data="USD/EUR")
            button_2 = types.InlineKeyboardButton("EUR/USD", callback_data="EUR/USD")
            button_5 = types.InlineKeyboardButton("Другое значение", callback_data="else")
            markup.add(button_1, button_2, button_5)

            bot.send_message(message.chat.id, "Выберите пару валют", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Сумма должна быть положительным числом. Введите сумму:")
            bot.register_next_step_handler(message, choose_currency)

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        values = call.data.split('/')
        result = currency.convert(ANSWER, values[0], values[1])

        value = f"""
{datetime.now().strftime('%d/%b/%Y %H:%M')}
Получается: {result}
"""
        bot.send_message(call.message.chat.id, value)          # ?????????????????????????????????????

    @bot.message_handler(content_types=["photo"])
    def get_photo(message):
        bot.reply_to(message, "Какое красивое фото!")

    @bot.message_handler(content_types=["video"])
    def get_video(message):
        bot.reply_to(message, "Какое красивое видео!")

    @bot.message_handler(commands=["start"])
    def start(message):

        info_about_bot = """Информация о боте:
"Привет" - бот поприветствует вас
"Пока" - бот попрощается с вами
"id" - бот скажет ваш id
"Ютуб" - откроет ютуб в браузере
"qrcode: [ваш текст]" - сгенерирует из текста QRCode
"bitcoin" - бот покажет текущую покупку и продажу биткоина
"Погода в '[ваш город в И.П]'"
-Вы можете отправить боту фото/видео и он оценит 
"""

        bot.send_message(message.chat.id, info_about_bot)

    @bot.message_handler(commands=["convert"])
    def convert(message):
        bot.send_message(message.chat.id, "Введите сумму:")
        bot.register_next_step_handler(message, choose_currency)

    @bot.message_handler()
    def answers(message):

        if message.text.lower() == "привет":
            bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")

        elif message.text.lower() == "пока":
            bot.send_message(message.chat.id, f"Пока, {message.from_user.first_name}!")

        elif message.text.lower() == "id":
            bot.reply_to(message, f"ID: {message.from_user.id}")

        elif message.text.lower() == "ютуб":
            webbrowser.open("https://www.youtube.com/")

        elif message.text.lower() == "bitcoin":
            bot.send_message(message.chat.id, get_data())

        elif message.text.lower().startswith("погода в "):
            index_left_quote = message.text.find("'")
            index_right_quote = message.text.rfind("'")

            city = message.text[index_left_quote + 1:index_right_quote]

            weather = get_weather(city)
            bot.send_message(message.chat.id, weather)

        # реализация qrcode
        elif message.text.lower().startswith("qrcode: "):
            image = qrcode.make(message.text[8:])
            image.save("myqrcode.png")

            with open("myqrcode.png", "rb") as file:
                bot.send_photo(message.chat.id, file)

        else:
            bot.send_message(message.chat.id, "Я не знаю такой команды😞")

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()



