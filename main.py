# подключаем все нужные библиотеки
from config import BOT_TOKEN
from aiogram import Bot, Dispatcher, executor, types
import httplib2
from keyboards import greet_kb
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

memory_storage = MemoryStorage()
# подключаем токен бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=memory_storage)

CREDENTIALS_FILE = 'cread.json'  # Имя файла с закрытым ключом, вы должны подставить свое
# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, [
    'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
service = apiclient.discovery.build('sheets', 'v4',
                                    http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
class registration(StatesGroup):
    waiting_for_gmail = State()
    waiting_for_sity = State()
    waiting_for_budjet = State()


# команда start
@dp.message_handler(commands="start", state="*")
async def start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f'{message.from_user.first_name},для работы необходимо зарегестрироваться.\nЭто займет пару минут.\n\n' \
                           + 'Шаг 1/3.Укажите электронную почту(только @gmail.com).К ящику будет привязана google-таблица с Вашими финансами')
    await registration.waiting_for_gmail.set()
# регистрация пользователя этап первый
@dp.message_handler(state=registration.waiting_for_gmail, content_types=types.ContentTypes.TEXT)
async def email(message: types.Message, state: FSMContext):
    # сохраняю адресс пользователя
    await state.update_data(gmail=message.text)
    user_data = await state.get_data()
    gmail = user_data['gmail']
    print({user_data['gmail']})
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
                'properties': {'title': 'Greenz - мои финансы', 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': 'Сводка',
                                           'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
            }).execute()
            await bot.send_message(message.from_user.id,"Создание таблицы....")
            spreadsheetId = spreadsheet['spreadsheetId']  # сохраняем идентификатор файла
            print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)
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
            # Добавление листа Статистика
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
            # Добавление листа Графики
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

            # Добавление листа Расходы
            await bot.send_message(message.from_user.id, "Иннициализация расходов....")
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
                                        "rowCount": 20,
                                        "columnCount": 12
                                    }
                                }
                            }
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
                                        "rowCount": 20,
                                        "columnCount": 12
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
                                        "rowCount": 20,
                                        "columnCount": 12
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
                                        "rowCount": 20,
                                        "columnCount": 12
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


            # Расходы заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Расходы!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки
                         ["ID", "Дата", "Бюджет","Источник","Категория","Сумма","Примечание"],  # Заполняем первую строку
                         [message.from_user.id, "", "","","",""]  # Заполняем вторую строку
                     ]}
                ]
            }).execute()


            # Доходы заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Доходы!A1:F20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки
                         ["ID", "Дата","Источник","Категория","Сумма","Примечание"],  # Заполняем первую строку
                         [message.from_user.id, "", "","","",""]  # Заполняем вторую строку
                     ]}
                ]
            }).execute()


            # Долги заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Долги!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки
                         ["ID", "Дата открытия", "Категория","Сумма","Примечание","Дата закрытия"],  # Заполняем первую строку
                         ["", "", "","","",""]  # Заполняем вторую строку
                     ]}
                ]
            }).execute()


            #Бюджеты заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Бюджеты!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки
                         ["ID", "Вкл", "Основной","Наименование","Лимит","Период", "Синонимы"],  # Заполняем первую строку
                     ]}
                ]
            }).execute()



            #Источники заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Источники!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки
                         ["ID", "Вкл", "Основной","Наименование","Синонимы","Начальное значение"],  # Заполняем первую строку
                         ["", "", "","","",""]  # Заполняем вторую строку
                     ]}
                ]
            }).execute()


            #Категории заполняем ячейки
            results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
                "valueInputOption": "USER_ENTERED",
                # Данные воспринимаются, как вводимые пользователем (считается значение формул)
                "data": [
                    {"range": "Категории!A1:G20",
                     "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                     "values": [
                         #заполняем строки

                         ["ID", "Вкл", "Отображать в расходах","Отображать в доходах","Отображать в долгах","Наименование","Синонимы"],  # Заполняем первую строку
                         ["", "", "","","",""]  # Заполняем вторую строку
                     ]}
                ]
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
    await registration.next()
    await bot.send_message(message.from_user.id, f'ШАГ 3/3. Укажите лимит ежемесячных расходов.')


# регистрация пользователя этап третий (ввод бюджета)
@dp.message_handler(state=registration.waiting_for_budjet, content_types=types.ContentTypes.TEXT)
async def email(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        # сохраняю бюджет который вводит пользователь
        await state.update_data(budjet=message.text)
        user_data = await state.get_data()
        print({user_data['budjet']})
        await bot.send_message(message.from_user.id, f'Поздравляем!Вы успешно зарегестрированны в Greenz.')
        await bot.send_message(message.from_user.id, f'Теперь вы можете отправлять доходы и расходы нашему'
                                                     f' боту.Cправка по работе с ботом - /help.Все записи заносятся в'
                                                     f'google-таблицу(подробная справка внутри таблицы).Ссылка на таблицу - /table')
        await bot.send_message(message.from_user.id, 'Примеры сообщений для бота - команда /samples.')
        await state.finish()
        return


# команда table
@dp.message_handler(commands="table", state="*")
async def table(message: types.Message):
    await bot.send_message(message.from_user.id, "Ваша ссылка: ")
    await bot.send_message(message.from_user.id, link)





# команда help
@dp.message_handler(commands="help", state="*")
async def help_text(message: types.Message):
    await bot.send_message(message.from_user.id, f'Cправка\n\n'
                                                 f'/balance — Мой баланс\n'
                                                 f'/table — Cсылка на google-таблицу\n'
                                                 f'/sync — Синхронизация бота c google-таблицей\n'
                                                 f'/settings — Настройки\n'
                                                 f'/help — Справка\n'
                                                 f'/delete — Удаление аккаунта\n\n'
                                                 f'Выберите интересующий раздел справки и получите краткую'
                                                 f'помощь. Если ваш вопрос не решен, то обратитесь за помощью'
                                                 f'к живому оператору @greenzapp.', reply_markup=greet_kb)
#Нажатие на кнопку баланс(информация по балансу)
@dp.message_handler(Text(equals=["1.Баланс"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f"Баланс\n\n"
                        f'Баланс — это маскимальная сумма расходов на сегодня.\n\n'
                        f'Баланс положительный - спокойно тратьте указанную сумму,\n'
                        f'отрицательный — отложите расходы, иначе не уложитесь в\n'
                        f'бюджет.\n\n'
                        f'По умолчанию бот присылает баланс Ежемесячных расходов.\n'
                        f'Добавьте к слову "баланс" название или синоним другого\n'
                        f'бюджета,чтобы проверить его баланс.Например,"баланс\n'
                        f'годовой".')
#нажатие на кнопку отчет(информация по отчетам)
@dp.message_handler(Text(equals=["2.Отчеты"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Отчеты\n\n'
                        f'Внутри бота доступен только отчет по балансу — команда\n'
                        f'/balance.\n\n'
                        f'Статистику по месяцам,категориям расходов, а также\n'
                        f'графические отчеты доступны в google-таблице — команда\n'
                        f'/table')
#нажатие на кнопку расходы(информация по расходам)
@dp.message_handler(Text(equals=["3.Расходы"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Расходы\n\n'
                        f'Отправляйте боту простые сообщения о Ваших расходах —\n'
                        f'"продукты 877".\n\n'
                        f'В сообщении обязательно укажите категорию и потраченную\n'
                        f'сумму,дополнительно можно указать дату,бюджет \n'
                        f'и источник расходов.\n\n'
                        f'Бот распознает данные  добавит их в google-таблицу.\n'
                        f'Позже Вы сможете изменить или удалить их из таблицы.\n\n'
                        f'Изучите примеры сообщений, чтобы понять как общаться\n'
                        f'с ботом — команда /samples.')
#нажатие на кнопку доходы(информация по доходам)
@dp.message_handler(Text(equals=["4.Доходы"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Доходы\n\n'
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
#нажатие на кнопку бюджеты(информация по бюджетам)
@dp.message_handler(Text(equals=["5.Бюджеты"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Бюджеты\n\n'
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
                        f'в google-таблицу /table.\n\n'
                        f'После изменения google-таблицы не забывайте\n'
                        f'синхронизировать её с ботом командой /sync.')
#нажатие на кнопку источники(информация по источникам)
@dp.message_handler(Text(equals=["6.Источники"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Источники\n\n'
                        f'Источники — это наличные, кредитные и дебитовые карты и т.п.\n\n'
                        f'Разделяйте расходы и доходы по источникам, если это важно\n'
                        f'для Вас.\n'
                        f'У каждого источника есть синонимы.Они позволяют упрощать\n'
                        f'сообщения для бота.Например у источника "Банковская\n'
                        f'карта" может быть "сбер" или "альфа".Изменять синонимы\n'
                        f'можно самостоятельно,для этого перейдите в google-таблицу\n'
                        f'/table.\n\n'
                        f'После изменения google-таблицы не забывайте\n'
                        f'синхронизировать её с ботом командой /sync.')
#нажатие на кнопку категории(информация о категориях)
@dp.message_handler(Text(equals=["7.Категории"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Категории\n\n'
                        f'Категории — основные типы расходов для удобства их\n'
                        f'подсчета и анализа:квартира, продукты и автомобиль и т.д.\n'
                        f'Для доходов и долгов есть свои категории\n\n'
                        f'Создавайте любое корличество категорий.\n\n'
                        f'У каждой категории есть синонимы.Они позволяют упрощать\n'
                        f'сообщения для бота.Например,у категории "Автомобиль"\n'
                        f'могут быть синонимы "авто,машина,стоянка,гараж,осаго,\n'
                        f'бензин,бенз".Любое сообщение с этими словами будет\n'
                        f'добавлено в "Автомобиль".\n\n'
                        f'Изменять синонимы можно самостоятельно, для этого\n'
                        f'перейдите в google-таблицу /table. После изменения таблицы\n'
                        f'не забывайте синхронизировать её с ботом командой /sync.')
#нажатие на кнопку google-таблица(информация по google-таблице)
@dp.message_handler(Text(equals=["8.Google-таблица"]))
async def btn_balance(message: types.Message):
    await bot.send_message(message.from_user.id,f'Google-таблица\n\n'
                        f'Таблица в Google позволяет увидеть наглядные отчеты или\n'
                        f'вносить изменения,минуя бота.Смотрите на таблицуне реже 1\n'
                        f'раза в неделю,чтобы иметь наглядное представление о \n'
                        f'Ваших финансах.\n\n'
                        f'После изменения таблицы синхронизируйте её с ботом\n'
                        f'командой /sync.После синхронизации все изменения будут\n'
                        f'внесены в базу бота,и он будет учитывать новый баланс и\n'
                        f'синонимы \n'
                        f'Ссылка на таблицу доступная по команде /table.".\n\n'
                        f'Cправка по таблице — https://www.greenzbot.ru/help\n')


#комана /samples
@dp.message_handler(commands="samples", state="*")
async def samples_command(message: types.Message):
    await bot.send_message(message.from_user.id,f'Примеры сообщений для бота:\n\n'
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


# запуск телеграм бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
