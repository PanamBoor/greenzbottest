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

#подключение кнопок команды help
greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    balance_btn, otchet_btn
)
greet_kb.row(rashod_btn, dohod_btn)
greet_kb.row(budjet_btn, istochniki_btn)
greet_kb.row(kategoriy_btn,google_table_btn)


#кнопки команды setings
gorod_btn = KeyboardButton("1. Город",callback_data = 'gorod_btn')
time_btn = KeyboardButton("2. Время напоминания",callback_data = 'time_btn')

#подключение кнопок команды setings
greet_settings = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
gorod_btn
)
greet_settings.row(time_btn)

#кнопки команда settings 2.Время напоминания
time_00 = KeyboardButton("00",callback_data = '00')
time_01 = KeyboardButton("01",callback_data = '01')
time_02 = KeyboardButton("02",callback_data = '02')
time_03 = KeyboardButton("03",callback_data = '03')
time_04 = KeyboardButton("04",callback_data = '04')
time_05 = KeyboardButton("05",callback_data = '05')
time_06 = KeyboardButton("06",callback_data = '06')
time_07 = KeyboardButton("07",callback_data = '07')
time_08 = KeyboardButton("08",callback_data = '08')
time_09 = KeyboardButton("09",callback_data = '09')
time_10 = KeyboardButton("10",callback_data = '10')
time_11 = KeyboardButton("11",callback_data = '11')
time_12 = KeyboardButton("12",callback_data = '12')
time_13 = KeyboardButton("13",callback_data = '13')
time_14 = KeyboardButton("14",callback_data = '14')
time_15 = KeyboardButton("15",callback_data = '15')
time_16 = KeyboardButton("16",callback_data = '16')
time_17 = KeyboardButton("17",callback_data = '17')
time_18 = KeyboardButton("18",callback_data = '18')
time_19 = KeyboardButton("19",callback_data = '19')
time_20 = KeyboardButton("20",callback_data = '20')
time_21 = KeyboardButton("21",callback_data = '21')
time_22 = KeyboardButton("22",callback_data = '22')
time_23= KeyboardButton("23",callback_data = '23')

time_otmena = KeyboardButton("Отключить напоминания",callback_data = 'otmena')
#подключение кнопок команды time
greet_time = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True).row(
   time_00,time_01,time_02,time_03,time_04,time_05
)
greet_time.row(time_06,time_07,time_08,time_09,time_10,time_11)
greet_time.row(time_12,time_13,time_14,time_15,time_16,time_17)
greet_time.row(time_18,time_19,time_20,time_21,time_22,time_23)
greet_time.row(time_otmena)
btn_minut_00 = KeyboardButton("00")
btn_minut_15 = KeyboardButton("15")
btn_minut_30 = KeyboardButton("30")
btn_minut_45 = KeyboardButton("45")
greet_minuts = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True).row(
   btn_minut_00,btn_minut_15,btn_minut_30,btn_minut_45
)


#кнопки команда delete
btn_delete_yes = KeyboardButton("Да")
btn_delete_no = KeyboardButton("Нет")

greet_delete =  ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True).row(
    btn_delete_yes,btn_delete_no
)
