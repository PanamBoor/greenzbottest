# подключаем все нужные библиотеки
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types
import httplib2
from keyboards import greet_kb, greet_settings, greet_time, greet_delete
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlite_db_worker import *
from datetime import *

memory_storage = MemoryStorage()
# подключаем токен бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=memory_storage)
CREDENTIALS_FILE = 'cread.json'  # Имя файла с закрытым ключом, вы должны подставить свое
# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, [
    'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API


class registration(StatesGroup):
    waiting_for_gmail = State()
    waiting_for_sity = State()
    waiting_for_budjet = State()
    waiting_for_new_data = State()
    waiting_for_answer_of_delete = State()


# команда start
@dp.message_handler(commands="start", state="*")
async def start(message: types.Message):
    # Проверка есть ли пользователь уже в базе?
    if get_have_user_in_a_base(user_id=message.from_user.id) == 0:
        await bot.send_message(message.from_user.id,
                               f'{message.from_user.first_name}, для работы необходимо зарегестрироваться.\nЭто займет меньше минуты.\n\n' \
                               + 'Шаг 1/3.Укажите электронную почту(только @gmail.com). К ящику будет привязана google-таблица с Вашими финансами')
        await registration.waiting_for_gmail.set()
    else:
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированы!")


# регистрация пользователя этап первый
@dp.message_handler(state=registration.waiting_for_gmail, content_types=types.ContentTypes.TEXT)
async def email(message: types.Message, state: FSMContext):
    # сохраняю адресс пользователя
    await state.update_data(gmail=message.text)
    user_data = await state.get_data()
    gmail = user_data['gmail']
    # cоздем словарь где хранятся виды электронной почты
    check_email = ['@gmail.com', 'abcdefghijklmnopqrstuvwxyz@.']
    # пишем проверку на правильность ввода электронной почты
    for i in check_email:
        if i in gmail:
            # если почта прошла проверку, то бот начинает регистрацию
            await bot.send_message(message.from_user.id,
                                   f'Дождитесь завершения регестрации! Это может занять пару минут')
            await registration.next()

            spreadsheet = service.spreadsheets().create(body={
                'properties': {'title': 'Penny - мои финансы', 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': 'Расходы',
                                           'gridProperties': {'rowCount': 200, 'columnCount': 30}}}]
            }).execute()
            await bot.send_message(message.from_user.id, "Создание таблицы....")
            spreadsheetId = spreadsheet['spreadsheetId']  # сохраняем идентификатор файла
            print("Great spreadsheetId is: " + spreadsheetId)
            await state.update_data(spreedsheetidofuser=spreadsheetId)
            # сохраняю ссылку на таблицу
            global link
            link = 'https://docs.google.com/spreadsheets/d/' + spreadsheetId
            driveService = apiclient.discovery.build('drive', 'v3',
                                                     http=httpAuth)  # Выбираем работу с Google Drive и 3 версию API
            access = driveService.permissions().create(
                fileId=spreadsheetId,
                body={'type': 'user', 'role': 'writer', 'emailAddress': gmail},
                # Открываем доступ на редактирование
                fields='id'
            ).execute()
            await bot.send_message(message.from_user.id, "Регистрация....")
            # Добавление листа Доходы
            await bot.send_message(message.from_user.id, "Иннициализация доходов....")
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
                                        "rowCount": 100,
                                        "columnCount": 20
                                    }
                                }
                            },

                        }
                    ]
                }).execute()
            # Добавление листа Долги
            await bot.send_message(message.from_user.id, "Иннициализация долгов....")
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
                                        "rowCount": 100,
                                        "columnCount": 20
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            # Добавление листа Бюджеты
            await bot.send_message(message.from_user.id, "Иннициализация бюджетов....")
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
                                        "rowCount": 100,
                                        "columnCount": 20
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            # Добавление листа Источники
            await bot.send_message(message.from_user.id, "Иннициализация источников....")
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
                                        "rowCount": 100,
                                        "columnCount": 20
                                    }
                                }
                            }
                        }
                    ]
                }).execute()
            # Добавление листа Категории
            await bot.send_message(message.from_user.id, "Иннициализация категорий....")
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
                                        "rowCount": 100,
                                        "columnCount": 20
                                    }
                                }
                            }

                        }
                    ]
                }).execute()
            DATA = {'requests': [
                {'repeatCell': {
                    'range': {'endRowIndex': 1},
                    'cell': {'userEnteredFormat': {'textFormat': {'bold': True}}},
                    'fields': 'userEnteredFormat.textFormat.bold',
                }}

            ]}
            # Получаем список листов, их Id и название
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
            sheetList = spreadsheet.get('sheets')
            for sheet in sheetList:
                print(sheet['properties']['sheetId'], sheet['properties']['title'])

            sheetId_rashod = sheetList[0]['properties']['sheetId']
            sheetId_dohod = sheetList[1]['properties']['sheetId']
            sheetId_dolg = sheetList[2]['properties']['sheetId']
            sheetId_budjet = sheetList[3]['properties']['sheetId']
            sheetId_istochniki = sheetList[4]['properties']['sheetId']
            sheetId_kategorii = sheetList[5]['properties']['sheetId']

            # Расходы заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Расходы!A1:G1000",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Дата", "Бюджет", "Источник", "Категория", "Сумма", "Примечание"],
                         # Заполняем первую строку

                     ]},

                ]
            }).execute()

            # Доходы заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Доходы!A1:F1000",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Дата", "Источник", "Категория", "Сумма", "Примечание"],  # Заполняем первую строку
                     ]},

                ]
            }).execute()

            # Долги заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Долги!A1:G1000",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Дата открытия", "Категория", "Сумма", "Примечание", "Дата закрытия"],
                         # Заполняем первую строку
                     ]}
                ]
            }).execute()

            # Бюджеты заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Бюджеты!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Вкл", "Основной", "Наименование", "Лимит", "Период", "Синонимы"],
                         ["", "1", "1", "Ежемесячные расходы", "", "Месяц", ""],
                         ["", "1", "0", "Годовые расходы", "", "Год", "годовые, годовой, год"],
                         ["", "1", "0", "Внебюджет", "", "Год", "вне"]
                     ]},

                ]
            }).execute()

            # Источники заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Источники!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Вкл", "Основной", "Наименование", "Синонимы", "Начальное значение"],
                         # Заполняем первую строку
                         ["", "1", "0", "Карта", "виза, visa, кард, кредитка, сбербанк, сбер, втб, альфа, сити", "0"]
                         # Заполняем вторую строку
                     ]}
                ],

            }).execute()
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId, body=DATA).execute()
            # Категории заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Категории!A1:G50",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         # заполняем строки
                         ["ID", "Вкл", "Отображать в расходах", "Отображать в доходах", "Отображать в долгах",
                          "Наименование", "Синонимы"],  # Заполняем первую строку
                         ["", "1", "1", "0", "0", "Автомобиль",
                          "авто, машина, бенз, бензин, гараж, стоянка, осаго, то"],  # Заполняем 2 строку
                         ["", "1", "1", "0", "0", "Активный отдых", "велосипед, лыжи, сноуборд"],  # Заполняем 3 строку
                         ["", "1", "1", "0", "0", "Алкоголь", "спиртное, пиво, вино, водка, коньяк"],
                         # Заполняем 4 строку
                         ["", "1", "1", "0", "0", "Благотворительность", ""],  # Заполняем 5 строку
                         ["", "1", "1", "0", "0", "Девушка", "девушка"],  # Заполняем 6 строку
                         ["", "1", "1", "0", "0", "Дети", "ребенок, сын, доч, сад, садик, школа"],  # Заполняем 7 строку
                         ["", "1", "1", "0", "0", "Еда вне дома", "обед, ланч, кфс, kfc, мак, макдак, макфак, кофе"],
                         # Заполняем 8 строку
                         ["", "1", "1", "0", "0", "Здоровье",
                          "аптека, больница, поликлиника, стоматолог, зубной, врач, баня"],  # Заполняем 9 строку
                         ["", "1", "1", "0", "0", "Квартира", "кварплата, газ, свет, домофон"],  # Заполняем 10 строку
                         ["", "1", "1", "0", "0", "Красота",
                          "прическа, стрижка, парикмахер, парикмахерская, макияж, визаж, ногти, маникюр, педикюр"],
                         # Заполняем 11 строку
                         ["", "1", "1", "0", "0", "Курение", "табак, сигареты, кальян, курево, электронка"],
                         # Заполняем 12 строку
                         ["", "1", "1", "0", "0", "Неразобранное", ""],  # Заполняем 13 строку
                         ["", "1", "1", "0", "0", "Образование", "книги, английский, репетитор"],  # Заполняем 14 строку
                         ["", "1", "1", "0", "0", "Одежда", "обувь"],  # Заполняем 15 строку
                         ["", "1", "1", "0", "0", "Подарки", "подарок, день рождения, др, цветы"],
                         # Заполняем 16 строку
                         ["", "1", "1", "0", "0", "Покупки", ""],  # Заполняем 17 строку
                         ["", "1", "1", "0", "0", "Продукты",
                          "питание, еда, хавчик, хлеб, мороженое, вода, сок, арбуз"],  # Заполняем 18 строку
                         ["", "1", "1", "0", "0", "Промтовары", "гигиена, быт"],  # Заполняем 19 строку
                         ["", "1", "1", "0", "0", "Прочее", "другое"],  # Заполняем 20 строку
                         ["", "1", "1", "0", "0", "Путешествия", "тур, самолет, авиа"],  # Заполняем 21 строку
                         ["", "1", "1", "0", "0", "Работа", "ооо, ип"],  # Заполняем 22 строку
                         ["", "1", "1", "0", "0", "Развлечения", "кафе, ресторан, бар, паб, клуб, кино"],
                         # Заполняем 23 строку
                         ["", "1", "1", "0", "0", "Связь", "телефон, интернет, мобильный, мегафон, мтс, билайн, теле2"],
                         # Заполняем 24 строку
                         ["", "1", "1", "0", "0", "Семья", "жена, муж"],  # Заполняем 25 строку
                         ["", "1", "1", "0", "0", "Спорт", "танцы, фитнес, зал"],  # Заполняем 26 строку
                         ["", "1", "1", "0", "0", "Транспорт",
                          "проезд, такси, переправа, дорога, метро, автобус, трамвай, троллейбус, подорожник, маршрутка"],
                         # Заполняем 27 строку
                         ["", "1", "0", "1", "0", "Зарплата", "зарплата, зп, оклад, аванс"],  # Заполняем 28 строку
                         ["", "1", "0", "0", "1", "Мне должны", "долг, должник, мне должны, должны"],
                         # Заполняем 29 строку
                         ["", "1", "0", "0", "1", "Я должен", "кредит, я должен, должен"],  # Заполняем 30 строку
                     ]
                     }
                ]
            }).execute()

            # Установка формата ячеек расход
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_rashod,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 7
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()

            # Установка формата ячеек доход
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_dohod,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 6
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()
            # Установка формата ячеек доход
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_dolg,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 6
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()
            # Установка формата ячеек бюджеты
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_budjet,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 7
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()

            # Установка формата ячеек источники
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_istochniki,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 6
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()

            # Установка формата ячеек категории
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body=
                {
                    "requests":
                        [
                            {
                                "repeatCell":
                                    {
                                        "cell":
                                            {
                                                "userEnteredFormat":
                                                    {
                                                        "verticalAlignment": 'MIDDLE',
                                                        "horizontalAlignment": 'CENTER',
                                                        "backgroundColor": {
                                                            "red": 0.8,
                                                            "green": 0.8,
                                                            "blue": 0.8,
                                                            "alpha": 1
                                                        },
                                                        "textFormat":
                                                            {
                                                                "bold": True,
                                                                "fontSize": 9
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId_kategorii,
                                                "startRowIndex": 0,
                                                "endRowIndex": 1,
                                                "startColumnIndex": 0,
                                                "endColumnIndex": 7
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()

            # задаем размеры таблиц
            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Бюджеты размер .
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_budjet,
                                "dimension": "COLUMNS",
                                "startIndex": 6,
                                "endIndex": 7
                            },
                            "properties": {
                                "pixelSize": 150,
                            },

                            "fields": "pixelSize"

                        },

                    },
                    # Таблица Бюджеты размер .
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_budjet,
                                "dimension": "COLUMNS",
                                "startIndex": 3,
                                "endIndex": 4
                            },
                            "properties": {
                                "pixelSize": 150,
                            },

                            "fields": "pixelSize"

                        },

                    }

                ]
            }).execute()
            # задаем размеры таблиц
            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Источники размер.
                    # Задать ширину столбцов E : 150 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_istochniki,
                                "dimension": "COLUMNS",
                                "startIndex": 4,
                                "endIndex": 5
                            },
                            "properties": {
                                "pixelSize": 150,

                            },
                            "fields": "pixelSize"
                        }
                    },
                    # Задать ширину столбца F: 200 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_istochniki,
                                "dimension": "COLUMNS",
                                "startIndex": 5,
                                "endIndex": 6
                            },
                            "properties": {
                                "pixelSize": 200
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }).execute()
            # задаем размеры таблиц
            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Категории размер.
                    # Задать ширину столбца A: 20 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {

                                "sheetId": sheetId_kategorii,
                                "dimension": "COLUMNS",  # Задаем ширину колонки
                                "startIndex": 0,  # Нумерация начинается с нуля
                                "endIndex": 1  # Со столбца номер startIndex по endIndex - 1 (endIndex не входит!)
                            },
                            "properties": {
                                "pixelSize": 70  # Ширина в пикселях
                            },
                            "fields": "pixelSize"  # Указываем, что нужно использовать параметр pixelSize
                        }
                    },
                    # Задать ширину столбцов B: 70 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "dimension": "COLUMNS",
                                "startIndex": 1,
                                "endIndex": 2
                            },
                            "properties": {
                                "pixelSize": 70
                            },
                            "fields": "pixelSize"
                        }
                    },
                    # Задать ширину столбцов C D и E : 150 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "dimension": "COLUMNS",
                                "startIndex": 2,
                                "endIndex": 5
                            },
                            "properties": {
                                "pixelSize": 150
                            },
                            "fields": "pixelSize"
                        }
                    },

                    # Задать ширину столбца F: 200 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "dimension": "COLUMNS",
                                "startIndex": 5,
                                "endIndex": 6,

                            },
                            "properties": {
                                "pixelSize": 200
                            },
                            "fields": "pixelSize"
                        }
                    },
                    # Задать ширину столбца G: 200 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "dimension": "COLUMNS",
                                "startIndex": 6,
                                "endIndex": 7
                            },
                            "properties": {
                                "pixelSize": 600
                            },
                            "fields": "pixelSize"
                        }
                    },
                    # делаем список в листе категории
                    {
                        "setDataValidation": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 5,
                                "endColumnIndex": 6
                            },
                            "rule": {
                                "condition": {
                                    "type": 'ONE_OF_LIST',
                                    "values": [
                                        {
                                            "userEnteredValue": 'Неразобранное',
                                        },

                                    ],
                                },
                                "showCustomUi": True,
                                "strict": True
                            }

                        }

                    }
                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Расход размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_rashod,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,
                            },

                            "fields": "pixelSize"

                        },

                    }

                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Доход размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_dohod,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,

                            },

                            "fields": "pixelSize"

                        },

                    },

                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица Долг размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_dolg,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,
                            },

                            "fields": "pixelSize"

                        },

                    }

                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица бюджет размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_budjet,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,
                            },

                            "fields": "pixelSize"

                        },

                    }

                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица источники размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_istochniki,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,
                            },

                            "fields": "pixelSize"

                        },

                    }

                ]
            }).execute()

            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [
                    # Таблица категории размер высота.
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId_kategorii,
                                "dimension": "ROWS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {
                                "pixelSize": 50,
                            },

                            "fields": "pixelSize"

                        },

                    },

                ],

            }).execute()


            await bot.send_message(message.from_user.id, 'ШАГ 2/3.Введите город в котором вы проживаете')
            break
        else:
            # если почта не прошла проверку, то бот отправляет тебя обратно к вводу пользователя
            await bot.send_message(message.from_user.id,
                                   f'Шаг 1/3.Укажите электронную почту(только @gmail.com).К\n'
                                   f'ящику будет привязана google-таблица с Вашими финансами')
            break


# регистрация пользователя этап второй
@dp.message_handler(state=registration.waiting_for_sity, content_types=types.ContentTypes.TEXT)
async def email(message: types.Message, state: FSMContext):
    # сохраняю город
    await state.update_data(sity=message.text)
    user_data = await state.get_data()
    print({user_data['sity']})
    print('User spreedsheet id is: ' + str({user_data['spreedsheetidofuser']}))
    global sity
    sity = f"{user_data['sity']}"
    spreadsheetidofuser_format = f"{user_data['spreedsheetidofuser']}"
    print(sity)
    await registration.next()
    add_new_user_to_base(user_id=message.from_user.id, spreedsheetid=spreadsheetidofuser_format, town=sity)
    await bot.send_message(message.from_user.id, f'ШАГ 3/3. Укажите лимит ежемесячных расходов.')


# регистрация пользователя этап третий (ввод бюджета)
@dp.message_handler(state=registration.waiting_for_budjet, content_types=types.ContentTypes.TEXT)
async def email(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        # сохраняю бюджет который вводит пользователь
        await state.update_data(budjet=message.text)
        user_data = await state.get_data()
        budjet = f"{user_data['budjet']}    "
        spreadsheetId_of_user = f"{user_data['spreedsheetidofuser']}"
        print(spreadsheetId_of_user)
        # print({user_data['budjet']})
        print(budjet)

        await bot.send_message(message.from_user.id, f'Поздравляем! Вы успешно зарегестрированны в Penny.')
        await bot.send_message(message.from_user.id, f'Теперь вы можете отправлять доходы и расходы нашему'
                                                     f' боту.Cправка по работе с ботом - /help. Все записи заносятся в'
                                                     f' google-таблицу (подробная справка внутри таблицы). Ссылка на таблицу - /table')
        await bot.send_message(message.from_user.id, 'Примеры сообщений для бота - команда /samples.')

        # Записываем сразу в таблицу месячный бюджет пользователя
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId_of_user, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": "Бюджеты!A1:G20",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     # заполняем строки
                     ["ID", "Вкл", "Основной", "Наименование", "Лимит", "Период", "Синонимы"],
                     ["", "1", "1", "Ежемесячные расходы", budjet, "Месяц", ""],
                     ["", "1", "0", "Годовые расходы", "", "Год", "годовые, годовой, год"],
                     ["", "1", "0", "Внебюджет", "", "Год", "вне"]
                 ]}
            ]
        }).execute()

        await registration.next()
        return


# команда balance
@dp.message_handler(state="*", content_types=types.ContentTypes.TEXT, commands="balance")
async def delete_account(message: types.Message, state: FSMContext):
    if get_have_user_in_a_base(user_id=message.from_user.id) == 0:
        await bot.send_message(message.from_user.id,
                               "Вы ещё не зарегистрированы, сделайте это с помощью команды /start")
    else:
        spreadsheetId = get_spreedsheetid_by_user_id(user_id=message.from_user.id)
        # Вытягиваем бюджет пользователя
        ranges = ["Бюджеты!B2:G31"]

        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        print(str(sheet_values))
        budjet_of_user = int(sheet_values[0][3])
        print(str(budjet_of_user))

        # Считаем сколько потрачено за месяц
        # Вытягиваем все расходы за месяц пользователя

        # Суммируем все расходы за месяц пользователя

        # Считаем сколько он может потратить сегодня
        # Пример: сегодня можно потратить: 2000

        # Считаем сколько потрачено из месячного бюджета
        # Пример: потрачено 15000 из 5000

        # Считаем сколько у него осталось денег на месяц из своего бюджета
        # Пример: остаток 5 000

        # Выводим это всё в сообщение пользователю


# команда cancel
@dp.message_handler(state="*", content_types=types.ContentTypes.TEXT, commands="cancel")
async def delete_last_message_in_bot(message: types.Message, state: FSMContext):
    if get_have_user_in_a_base(user_id=message.from_user.id) == 0:
        await bot.send_message(message.from_user.id,
                               "Вы ещё не зарегистрированы, сделайте это с помощью команды /start")
    else:
        last_message_id_of_user = get_id_of_last_message_of_user_id(user_id=message.from_user.id)
        spreadsheetId = get_spreedsheetid_by_user_id(user_id=message.from_user.id)
        # Вытягиваем ячейки из доходов
        ranges = ["Доходы!A1:A1000"]

        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        print(str(sheet_values))

        # Ищем есть ли нужный айди в доходах
        for element in sheet_values:
            print("Element / last message " + str(element[0]) + " last message - " + str(last_message_id_of_user))
            if str(element[0]) == str(last_message_id_of_user):
                print("Last zapis in dohodi")

                # Если есть, то вытягиваем её и удаляем из таблицы
                tablelist = "Доходы!A" + str(
                    get_last_message_of_user_id_in_dohod(user_id=message.from_user.id)) + ":F" + str(
                    get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                print(str(tablelist))

                batch_clear_values_request_body = {
                    'ranges': tablelist,
                }
                request = service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetId,
                                                                     body=batch_clear_values_request_body)
                response = request.execute()

        # Вытягиваем ячейки из расходов
        ranges = ["Расходы!A1:A1000"]

        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        print(str(sheet_values))

        # Ищем есть ли нужный айди в расходах
        for element in sheet_values:
            print("Element / last message " + str(element[0]) + " last message - " + str(last_message_id_of_user))
            if str(element[0]) == str(last_message_id_of_user):
                print("Last zapis in rashodi")

                # Если есть, то вытягиваем её и удаляем из таблицы
                tablelist = "Расходы!A" + str(
                    get_last_message_of_user_id_in_rashod(user_id=message.from_user.id)) + ":G" + str(
                    get_last_message_of_user_id_in_rashod(user_id=message.from_user.id))
                print(str(tablelist))
                batch_clear_values_request_body = {
                    'ranges': tablelist,
                }
                request = service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetId,
                                                                     body=batch_clear_values_request_body)
                response = request.execute()

        # Вытягиваем ячейки из долгов
        ranges = ["Долги!A1:A1000"]

        results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                           ranges=ranges,
                                                           valueRenderOption='FORMATTED_VALUE',
                                                           dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        print(str(sheet_values))

        # Ищем есть ли нужный айди в долгах
        for element in sheet_values:
            print("Element / last message " + str(element[0]) + " last message - " + str(last_message_id_of_user))
            if str(element[0]) == str(last_message_id_of_user):
                print("Last zapis in dolgi")

                # Если есть, то вытягиваем её и удаляем из таблицы
                tablelist = "Долги!A" + str(
                    get_last_message_of_user_id_in_dolg(user_id=message.from_user.id)) + ":F" + str(
                    get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                print(str(tablelist))
                batch_clear_values_request_body = {
                    'ranges': tablelist,
                }
                request = service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetId,
                                                                     body=batch_clear_values_request_body)
                response = request.execute()

        # Убираем её из базы данных
        delete_last_message(user_id=message.from_user.id)

        # Если успешно всё убрали - вывели сообщение о том, что мы убрали данную запись
        await bot.send_message(message.from_user.id, "Последняя запись удалена.")


# команда delete
@dp.message_handler(state="*", content_types=types.ContentTypes.TEXT, commands="delete")
async def delete_account(message: types.Message, state: FSMContext):
    if get_have_user_in_a_base(user_id=message.from_user.id) == 0:
        await bot.send_message(message.from_user.id,
                               "Вы ещё не зарегистрированы, сделайте это с помощью команды /start")
    else:
        await bot.send_message(message.from_user.id, f'Вы действительно хотите удалить свой аккаунт?\n'
                                                     f'Файл на Гугл Диске сохранится:', reply_markup=greet_delete)
        await registration.waiting_for_answer_of_delete.set()

    # нажатие на кнопку Да


@dp.message_handler(state=registration.waiting_for_answer_of_delete, content_types=types.ContentTypes.TEXT)
async def delete_yes(message: types.Message, state: FSMContext):
    if message.text == "Да":
        delete_user(user_id=message.from_user.id)
        await state.finish()
        await bot.send_message(message.from_user.id, "Аккаунт был успешно удалён!")

    elif message.text == "Нет":
        await bot.send_message(message.from_user.id, f'Вы отменили удаление аккаунта.')
        await registration.waiting_for_new_data.set()
    else:
        await bot.send_message(message.from_user.id, f'Выберите один из вариантов в меню:', reply_markup=greet_delete)


# Обработчик любых текстовых сообщений
@dp.message_handler(state="*", content_types=types.ContentTypes.TEXT)
async def getDataStep(message: types.Message, state: FSMContext):
    if get_have_user_in_a_base(user_id=message.from_user.id) == 0:
        await bot.send_message(message.from_user.id,
                               "Вы ещё не зарегистрированы, сделайте это с помощью команды /start")
    else:
        await registration.waiting_for_new_data.set()
        spreadsheetId = get_spreedsheetid_by_user_id(user_id=message.from_user.id)
        if message.text == "/table":
            await bot.send_message(message.from_user.id, "Ваша ссылка: ")
            link = 'https://docs.google.com/spreadsheets/d/' + spreadsheetId
            await bot.send_message(message.from_user.id, link)
        elif message.text == "/help":
            await bot.send_message(message.from_user.id, f'Cправка\n\n'
                                                         f'/balance — Мой баланс\n'
                                                         f'/table — Cсылка на google-таблицу\n'
                                                         f'/settings — Настройки\n'
                                                         f'/help — Справка\n'
                                                         f'/delete — Удаление аккаунта\n\n'
                                                         f'Выберите интересующий раздел справки и получите краткую '
                                                         f'помощь. Если ваш вопрос не решен, то обратитесь за помощью'
                                                         f'к живому оператору https://t.me/finance_helpers',
                                   reply_markup=greet_kb)
        elif message.text == "1.Баланс":
            await bot.send_message(message.from_user.id, f"Баланс\n\n"
                                                         f'Баланс — это маскимальная сумма расходов на сегодня.\n\n'
                                                         f'Баланс положительный - спокойно тратьте указанную сумму,\n'
                                                         f'отрицательный — отложите расходы, иначе не уложитесь в\n'
                                                         f'бюджет.\n\n'
                                                         f'По умолчанию бот присылает баланс Ежемесячных расходов.\n'
                                                         f'Добавьте к слову "баланс" название или синоним другого\n'
                                                         f'бюджета,чтобы проверить его баланс.Например,"баланс\n'
                                                         f'годовой".')
        elif message.text == "2.Отчеты":
            await bot.send_message(message.from_user.id, f'Отчеты\n\n'
                                                         f'Внутри бота доступен только отчет по балансу — команда\n'
                                                         f'/balance.\n\n'
                                                         f'Статистику по месяцам,категориям расходов, а также\n'
                                                         f'графические отчеты доступны в google-таблице — команда\n'
                                                         f'/table')
        elif message.text == "3.Расходы":
            await bot.send_message(message.from_user.id, f'Расходы\n\n'
                                                         f'Отправляйте боту простые сообщения о Ваших расходах —\n'
                                                         f'"продукты 877".\n\n'
                                                         f'В сообщении обязательно укажите категорию и потраченную\n'
                                                         f'сумму,дополнительно можно указать дату,бюджет \n'
                                                         f'и источник расходов.\n\n'
                                                         f'Бот распознает данные  добавит их в google-таблицу.\n'
                                                         f'Позже Вы сможете изменить или удалить их из таблицы.\n\n'
                                                         f'Изучите примеры сообщений, чтобы понять как общаться\n'
                                                         f'с ботом — команда /samples.')
        elif message.text == "4.Доходы":
            await bot.send_message(message.from_user.id, f'Доходы\n\n'
                                                         f'Отправляйте боту простые сообщения о Ваших доходах —\n'
                                                         f'"доход 15000 аренда" или "зарплата 35000".\n\n'
                                                         f'Создайте отдельные категории только для доходов,указав в\n'
                                                         f'google-таблице принадлежность категории только к доходам.\n\n'
                                                         f'В сообщени обязятельно укажите категорию и полученную\n'
                                                         f'сумму,дополнительно можно указать дату и источник,в\n'
                                                         f'который поступил доход.\n\n'
                                                         f'Бот распознает данные и добавит их в google-таблицу.\n'
                                                         f'Позже Вы сможете изменить или удалить их из таблицы.\n\n'
                                                         f'Изучите примеры сообщенией, чтобы понять как общаться с\n'
                                                         f'ботом — команда /samples.')
        elif message.text == "5.Бюджеты":
            await bot.send_message(message.from_user.id, f'Бюджеты\n\n'
                                                         f'Бюджеты разделяют ваши Расходы чтобы их проще было\n'
                                                         f'контролировать.\n\n'
                                                         f'Бюджет обязательно привязан к периоду:неделя,месяц или\n'
                                                         f'год — и имеет лимит — максимальная сумма затрат за период.\n\n'
                                                         f'Создавайте любое количество бюджетов.Разделите\n'
                                                         f'ежемесячные и годовые расходы.Добавьте и контролируйте\n'
                                                         f'отдельный бюджет для каждой поездки в отпуск.\n\n'
                                                         f'У каждого бюджета есть синонимы.Они позволяют упрощать\n'
                                                         f'сообщения для бота.Например у бюджета "Годовые расходы"\n'
                                                         f'есть синоним "год".Изменять синонимы можно\n'
                                                         f'самостоятельно,для этого перейдите \n'
                                                         f'в google-таблицу /table.\n\n')
        elif message.text == "6.Источники":
            await bot.send_message(message.from_user.id, f'Источники\n\n'
                                                         f'Источники — это наличные, кредитные и дебитовые карты и т.п.\n\n'
                                                         f'Разделяйте расходы и доходы по источникам, если это важно\n'
                                                         f'для Вас.\n'
                                                         f'У каждого источника есть синонимы.Они позволяют упрощать\n'
                                                         f'сообщения для бота.Например у источника "Банковская\n'
                                                         f'карта" может быть "сбер" или "альфа".Изменять синонимы\n'
                                                         f'можно самостоятельно,для этого перейдите в google-таблицу\n'
                                                         f'/table.\n\n')
        elif message.text == "7.Категории":
            await bot.send_message(message.from_user.id, f'Категории\n\n'
                                                         f'Категории — основные типы расходов для удобства их\n'
                                                         f'подсчета и анализа:квартира, продукты и автомобиль и т.д.\n'
                                                         f'Для доходов и долгов есть свои категории\n\n'
                                                         f'Создавайте любое корличество категорий.\n\n'
                                                         f'У каждой категории есть синонимы.Они позволяют упрощать\n'
                                                         f'сообщения для бота.Например,у категории "Автомобиль"\n'
                                                         f'могут быть синонимы "авто,машина,стоянка,гараж,осаго,\n'
                                                         f'бензин,бенз".Любое сообщение с этими словами будет\n'
                                                         f'добавлено в "Автомобиль".\n\n'
                                                         f'Изменять синонимы можно самостоятельно, для этого\n')
        elif message.text == "8.Google-таблица":
            await bot.send_message(message.from_user.id, f'Google-таблица\n\n'
                                                         f'Таблица в Google позволяет увидеть наглядные отчеты или\n'
                                                         f'вносить изменения,минуя бота.Смотрите на таблицуне реже 1\n'
                                                         f'раза в неделю,чтобы иметь наглядное представление о \n'
                                                         f'Ваших финансах.\n\n'
                                                         f'Ссылка на таблицу доступна по команде /table\n\n'
                                                         f'Справка и помощь по таблице - https://t.me/finance_helpers\n\n')
        elif message.text == "/samples":
            await bot.send_message(message.from_user.id, f'Примеры сообщений для бота:\n\n'
                                                         f'“продукты 750”\n'
                                                         f'По умолчанию запись вносится на сегодня, в расходы/\n'
                                                         f'доходы/долги, в зависимости от настроек категории в\n'
                                                         f'google-таблице.\n\n'
                                                         f'“вчера продукты 750”\n'
                                                         f'Используйте “вчера” и “позавчера” для изменения даты.\n\n'
                                                         f'“среда продукты 750”\n'
                                                         f'“продукты 750 ср”\n'
                                                         f'Или укажите ближайший прошедший день недели. Можно\n'
                                                         f'написать день недели полностью или 2-буквенное\n'
                                                         f'обозначение.\n\n'
                                                         f'“31 авг автомобиль бензин 1500”\n'
                                                         f'Можете указать конкретное число. Месяц пишите полностью,\n'
                                                         f'первые 3 буквы, или цифрами после точки.\n\n'
                                                         f'“бенз 1500”\n'
                                                         f'Используйте синонимы для категорий, бюджетов и\n'
                                                         f'источников. Запись всё равно будет внесена в категорию\n'
                                                         f'Автомобиль.\n\n'
                                                         f'“одежда 3200+1900”\n'
                                                         f'Используйте простые формулы (“+” и “-”), если надо \n'
                                                         f'объединить суммы.\n\n'
                                                         f'“зарплата 35000”\n'
                                                         f'Для доходов работают те же правила.\n\n'
                                                         f'“25.08 дал в долг сестре 15000”\n'
                                                         f'И для долгов тоже.')
        elif message.text == "/settings":
            await bot.send_message(message.from_user.id, f'Выберите настройки, которые хотите поменять:',
                                   reply_markup=greet_settings)
        elif message.text == "1. Город":
            await bot.send_message(message.from_user.id, f'Текущий город:"{sity}". Укажите новый город:')
        elif message.text == "2. Время напоминания":
            await bot.send_message(message.from_user.id, f'Укажите час, в котором присылать уведомления:',
                                   reply_markup=greet_time)

        else:
            # Вытягиваем синонимы из таблицы
            ranges = ["Категории!B2:G31"]

            results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                               ranges=ranges,
                                                               valueRenderOption='FORMATTED_VALUE',
                                                               dateTimeRenderOption='FORMATTED_STRING').execute()
            sheet_values = results['valueRanges'][0]['values']

            print(str(sheet_values))

            dohod_sinonims = ''
            rashod_sinonims = ''
            v_dolg_sinonims = ''
            dict_of_categories_dohod = {'Доход': 'доход'}
            dict_of_categories_rashod = {'Расход': 'расход'}
            dict_of_categories_dolg = {'Долг': 'долг'}

            # Пишем выборку, что добавить в сортировку синонимов
            for element in sheet_values:
                # Проверяем включена ли категория у элемента в таблице
                # print(str(element))
                if element[0] == "1":
                    # Делаем выбор, куда заносить синонимы
                    # Если это доход
                    if element[2] == "1":
                        if len(element) == 6:
                            dohod_sinonims = dohod_sinonims + ", " + element[5]
                            dict_of_categories_dohod[str(element[4])] = str(element[5])
                        continue
                    elif element[1] == "1":
                        if len(element) == 6:
                            rashod_sinonims = rashod_sinonims + ", " + element[5]
                            dict_of_categories_rashod[str(element[4])] = str(element[5])
                        continue
                    elif element[3] == "1":
                        if len(element) == 6:
                            v_dolg_sinonims = v_dolg_sinonims + ", " + element[5]
                            dict_of_categories_dolg[str(element[4])] = str(element[5])
                        continue
                    else:
                        pass

            print('Dict of dohod: ' + str(dict_of_categories_dohod))

            # Отмечаем дефолтные слова, которых обрабатывает бот
            kratko_dni_sinonims = 'пн, вт, ср, чт, пт, сб, вс'
            kratko_month_sinonims = 'сен, окт, дек, нояб, фев, март, апр, май, июнь, июль, авг, янв'

            # Получаемое сообщение на разбор.
            find_word = message.text.lower()

            # Выводим значения
            date_global_full = ''
            category_global = ''
            kuda_global = ''
            prim_global = ''
            summa_global = 0
            mesyac_global = ''
            den_global = ''
            nulls_adding = 0

            # Разбираем искомую фразы через пробел на слова.
            find_word_fraze = find_word.split(' ')
            print('Разобранная фраза на слова: ' + str(find_word_fraze))

            # Делим строку синонимов, чтобы проверить это в доход, в расход, в долг или не в разобранное.
            sort_dohod_sinonims = dohod_sinonims.split(', ')
            print(str(sort_dohod_sinonims))

            sort_rashod_sinonims = rashod_sinonims.split(', ')
            print(str(sort_rashod_sinonims))

            sort_v_dolg_sinonims = v_dolg_sinonims.split(', ')
            print(str(sort_v_dolg_sinonims))

            sort_dni_sinonims = kratko_dni_sinonims.split(', ')

            sort_month_sinonims = kratko_month_sinonims.split(', ')

            # Начинаем проверять каждое слово в листе через проверки на схожесть ключевых слов.
            for element in range(0, len(find_word_fraze)):
                print(str(find_word_fraze[element]))

                # Проверяем, если число от 1 до 31, ищем месяц и записываем в дату
                if find_word_fraze[element].isalpha() == False:
                    if int(find_word_fraze[element]) > 0 and int(find_word_fraze[element]) < 32:
                        if sort_month_sinonims.count(find_word_fraze[element + 1]) > 0:
                            date = find_word_fraze[element] + '.' + find_word_fraze[element + 1]
                            print('Eto data: ' + date)
                            date_global_full = str(date)
                            den_global = str(find_word_fraze[element])
                            continue

                # Проверяем ключевое слово на месяца, чтобы записывать дату месяца ( потом должен быть поиск дня этого месяца, ПЕРЕД месяцом?)
                if sort_month_sinonims.count(find_word_fraze[element]) > 0:
                    print('Eto mesyac: ' + str(find_word_fraze[element]))
                    mesyac_global = str(find_word_fraze[element])
                    continue

                # Проверяем есть ли у нас запись "000"
                if find_word_fraze[element] == "000":
                    nulls_adding = 1
                    continue

                # Проверяем число ли данный элемент, чтобы вытянуть сумму.
                if find_word_fraze[element].isalpha() == False:
                    print('Eto chisla')
                    # Проверяем, если в этом числах точка и размер из 5 символов в элементе
                    if find_word_fraze[element].count('.') and len(find_word_fraze[element]) == 5:
                        print('Eto den i mesyac')
                        date_global_full = find_word_fraze[element]
                    else:
                        summa_global = find_word_fraze[element]
                    continue

                # Проверяем ключевое ли слово дней это.
                if sort_dni_sinonims.count(find_word_fraze[element]) > 0:
                    print('Eto den: ' + str(find_word_fraze[element]))
                    den_global = find_word_fraze[element]
                    continue

                # Проверяем ключевое слово вчера, чтобы записывать сразу дату с функционал этого ключевого слова.
                if find_word_fraze[element] == 'вчера':
                    yesterday = datetime.now() - timedelta(1)
                    date_global_full = yesterday.strftime("%d.%m")
                    print('Eto bilo vchera!')
                    continue

                # Проверяем ключевое слово позавчера, чтобы записывать сразу дату с функционал этого ключевого слова.
                if find_word_fraze[element] == 'позавчера':
                    afteryesterday = datetime.now() - timedelta(2)
                    date_global_full = afteryesterday.strftime("%d.%m")
                    print('Eto bilo pozavchera!')
                    continue

                # Проверяем ключевое слово "доход"
                if find_word_fraze[element] == 'доход' or find_word_fraze[element] == 'Доход':
                    kuda_global = 'Dohod'
                    category_global = 'Неразобранное'
                    continue

                # Проверяем ключевое слово "расход"
                if find_word_fraze[element] == 'расход' or find_word_fraze[element] == 'Расход':
                    kuda_global = 'Rashod'
                    category_global = 'Неразобранное'
                    continue

                # Проверяем есть ли такой синоним ( одно слово ) в доходах, расходах, долгах.
                if sort_dohod_sinonims.count(find_word_fraze[element]) > 0:
                    print('Eto dohod!')
                    kuda_global = 'Dohod'
                    for key, value in dict_of_categories_dohod.items():
                        if value.count(find_word_fraze[element]) > 0:
                            category_global = str(key)

                    continue

                elif sort_rashod_sinonims.count(find_word_fraze[element]) > 0:
                    print('Eto rashod')
                    kuda_global = 'Rashod'
                    for key, value in dict_of_categories_rashod.items():
                        if value.count(find_word_fraze[element]) > 0:
                            category_global = str(key)

                    continue

                elif sort_v_dolg_sinonims.count(find_word_fraze[element]) > 0:
                    print('Eto v dolg')
                    kuda_global = 'Dolg'
                    for key, value in dict_of_categories_dolg.items():
                        if value.count(find_word_fraze[element]) > 0:
                            category_global = str(key)

                    continue
                else:
                    print('Ne razobral edinichn slovo(')
                    # Проверяем есть ли в строке ключевое слово длиной больше одного - доходы
                    for sinonim in range(0, len(sort_dohod_sinonims)):
                        if find_word.count(sort_dohod_sinonims[sinonim]):
                            if sort_dohod_sinonims[sinonim] != "":
                                print('Eto svyaska dohodov')
                                kuda_global = 'Dohod_svyazka'
                                break

                    # Проверяем есть ли в строке ключевое слово длиной больше одного - расходы
                    for sinonim2 in range(0, len(sort_rashod_sinonims)):
                        if find_word.count(sort_rashod_sinonims[sinonim2]):
                            if sort_rashod_sinonims[sinonim2] != "":
                                print('Eto svyaska rashodov')
                                kuda_global = 'Rashod_svyazka'
                                break

                    # Проверяем есть ли в строке ключевое слово длиной больше одного - долг
                    for sinonim3 in range(0, len(sort_v_dolg_sinonims)):
                        if find_word.count(sort_v_dolg_sinonims[sinonim3]):
                            if sort_v_dolg_sinonims[sinonim3] != "":
                                print('Eto svyaska kategorii dolg')
                                kuda_global = 'Dolg_svyazka'
                                break
                            else:
                                print('Ne poluchilos razobrat: ' + find_word)
                                kuda_global = 'Nerazobrano'

            if not category_global:
                category_global = "Неразобранное"

            if not date_global_full:
                print(date_global_full)
                now = datetime.now()
                date_global_full = now.strftime("%d.%m")
            else:
                pass

            prim_global = message.text

            # Delete summ from prim_global
            if not summa_global:
                pass
            else:
                print("will replace this")
                prim_global = prim_global.replace(str(summa_global), '')

            print("summa_global - " + (str(summa_global)) + " / prim_global - " + str(prim_global))

            # Процесс обработки сообщения прошёл
            # Происходит полная запись в бд
            if kuda_global == "Dohod":
                # Отправляем сообщение ботом
                await bot.send_message(message.from_user.id, "Записано в Ежемесячные доходы → " + category_global)

                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="2", last_ind_rashod="1",
                                                     last_ind_dolg="1")
                    print("ONLY NEW MESSAGE")
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    # Добавляем запись в таблицу доходы
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Доходы!A2:F2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Наличные", category_global,
                                  str(summa_global), prim_global],
                             ]}
                        ]
                    }).execute()
                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id)) + 1
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id))
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    tablelist = "Доходы!A" + str(index_to_add_dohod) + ":F" + str(index_to_add_dohod)
                    print(str(tablelist))
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Наличные", category_global,
                                  str(summa_global), prim_global],
                             ]}
                        ]
                    }).execute()

            elif kuda_global == "Rashod":
                await bot.send_message(message.from_user.id, "Записано в Ежемесячные расходы → " + category_global)

                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="1", last_ind_rashod="2",
                                                     last_ind_dolg="1")

                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    # Добавляем запись в таблицу расходы
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Расходы!A2:G2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()

                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id)) + 1
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    tablelist = "Расходы!A" + str(index_to_add_rashod) + ":G" + str(index_to_add_rashod)
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()


            elif kuda_global == "Dolg":
                await bot.send_message(message.from_user.id, "Записано в раздел 'Долги' → " + category_global)
                if nulls_adding == 1:
                    summa_global = str(summa_global) + " 000"
                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="1", last_ind_rashod="1",
                                                     last_ind_dolg="2")

                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))

                    # Добавляем запись в таблицу долги
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Долги!A2:F2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, category_global, str(summa_global),
                                  prim_global, "", ],
                             ]}
                        ]
                    }).execute()
                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id))
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id)) + 1
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    tablelist = "Долги!A" + str(index_to_add_dolg) + ":F" + str(index_to_add_dolg)
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, category_global, str(summa_global),
                                  prim_global, "", ],
                             ]}
                        ]
                    }).execute()



            elif kuda_global == "Rashod_svyazka":
                await bot.send_message(message.from_user.id, "Записано в Ежемесячные расходы")
                if nulls_adding == 1:
                    summa_global = str(summa_global) + " 000"
                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="1", last_ind_rashod="2",
                                                     last_ind_dolg="1")

                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    # Добавляем запись в таблицу расходы
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Расходы!A2:F2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()

                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id)) + 1
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    tablelist = "Расходы!A" + str(index_to_add_rashod) + ":F" + str(index_to_add_rashod)
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()

            elif kuda_global == "Dolg_svyazka":
                await bot.send_message(message.from_user.id, 'Записано в раздел "Долги"')
                if nulls_adding == 1:
                    summa_global = str(summa_global) + " 000"
                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="1", last_ind_rashod="1",
                                                     last_ind_dolg="2")

                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    # Добавляем запись в таблицу долги
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Долги!A2:F2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, category_global, str(summa_global),
                                  prim_global, "", ],
                             ]}
                        ]
                    }).execute()
                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id))
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id)) + 1
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    tablelist = "Долги!A" + str(index_to_add_dolg) + ":F" + str(index_to_add_dolg)
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, category_global, str(summa_global),
                                  prim_global, "", ],
                             ]}
                        ]
                    }).execute()
            elif kuda_global == "Dohod_svyazka":
                await bot.send_message(message.from_user.id, "Записано в Ежемесячные доходы")
                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="2", last_ind_rashod="1",
                                                     last_ind_dolg="1")
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    # Добавляем запись в таблицу доходы
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Доходы!A2:F2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Наличные", category_global,
                                  str(summa_global), prim_global],
                             ]}
                        ]
                    }).execute()
                else:
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id)) + 1
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id))
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    tablelist = "Доходы!A" + str(index_to_add_dohod) + ":F" + str(index_to_add_dohod)
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Наличные", category_global,
                                  str(summa_global), prim_global],
                             ]}
                        ]
                    }).execute()
            elif kuda_global == 'Nerazobrano':
                # Добавляем запись в базу данных
                if get_have_user_any_message(user_id=message.from_user.id) == 0:
                    print("PERVIY RAZ VVODIT")
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod="1", last_ind_rashod="2",
                                                     last_ind_dolg="1")
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id))
                    # Добавляем запись в таблицу расходы
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": "Расходы!A2:G2",
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()

                else:
                    index_to_add_dohod = int(get_last_message_of_user_id_in_dohod(user_id=message.from_user.id))
                    index_to_add_rashod = int(get_last_message_of_user_id_in_rashod(user_id=message.from_user.id)) + 1
                    index_to_add_dolg = int(get_last_message_of_user_id_in_dolg(user_id=message.from_user.id))
                    new_id_to_message = int(get_id_of_last_message_of_user_id(user_id=message.from_user.id)) + 1
                    add_new_message_in_base_in_dohod(user_id=message.from_user.id, spreedsheetid=spreadsheetId,
                                                     last_message=message.text, last_ind_dohod=str(index_to_add_dohod),
                                                     last_ind_dolg=str(index_to_add_dolg),
                                                     last_ind_rashod=str(index_to_add_rashod))
                    # Добавляем запись в таблицу доходы
                    tablelist = "Расходы!A" + str(index_to_add_rashod) + ":G" + str(index_to_add_rashod)
                    print(tablelist)
                    if nulls_adding == 1:
                        summa_global = str(summa_global) + " 000"
                    print(str(tablelist))
                    results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                        "valueInputOption": "USER_ENTERED",
                        # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                        "data": [
                            {"range": tablelist,
                             "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                             "values": [
                                 # заполняем строки
                                 [str(new_id_to_message), date_global_full, "Ежемесячный", "Наличные",
                                  str(category_global), str(summa_global), str(prim_global)],
                             ]}
                        ]
                    }).execute()
                await bot.send_message(message.from_user.id, "Записано в Ежемесячные расходы → Неразобранное")

               
# нажатие на кнопку Время напоминания
# @dp.message_handler(Text(equals=["2. Время напоминания"]))
# async def btn_balance(message: types.Message):
# await bot.send_message(message.from_user.id,f'Укажите час, в котором присылать уведомления:',reply_markup=greet_time)
# @dp.message_handler(Text(equals=["00"]))
# async def btn_google_table(message: types.Message):
# pass
# await bot.send_message(message.from_user.id,f'Укажите минуты для уведомлений:',reply_markup=greet_minuts)
# pass


# запуск телеграм бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)