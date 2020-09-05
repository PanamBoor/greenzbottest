from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove,KeyboardButton

#кнопки комманда help
balance_btn = KeyboardButton("1.Баланс",callback_data = 'balance')
otchet_btn = KeyboardButton("2.Отчеты",callback_data = 'otchet_btn ')
rashod_btn = KeyboardButton("3.Расходы",callback_data = 'rashod_btn')
dohod_btn = KeyboardButton("4.Доходы",callback_data = 'dohod_btn')
budjet_btn = KeyboardButton("5.Бюджеты",callback_data = 'budjet_btn')
istochniki_btn = KeyboardButton("6.Источники",callback_data = 'istochniki_btn')
kategoriy_btn = KeyboardButton("7.Категории",callback_data = 'kategoriy_btn')
google_table_btn = KeyboardButton("8.Google-таблица",callback_data = 'google_table_btn')

#подключение кнопок команды хелп
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    balance_btn, otchet_btn
)
greet_kb.row(rashod_btn, dohod_btn)
greet_kb.row(budjet_btn, istochniki_btn)
greet_kb.row(kategoriy_btn,google_table_btn)

