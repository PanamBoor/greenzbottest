# coding=utf-8
import sqlite3
from random import randint

def ensure_connection(func):
    """ Декоратор для подключения к СУБД: открывает соединение,
        выполняет переданную функцию и закрывает за собой соединение.
        Потокобезопасно!
    """

    def inner(*args, **kwargs):
        with sqlite3.connect('sqlite_users.db') as conn:
            kwargs['conn'] = conn
            res = func(*args, **kwargs)
        return res

    return inner


# Создаём таблицу под запоминание пользователей - User
# Она совмещает в себе: id пользователя в базе, его SpreedsheetId
# Так же создаём таблицу для каждой записи в таблицу, чтобы записывать айдишник запись
# Так же записывать последнюю ячейку, где велась запись и её текст, который получил бот

@ensure_connection
def init_db(conn, force: bool = False):
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS users')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY,
            user_id INT NOT NULL,
            spreedsheetid TEXT NOT NULL,
            town TEXT NOT NULL
        )
    ''')

    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS messages')

    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY,
            user_id INT NOT NULL,
            spreedsheetid TEXT NOT NULL,
            last_ind_rashod TEXT NOT NULL,
            last_ind_dohod TEXT NOT NULL,
            last_ind_dolg TEXT NOT NULL,
            last_message TEXT NOT NULL
        )
    ''')


# Ретурн найденного человека в базе
@ensure_connection
def get_have_user_in_a_base(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id, ))
    user_result_id = c.fetchall()
    if not user_result_id:
        return 0
    else:
        return 1


@ensure_connection
def add_new_user_to_base(conn, user_id: int, spreedsheetid: str, town: str):
    c = conn.cursor()
    c.execute(
        'INSERT INTO users (user_id, spreedsheetid, town) VALUES (?, ?, ?)',
        (user_id, spreedsheetid, town))
    conn.commit()
    print('Bot have a new user')

@ensure_connection
def get_spreedsheetid_by_user_id(conn, user_id: int):
	c = conn.cursor()
	c.execute("SELECT spreedsheetid FROM users WHERE user_id = ?", (user_id, ))
	spreedshet_id_of_user = c.fetchall()
	return spreedshet_id_of_user[0][0]

# Return any message of user spreedsheetid
@ensure_connection
def get_have_user_any_message(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT user_id FROM messages WHERE user_id = ?", (user_id, ))
    user_result_id = c.fetchall()
    if not user_result_id:
        return 0
    else:
        return 1

# Add new data in table of messages in dohod
@ensure_connection
def add_new_message_in_base_in_dohod(conn, user_id: int, spreedsheetid: str, last_message: str, last_ind_dohod: str, last_ind_rashod: str, last_ind_dolg: str):
	c = conn.cursor()
	c.execute(
        'INSERT INTO messages (user_id, spreedsheetid, last_ind_dohod, last_message, last_ind_rashod, last_ind_dolg) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, spreedsheetid, last_ind_dohod, last_message, last_ind_rashod, last_ind_dolg))
	conn.commit()
	print('Bot get new message')

# Get last message from user_id in table in dohod
@ensure_connection
def get_last_message_of_user_id_in_dohod(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT last_ind_dohod FROM messages WHERE user_id = ?", (user_id, ))
    last_message = c.fetchall()
    return last_message[-1][0]

# Get last message from user_id in table in rashod
@ensure_connection
def get_last_message_of_user_id_in_rashod(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT last_ind_rashod FROM messages WHERE user_id = ?", (user_id, ))
    last_message = c.fetchall()
    return last_message[-1][0]

# Get last message from user_id in table in dolg
@ensure_connection
def get_last_message_of_user_id_in_dolg(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT last_ind_dolg FROM messages WHERE user_id = ?", (user_id, ))
    last_message = c.fetchall()
    return last_message[-1][0]

# Get last id of message in table
@ensure_connection
def get_id_of_last_message_of_user_id(conn, user_id: int):
    c = conn.cursor()
    c.execute("SELECT id FROM messages WHERE user_id = ?", (user_id, ))
    last_message = c.fetchall()
    return last_message[-1][0]

# Delete last message of user_id
@ensure_connection
def delete_last_message(conn, user_id: int):
    c = conn.cursor()
    last_user_id = get_id_of_last_message_of_user_id(user_id=user_id)
    c.execute('DELETE FROM messages WHERE user_id = ? AND id = ?', (user_id, last_user_id))
    conn.commit()

# Delete user from Base
@ensure_connection
def delete_user(conn, user_id: int):
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
    conn.commit()





if __name__ == '__main__':
    init_db()