import telebot
from telebot import types
import webbrowser
import qrcode
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
from pyowm import OWM
from pyowm.utils.config import get_default_config
from currency_converter import CurrencyConverter


def get_now_date():
    return datetime.now().strftime(f'%d/%b/%Y %H:%M')

def get_joke():
    """Функция, которая возвращает список из шуток"""
    URL = "https://www.anekdot.ru/last/good/"

    request = requests.get(URL)
    soup = BeautifulSoup(request.text, "html.parser")
    jokes = soup.find_all("div", class_="text")
    clear_jokes = [joke.text for joke in jokes]

    return clear_jokes

def get_data():
    """Функция, которая возвращает цену покупки и продажи битка"""

    request = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = request.json()

    # цена продажи/покупки битка
    sell_price = round(response["btc_usd"]["sell"], 2)
    buy_price = round(response["btc_usd"]["buy"], 2)

    return f"{get_now_date()}\nSell price: {sell_price}\nBuy price: {buy_price}"

def main():
    bot = telebot.TeleBot("6271994553:AAGJx3KkAONcDibJMaAdRgzYOw2P_YqPz-g")
    currency = CurrencyConverter()

    def get_qrcode(message):
        image = qrcode.make(message.text)
        image.save("myqrcode.png")

        with open("myqrcode.png", "rb") as file:
            bot.send_photo(message.chat.id, file)

    def get_weather(message):
        """Функция возвращает погоду в городе"""

        language = get_default_config()
        language["language"] = "ru"
        owm = OWM('23232775d430e5fe2ac9a9c2cbdb8410', language)

        manager = owm.weather_manager()

        try:
            city = message.text
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
            bot.send_message(message.chat.id, result_of_weather)

        except:
            bot.send_message(message.chat.id, "Некорректный ввод города((\nВведите город")
            bot.register_next_step_handler(message, get_weather)

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
            button_3 = types.InlineKeyboardButton("Другое значение", callback_data="else")
            markup.add(button_1, button_2, button_3)

            bot.send_message(message.chat.id, "Выберите пару валют", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Сумма должна быть положительным числом. Введите сумму:")
            bot.register_next_step_handler(message, choose_currency)

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):

        if call.data != "else":
            values = call.data.split('/')
            result = currency.convert(ANSWER, values[0], values[1])

            value = f"""
            {get_now_date()}
            Получается: {round(result, 2)}
            """
            bot.send_message(call.message.chat.id, value)
        else:
            bot.send_message(call.message.chat.id, "Введите пару валют через слэш:")
            bot.register_next_step_handler(call.message, my_currency)

    def my_currency(message):

        try:
            values = message.text.upper().split("/")
            result = currency.convert(ANSWER, values[0], values[1])

            value = f"{get_now_date()}\nПолучается: {round(result, 2)}"
            bot.send_message(message.chat.id, value)
        except:
            bot.send_message(message.chat.id, "Некорректный ввод. Введите пару валют через слэш:")
            bot.register_next_step_handler(message, my_currency)

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
"convert" - бот с конвертирует валюту
"Ютуб" - откроет ютуб в браузере
"qrcode" - сгенерирует из текста QRCode
"bitcoin" - бот покажет текущую покупку и продажу биткоина
"Погода" - бот спросит город для показа погоды
"Анекдот" - бот расскажет анекдот
"Дата" - бот скажет точную дату
-Вы можете отправить боту фото/видео и он оценит 
"""

        bot.send_message(message.chat.id, info_about_bot)

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

        elif message.text.lower() == "погода":
            bot.send_message(message.chat.id, "Введите город:")
            bot.register_next_step_handler(message, get_weather)

        elif message.text.lower() == "анекдот":
            joke = random.choice(get_joke())
            bot.send_message(message.chat.id, joke)

        elif message.text.lower() == "convert":
            bot.send_message(message.chat.id, "Введите сумму:")
            bot.register_next_step_handler(message, choose_currency)

        elif message.text.lower() == "дата":
            bot.send_message(message.chat.id, get_now_date())

        # реализация qrcode
        elif message.text.lower() == "qrcode":
            bot.send_message(message.chat.id, "Введите текст для конвертации в qrcode:")
            bot.register_next_step_handler(message, get_qrcode)

        else:
            bot.send_message(message.chat.id, "Я не знаю такой команды😞")

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()



