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

                spreadsheet1 = service.spreadsheets().create(body={
                'properties': {'title': adress, 'locale': 'ru_RU'},
                'sheets': [{'properties': {'sheetType': 'GRID',
                                           'sheetId': 0,
                                           'title': 'Доходы',
                                           'gridProperties': {'rowCount': 100, 'columnCount': 15}}}]
                }).execute()
                await bot.send_message(message.from_user.id, "Создание таблицы")

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
                                    "title": "Расходы",
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
    print("/help", message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f'Cправка\n\n\n/balance - Мой баланс \n/table - Ссылка на google-таблицу\n/sync - Синхронизация бота с google-таблицой\n/settings - Настройка \n/help  - Справка \n/delete - Удаление аккаунта \n\n'
                           f'Выберите интересующий раздел справки и получите краткую помощь.Если Ваш вопрос не решен,то обратитесь за помощью.Если  Ваш вопрос не решен , то обратитесь за помощью к живому оператору @......',
                           parse_mode='HTML', reply_markup=greet_kb)

    # кпнока баланс
    @dp.callback_query_handler(lambda c: c.data == '/balance')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f'Баланс\n\nБаланс - это максимальная сумма расходов на сегодня.\n\n'
                               f'Баланс положительный - спокойно тратьте указанную сумму, отрицательный - отложите расходы , иначе не уложитесь в бюджет\n\n'
                               f'По умолчанию бот присылает баланс Ежемесячных расходов.Добавьте к слову "баланс" название или синоним другого бюджета, чтобы проверить его баланс.Например, '
                               f'"баланс годовой"', parse_mode='HTML')

    # кнопка отчет
    @dp.callback_query_handler(lambda c: c.data == 'otchet_btn')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f'Отчеты\n\nВнутри бота доступен только отчет по балансу - команда \n /balance.\n\n'
                               f'Статистику по месяцам, категориям расходов, а также графические отчеты доступны в google-таблице - команда\n'
                               f'/table.', parse_mode='HTML')

    # кнопка расход
    @dp.callback_query_handler(lambda c: c.data == 'rashod_btn')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f'Доходы\n\nОтправляйте боту простые сообщения о Ваших расходах -\n"продукты 877".'
                               f'В сообщении обязательно укажите категорию и потраченную\n сумму, дополнительно можно указать дату,бюджет и источник\nрасходов.'
                               f'Бот распознает данные и добавит их в google-таблицу. Позже Вы\nсможете изменить или удалить их из таблиц.\n\n'
                               f'Изучите примеры сообщений,чтобы понять как общаться с ботом - команда /samples.',
                               parse_mode='HTML')

    # кнопка доход
    @dp.callback_query_handler(lambda c: c.data == 'dohod_btn')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id, f'Доходы\n\nОтправляйте боту простые сообщения о Ваших доходах -\n'
                                                     f'"доход 15000 аренда" или "зарпалата 35000".\n\nСоздайте отдельные категории только для доходов, указав в\ngoogle-таблице принадлежность категории только к доходам.\n\n'
                                                     f'В сообщении обязательно укажите категорию и полученную сумму, дополнительно можно указать дату и источник, в который поступил доход.\n\n'
                                                     f'Бот распознает данные и добавит их в google-таблицу.Позже Вы\nсможете изменить или удалить их из таблицы.\n\n'
                                                     f'Изучите примеры сообщений,чтобы понять как общаться с ботом - команда /samples.',
                               parse_mode='HTML')

    # кнопка бюджет
    @dp.callback_query_handler(lambda c: c.data == 'budjet_btn')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f'Бюджеты\n\nБюджеты разделяют Ваши расходы, чтобы их проще было\nконтролировать.\n\nБюджет обязательно привязан к периоду:неделя, месяц или год\n - и имеет лимит - максимальная сумма затрат за период'
                               f'Создавайтте любое килчество бюджетов.Разделите\nежемесячные и годовые расходы.Добавьте и контролируйте\nотдельный бюджет для каждой поездки в отпуск\n\n'
                               f'У каждого бюджета есть синонимы.Они позволяют упрощать\n сообщения для бота. Например, у бюджета "Годовые расходы" есть синоним "год".Изменять синонимы можно\n самостоятельно,для этого перейдите в google-таблицу/table.\n\n'
                               f'После изменения google-таблицы не забывайте\n синхронизировать её с ботом командой/sync.',
                               parse_mode='HTML')

    # кнопка источники
    @dp.callback_query_handler(lambda c: c.data == 'istochniki_btn')
    async def order(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f'Источники\n\nИсточники - это наличные, кредитные и дебетовые карты и т.п.\n'
                               f'Разделяйте расходы и доходы по источникам, если это важно для Вас.\n\nУ каждого источника есть синонимы.Они позволяют упрощать\nсообщения для бота.Например, у источника"Банковская\n'
                               f'карта" может быть "cбер" или "альфа".Изменять синонимы\nможно самостоятельно, для этого перейдите в google-таблицу\n/table.\n\n'
                               f'После изменения google-таблицы не забывайте\nсинхронизировать её с ботом командой /sync.',
                               parse_mode='HTML')


# запуск телеграм бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)