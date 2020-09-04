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



#регистрация пользователя этап первый
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

            spreadsheet = service.spreadsheets().create(body={
                'properties': {'title': 'Greenz Мои финансы', 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': 'Сводка',
                                           'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
            }).execute()
            spreadsheetId = spreadsheet['spreadsheetId']  # сохраняем идентификатор файла
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
                }).execute()
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
            # Получаем список листов, их Id и название
            spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
            sheetList = spreadsheet.get('sheets')
            for sheet in sheetList:
                print(sheet['properties']['sheetId'], sheet['properties']['title'])

            sheetId = sheetList[0]['properties']['sheetId']

            print('Мы будем использовать лист с Id = ', sheetId)
            {"range":
                {
                    "sheetId": sheetId,  # ID листа
                    "startRowIndex": 1,  # Со строки номер startRowIndex
                    "endRowIndex": 5,  # по endRowIndex - 1 (endRowIndex не входит!)
                    "startColumnIndex": 0,  # Со столбца номер startColumnIndex
                    "endColumnIndex": 1  # по endColumnIndex - 1
                }}
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Сводка!B2:D5",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         ["Ячейка B2", "Ячейка C2", "Ячейка D2"],  # Заполняем первую строку
                     ]}
                ]
            }).execute()
            results = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body={
                "requests": [

                    # Задать ширину столбца A: 20 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId,
                                "dimension": "COLUMNS",  # Задаем ширину колонки
                                "startIndex": 0,  # Нумерация начинается с нуля
                                "endIndex": 1  # Со столбца номер startIndex по endIndex - 1 (endIndex не входит!)
                            },
                            "properties": {
                                "pixelSize": 20  # Ширина в пикселях
                            },
                            "fields": "pixelSize"  # Указываем, что нужно использовать параметр pixelSize
                        }
                    },

                    # Задать ширину столбцов B и C: 150 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId,
                                "dimension": "COLUMNS",
                                "startIndex": 1,
                                "endIndex": 3
                            },
                            "properties": {
                                "pixelSize": 150
                            },
                            "fields": "pixelSize"
                        }
                    },

                    # Задать ширину столбца D: 200 пикселей
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheetId,
                                "dimension": "COLUMNS",
                                "startIndex": 3,
                                "endIndex": 4
                            },
                            "properties": {
                                "pixelSize": 200
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }).execute()
            # Рисуем рамку
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body={
                    "requests": [
                        {'updateBorders': {'range': {'sheetId': sheetId,
                                                     'startRowIndex': 1,
                                                     'endRowIndex': 3,
                                                     'startColumnIndex': 1,
                                                     'endColumnIndex': 4},
                                           'bottom': {
                                               # Задаем стиль для верхней границы
                                               'style': 'SOLID',  # Сплошная линия
                                               'width': 1,  # Шириной 1 пиксель
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},  # Черный цвет
                                           'top': {
                                               # Задаем стиль для нижней границы
                                               'style': 'SOLID',
                                               'width': 1,
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
                                           'left': {  # Задаем стиль для левой границы
                                               'style': 'SOLID',
                                               'width': 1,
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
                                           'right': {
                                               # Задаем стиль для правой границы
                                               'style': 'SOLID',
                                               'width': 1,
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
                                           'innerHorizontal': {
                                               # Задаем стиль для внутренних горизонтальных линий
                                               'style': 'SOLID',
                                               'width': 1,
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}},
                                           'innerVertical': {
                                               # Задаем стиль для внутренних вертикальных линий
                                               'style': 'SOLID',
                                               'width': 1,
                                               'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}}

                                           }}
                    ]
                }).execute()
            # Объединяем ячейки A2:D1
            results = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheetId,
                body={
                    "requests": [
                        {'mergeCells': {'range': {'sheetId': sheetId,
                                                  'startRowIndex': 0,
                                                  'endRowIndex': 1,
                                                  'startColumnIndex': 1,
                                                  'endColumnIndex': 4},
                                        'mergeType': 'MERGE_ALL'}}
                    ]
                }).execute()
            # Добавляем заголовок таблицы
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Сводка!B1",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [["Заголовок таблицы"]
                                ]}
                ]
            }).execute()
            # Установка формата ячеек
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
                                                                "fontSize": 14
                                                            }
                                                    }
                                            },
                                        "range":
                                            {
                                                "sheetId": sheetId,
                                                "startRowIndex": 1,
                                                "endRowIndex": 2,
                                                "startColumnIndex": 1,
                                                "endColumnIndex": 4
                                            },
                                        "fields": "userEnteredFormat"
                                    }
                            }
                        ]
                }).execute()
            ranges = ["Сводка!C2:C2"]  #

            results = service.spreadsheets().get(spreadsheetId=spreadsheetId,
                                                 ranges=ranges, includeGridData=True).execute()

            results = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
                                                               ranges=ranges,
                                                               valueRenderOption='FORMATTED_VALUE',
                                                               dateTimeRenderOption='FORMATTED_STRING').execute()
            sheet_values = results['valueRanges'][0]['values']
            print(sheet_values)
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