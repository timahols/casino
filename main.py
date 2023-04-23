import asyncio
import json
import requests
from currency_converter import CurrencyConverter
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, types
from aiogram.utils import executor

TOKEN = 'YOUR TOKEN'
URL = 'http://data.fixer.io/api/latest?access_key=7370ff2962d49abefc56c32f5bc74aa8'  # ссылка API для конвертирования
APPID = '8266ef4bef0f1cc50f61f1126da6acd0'
CATS_URL = 'https://api.thecatapi.com/v1/images/search'  # ссылка API для котиков
# DOGS_URL = 'https://api.thedogapi.com/v1/images/search' #ссылка API для собачек

bot = Bot(token=TOKEN)
storage = MemoryStorage()
c = CurrencyConverter()
dp = Dispatcher(bot, storage=storage)

# Глобальные переменные
global user_money
global user_question

# Кнопка для возврата в меню функционала
back = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("Назад к функционалу↩")
back.add(item1)


# Класс для передачи данных
class ProfileStatesGroup(StatesGroup):
    city = State()
    money = State()
    fromm = State()
    to = State()
    question = State()
    answers = State()


# Старт диалога
@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    # Кнопки
    print(message.chat.id)
    # Перенесет в меню
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Посмотреть функционал")
    markup.add(item1)
    # Приветствие
    await bot.send_message(message.chat.id,
                           "<strong>Приветствую тебя, {first}</strong>\n\n"
                           "Я - современный многофункциональный бот\n\n"
                           "Благодаря мне учитываются с помощью опроса мнение каждого!\n\n"
                           "Милые котики не остаются без внимания\n\n"
                           "Будешь вкурсе погодных условий и всегда одеваться правильно!\n\n"
                           "И главное ты сможешь всегда остаться в плюсе с точным конвертором валют\n\n"
                           "Перейди в меню функций и убедись в это сам".format(
                               first=message.from_user.first_name),
                           reply_markup=markup,
                           parse_mode='html'
                           )


# обработчик текста
@dp.message_handler(content_types=['text'])
async def home(message: types.Message):
    # Ответное смс на "Посмотреть функционал" и кнопки меню
    if message.text == 'Посмотреть функционал' or message.text == 'Назад к функционалу↩':
        information_table = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Узнать погоду🌡")
        item2 = types.KeyboardButton("Конвертировать валюту💲")
        item3 = types.KeyboardButton("Получить фото котика🦁")
        item4 = types.KeyboardButton("Создать опрос")
        information_table.add(item1, item2, item3, item4)
        await bot.send_message(message.chat.id,
                               "<strong>Функционал</strong>\n\n"
                               "☔🌡Здесь ты можешь узнать текущую погоду в своем городе☔🌡\n\n"
                               "💲Конвертировать валюту💲\n\n"
                               "🐱Получить милую фоточку котика\n\n"
                               "👨‍👨‍👦Создавать опрос👨‍👨‍👦\n\n".format(
                                   first=message.from_user.first_name),
                               reply_markup=information_table,
                               parse_mode='html'
                               )
    # Обработает если пользователь напишет "Узнать погоду🌡"
    if message.text == 'Узнать погоду🌡':
        await bot.send_message(message.chat.id, 'Введи название своего города (Москва, Уфа, Челябинск)')
        # Перенесет текст сообщения в функцию "city"
        await ProfileStatesGroup.city.set()

    # Обработает если пользователь напишет "Конвертировать валюту💲"
    if message.text == 'Конвертировать валюту💲':
        await bot.send_message(message.chat.id, 'Введи сумму для конвертирования')
        # Перенесет текст сообщения в функцию "money"
        await ProfileStatesGroup.money.set()

    # Обработает если пользователь напишет "Получить фото котика🦁"
    if message.text == 'Получить фото котика🦁':
        response = requests.get(CATS_URL)  # запрос
        response = response.json()  # перевод в json()
        print(response)  # вывод для мониторинга происходящего
        random_cat = response[0].get('url')  # сортировка и выбор только ссылки
        await bot.send_message(message.chat.id, f'{random_cat}')  # отправка ссылки

    # Обработает если пользователь напишет "Создать опрос"
    if message.text == 'Создать опрос':
        await bot.send_message(message.chat.id, 'Введи вопрос для опроса')
        # Перенесет текст сообщения в функцию "question"
        await ProfileStatesGroup.question.set()


# Сюда перенеслись после того как ввели "Создать опрос"
@dp.message_handler(state=ProfileStatesGroup.question)
async def load_digit(message: types.Message) -> None:
    global user_question  # Глобальная чтоб в след функции можно было использовать
    # Обработчик ошибок если пользователь ввел вместо вопроса число
    try:  # В случаи успеха произойдет
        user_question = str(message.text)
        await bot.send_message(message.chat.id, 'Введи через запятую варианты ответа\n\n'
                                                'Пример: (Да, нет, возможно)')
        # Переносимся для создания ответов в другую функцию
        await ProfileStatesGroup.answers.set()
    except ValueError:  # Если возникла ошибка ввода
        await bot.send_message(message.chat.id, 'Некорректный ввод!\n\n'
                                                'Возможно ты ввел цифры')
        await ProfileStatesGroup.answers.set()


# Функция для создания ответов и опроса в целом
@dp.message_handler(state=ProfileStatesGroup.answers)
async def load_digit(message: types.Message, state: FSMContext) -> None:
    global user_question  # Сделаем локальный повтор для подстраховки
    user_answers = list(map(str, message.text.split(', ')))  # разобьем то что ввел пользователь через запятую
    json_str_1 = json.dumps(user_answers)  # переделаем в json (телеграмм создает только в json)
    print("\nПользователь ввел:", json_str_1)  # для мониторинга происходящего

    # Обработчик ошибок если при запросе в телеграмме API произойдет ошибка (ввел цифры, или не так как в примере)
    try:  # В случаи успеха
        base_url = f"https://api.telegram.org/bot{TOKEN}/sendPoll"  # Ссылка API

        parameters = {  # Параметры
            "chat_id": f"{message.chat.id}",
            "question": f"{user_question}",
            "options": json_str_1,
            'is_anonymous': False,
        }
        await bot.send_message(message.chat.id, 'Опрос создается...',
                               reply_markup=back)  # обратная связь и возможность вернуться в меню
        resp = requests.get(base_url, data=parameters)  # запрос
        print(resp.raise_for_status())  # для мониторинга
        await state.finish()  # завершим чтоб можно было выйти в меню функционала
    # Если возникла ошибка
    except (
            requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout) as err:  # Виды ошибок
        print(err)
        await bot.send_message(message.chat.id, f'Что-то пошло не так, попробуй еще раз заново\n\n'
                                                f'Попробуй написать как в примере (с учетом пробелов)',
                               reply_markup=back)
        await state.finish()


# Сюда перенеслись после того как ввели "Конвертировать валюту"
@dp.message_handler(state=ProfileStatesGroup.money)
async def load_digit(message: types.Message) -> None:
    # Обработчик ошибок (если ввел не число)
    try:
        global user_money  # Повтор локально
        user_money = int(message.text)  # переведем в int
        if user_money > 0:  # Конвертировать невозможно то что <= 0
            print('user ввел сумму: ', user_money)  # для мониторинга
            await bot.send_message(message.chat.id, 'Из какой валюты ты хочешь конвертировать? (RUB, USD, EUR)')
            # перенесемся в функцию где указываем из какой валюту конвертируем
            await ProfileStatesGroup.fromm.set()
        else:
            await bot.send_message(message.chat.id, 'Введите число больше 0!')
            # Возврат обратно для корректного ввода
            await ProfileStatesGroup.money.set()
    # В случаи ошибок
    except ValueError:
        await bot.send_message(message.chat.id, 'Вы ввели не цифры, введите сумму')
        await ProfileStatesGroup.money.set()
    except KeyError:
        await bot.send_message(message.chat.id, 'Вы ввели не цифры, введите сумму')
        await ProfileStatesGroup.money.set()


# Место где указываем из какой валюты
@dp.message_handler(state=ProfileStatesGroup.fromm)
async def load_digit(message: types.Message) -> None:
    global user_from_money  # Повтор
    user_from_money = message.text.upper()  # переведем в верхний регистр
    await bot.send_message(message.chat.id, 'В какую валюту ты хочешь конвертировать? (RUB, USD, EUR)')
    # Переход вместо где укажем в какую валюту
    await ProfileStatesGroup.to.set()


# Место где указываем в какую валюту и выдаем сразу ответ
@dp.message_handler(state=ProfileStatesGroup.to)
async def load_digit(message: types.Message, state: FSMContext) -> None:
    # Обработчик если ввел цифры или несуществующую валюту
    try:  # В случаи успеха
        to_currency = message.text.upper()  # переведем в верхний регистр
        response = requests.get(URL)  # Запрос по API
        rate = response.json()['rates'][user_from_money]
        amount_in = user_money / rate
        amount = amount_in * (response.json()['rates'][to_currency])
        amount = round(amount, 1)  # Кол-ва чисел после запятой
        await bot.send_message(message.chat.id, f'Получилось: {amount}', reply_markup=back)
        await state.finish()
    # В случаи ошибок
    except KeyError:
        await bot.send_message(message.chat.id, f'Что-то пошло не так, попробуй еще раз заново\n\n'
                                                f'Попробуй написать как в примере;)', reply_markup=back)
        await state.finish()


# Место куда мы перенеслись после смс "Узнать погоду"
@dp.message_handler(state=ProfileStatesGroup.city)
async def load_digit(message: types.Message, state: FSMContext) -> None:
    user_city = str(message.text)  # Переведем в строку
    # Обработчик если ввел число или не существующий город
    try:  # В случаи успеха
        print('user назвал город:', user_city)  # мониторинг
        s_city = f"{user_city},RU"
        res = requests.get("http://api.openweathermap.org/data/2.5/weather?",  # Запрос с параметрами
                           params={'q': s_city, 'lang': 'ru', 'APPID': APPID})
        data = res.json()
        temperature = int(data['main']['temp'] - 273.15)  # возьмем из json температуру
        weather = data['weather'][0]['description']  # Возьмем теперь погодные условия
        await bot.send_message(message.chat.id, f"Загрузка погодных данных твоего города..\n\n",
                               reply_markup=back)  # Небольшая задержка + возможность вернуться потом в меню
        await asyncio.sleep(5)
        # В зависимость от температуры выдаем соответствующее смс о том, что холодно/тепло/прохладно
        if temperature >= 10:
            await bot.send_message(message.chat.id, f"Сегодня весьма тепло - +{temperature}C\n\n"
                                                    f"За бортом - {weather}\n\n")
        elif temperature < 10:
            await bot.send_message(message.chat.id, f"Сегодня прохладно - +{temperature}C\n\n"
                                                    f"За бортом - {weather}\n\n")
        elif temperature < 5:
            await bot.send_message(message.chat.id, f"Сегодня холодно - +{temperature}C\n\n"
                                                    f"За бортом - {weather}\n\n")
        elif temperature < 0:
            await bot.send_message(message.chat.id, f"Сегодня ниже 0!! - -{temperature}C\n\n"
                                                    f"За бортом - {weather}\n\n")
        await state.finish()
    # Если произошла ошибка
    except KeyError:
        await bot.send_message(message.chat.id, 'Некорректный ввод, введи название города!')
        await ProfileStatesGroup.city.set()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
