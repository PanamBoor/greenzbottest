from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from keyboards import greet_kb
from aiogram.dispatcher.filters import Command, Text

# подключаем бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

id = []


# команда start
@dp.message_handler(Command('start'))
async def welcome(message: types.Message):
    print("/start", message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f'{message.from_user.first_name},для работы необходимо зарегестрироваться.\nЭто займет пару минут.\n\n' \
                           + 'Шаг 1/3.Укажите электронную почту(только @gmail.com).К ящику будет привязана google-таблица с Вашими финансами',
                           parse_mode='HTML')




@dp.message_handler()
async def adress_msg(message):
    print("text message", message.from_user.id)
    # cоздем словарь где хранятся виды электронной почты
    gmail = ['@gmail.com', 'abcdefghijklmnopqrstuvwxyz@.']
    adress = message.text
    # пишем проверку на правильность ввода электронной почты
    for i in gmail:
        if i in adress:
            await bot.send_message(message.from_user.id,
                                f'Дождитесь завершения регестрации! Это может занять пару минут',
                                parse_mode='HTML')
            CREDENTIALS_FILE = 'cread.json'  # Имя файла с закрытым ключом, вы должны подставить свое

            # Читаем ключи из файла
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, [
            'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

            httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
            service = apiclient.discovery.build('sheets', 'v4',
                                                http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
            await bot.send_message(message.from_user.id, "Создание таблицы")
            spreadsheet1 = service.spreadsheets().create(body={
            'properties': {'title': adress, 'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                        'sheetId': 0,
                                        'title': 'Сводка',
                                        'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
            }).execute()

            await bot.send_message(message.from_user.id, "Регистрация")
            spreadsheetId = spreadsheet1['spreadsheetId']  # сохраняем идентификатор файла
            driveService = apiclient.discovery.build('drive', 'v3',
                                                     http=httpAuth)  # Выбираем работу с Google Drive и 3 версию API
            access = driveService.permissions().create(
                fileId=spreadsheetId,
                body={'type': 'user', 'role': 'writer', 'emailAddress': adress},
                # Открываем доступ на редактирование
                fields='id'
            ).execute()

            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": "Статистика",
                                "gridProperties": {
                                    "rowCount": 20,
                                    "columnCount": 12
                                }
                            }
                        }
                    }
                ]
                }
                ).execute()

            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Графики",
                                    "gridProperties": {
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Графиков")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Расходы",
                                    "gridProperties": {
                                         "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Расходов")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Доходы",
                                    "gridProperties": {
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Доходов")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Долги",
                                     "gridProperties": {
                                            "rowCount": 20,
                                            "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Долгов")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Бюджеты",
                                    "gridProperties": {
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Иннициализация бюджетов")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Источники",
                                    "gridProperties": {
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Источников")
            # Добавление листа
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": "Категории",
                                    "gridProperties": {
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            await bot.send_message(message.from_user.id, "Инициализация Категории")
            await bot.send_message(message.from_user.id,
                                'https://docs.google.com/spreadsheets/d/' + spreadsheetId)
            break
        else:
            await bot.send_message(message.from_user.id,
                                f'Вы ввели недопустимую почту.Введите почту с @gmail.com',
                                parse_mode='HTML')
        break





# команда help
@dp.message_handler(Command('help'))
async def help(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f'Cправка\n\n\n/balance - Мой баланс \n/table - Ссылка на google-таблицу\n/sync - Синхронизация бота с google-таблицой\n/settings - Настройка \n/help  - Справка \n/delete - Удаление аккаунта \n\n'
                           f'Выберите интересующий раздел справки и получите краткую помощь.Если Ваш вопрос не решен,то обратитесь за помощью.Если  Ваш вопрос не решен , то обратитесь за помощью к живому оператору @......',
                           parse_mode='HTML', reply_markup=greet_kb)


# запуск телеграм бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)