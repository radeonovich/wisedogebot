import telebot  # PyTelegramBotAPI
from telebot import types
from pathlib import Path  # to check if some paths exist
from sys import exit  # to stop program if config is not filled
import logging  # to log things
import sqlite3  # to make queues of suggested and moderated posts
import configparser  # to use config to set up token etc
from os import mkdir

logging.basicConfig(level=logging.INFO)  # set logger to log all info except telegram debug messages

config = configparser.ConfigParser()
if Path("./config.ini").is_file():
    config.read("./config.ini")
else:

    config = configparser.ConfigParser()  # init config file

    config.add_section('main')
    config.set('main', 'token', '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')
    config.set('main', 'channelName', '@mychannel')
    config.set('main', 'moderators', '123456789 987654321 314159265')

    logging.warning('No config file was found. Trying to create a new one...')
    try:
        with open("./config.ini", 'w') as configfile:
            config.write(configfile)
    except Exception as e:
        logging.error('Failed to create config file: ', e.__repr__(), e.args)
    else:
        logging.warning('A new config file was created. Fill it with your data and start bot again.')
    exit(0)


token = config.get('main', 'token')  # get bot token
bot = telebot.TeleBot(token)
channelName = config.get('main', 'channelName')  # channel to post to
moderators = config.get('main', 'moderators').split()  # who can moderate
try:  # ascii greeting in console
    from art import *  # pip install art
    tprint('WiseDogeBot')
except ImportError:
    pass


def sqlite_connect():
    conn = sqlite3.connect("db/database.db", check_same_thread=False)
    conn.execute("pragma journal_mode=wal;")
    return conn


def init_sqlite():
    conn = sqlite_connect()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE SuggestionQueue \
    (id integer primary key, user_id integer, username text, image text, extra text)''')
    cursor.execute('''CREATE TABLE PostQueue \
    (id integer primary key, user_id integer, username text, image text, extra text)''')
    conn.commit()
    conn.close()
    return


db = Path("./db/database.db")
if not db.is_file():
    logging.warning("Database not found, trying to create a new one...")
    try:
        mkdir('db')
        init_sqlite()
    except Exception as e:
        logging.error("Failed to create database : ", e.__repr__(), e.args)
        pass
    else:
        logging.info("Created database successfully.")


def insert_queue(table: str, user_id: int, username: str, image: str, extra: str):
    # adds an element to suggestion or post queue
    conn = sqlite_connect()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO ' + table + ' (user_id, username, image, extra) VALUES (?,?,?,?)',
        (user_id, username, image, extra)
    )
    conn.commit()


def pop_queue(table: str, image: str):
    conn = sqlite_connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ' + table + ' WHERE image = ?', (image,))
    conn.commit()


def check_admin(message):
    if str(message.from_user.id) in moderators:
        return True
    return False


@bot.message_handler(commands=["start"])
def start(message):
    logging.info("User {0}, id{1} entered /start".format(message.from_user.first_name, str(message.from_user.id)))
    markup = make_buttons(message)
    bot.send_message(
        message.chat.id,
        'Здесь ты можешь предложить опубликовать свою мудрость Клыка.\nВыбери режим работы.',
        reply_markup=markup)  # hello message


def make_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Предложить")
    markup.add(item1)
    if check_admin(message):
        item2 = types.KeyboardButton("Модерировать")
        markup.add(item2)
    return markup


@bot.message_handler(content_types=["text"])
def handle_admin_text(message):
    global user_id, username, image, extra
    if message.text.strip() == 'Предложить':
        bot.send_message(message.chat.id, 'Пришли картинку с волком, я добавлю ее в очередь модерации.')

    if message.text.strip() == 'Модерировать':
        if check_admin(message):
            logging.warning("User {0}, id{1} started moderating".format(
                message.from_user.first_name, str(message.from_user.id))
            )
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # add buttons for moderation
            item1 = types.KeyboardButton("+")
            item2 = types.KeyboardButton("-")
            item3 = types.KeyboardButton("Пропуск")
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)

            conn = sqlite_connect()
            cursor = conn.cursor()
            try:
                row = cursor.execute(
                    'SELECT user_id, username, image, extra FROM SuggestionQueue ORDER BY id ASC LIMIT 1'
                    ).fetchall()[0]  # get last image from suggested
            except IndexError:
                bot.send_message(message.chat.id, 'Предложка пуста.')
            else:
                user_id = row[0]  # bad practice, better replace to a dictionary
                username = row[1]
                image = row[2]
                extra = row[3]
                bot.send_photo(message.chat.id, photo=image)
                bot.send_message(
                    message.chat.id,
                    'Картинка от {0} id{1}'.format(username, user_id),
                    reply_markup=markup
                )

        else:
            bot.send_message(message.chat.id, 'Вы не можете модерировать.')
    # handling moderator decision
    if check_admin(message):

        if message.text.strip() == '+':  # will make bug if moderator sent + without the context of moderating
            insert_queue(
                table='PostQueue',
                user_id=user_id,
                username=username,
                image=image,
                extra=extra
            )
            markup = make_buttons(message)
            bot.send_message(
                message.chat.id,
                'Картинка добавлена в очередь.',
                reply_markup=markup
            )

        elif message.text.strip() == '-':
            pop_queue(table='SuggestionQueue', image=image)
            markup = make_buttons(message)
            bot.send_message(
                message.chat.id,
                'Картинка снята с модерации.',
                reply_markup=markup
            )

        elif message.text.strip() == 'Пропуск':  # remove image from queue and add it to the end
            pop_queue(table='SuggestionQueue', image=image)
            insert_queue(
                table='SuggestionQueue',
                user_id=user_id,
                username=username,
                image=image,
                extra=extra
            )
            markup = make_buttons(message)
            bot.send_message(
                message.chat.id,
                'Картинка перемещена в начало очереди.',
                reply_markup=markup
            )


@bot.message_handler(content_types=['photo'])  # receive an image from user
def handle_photo(message):
    received_image = message.photo[-1].file_id
    logging.info(
        'A photo has just received from user {0}, id {1}'.format(message.from_user.first_name, message.from_user.id))
    insert_queue(
        table='SuggestionQueue',
        user_id=message.from_user.id,
        username=message.from_user.username,
        image=received_image,
        extra=''
    )
    bot.send_message(message.chat.id, 'Отправил на проверку.')


bot.polling(none_stop=True, interval=0)
