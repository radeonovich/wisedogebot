import telebot
from telebot import types
import logging

logging.basicConfig(level=logging.INFO)  # set logger to log all info except telegram debug messages

with open("token.txt", 'r') as tokenFile:  # get bot token
    bot = telebot.TeleBot(tokenFile.read())
channelName = '@testomeska'  # channel to post to
moderators = [518283574]  # who can moderate


def checkadmin(message):
    if message.from_user.id in moderators:
        return True
    return False


@bot.message_handler(commands=["start"])
def start(message):
    logging.info("User {0}, id{1} entered /start".format(message.from_user.first_name, str(message.from_user.id)))
    markup = makebuttons(message)
    bot.send_message(message.chat.id,
                     'Здесь ты можешь предложить опубликовать свою мудрость Клыка.\nВыбери режим работы.',
                     reply_markup=markup)  # hello message


imglist = [] # don't know how to avoid global variables here
datalist = []


def makebuttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Предложить")
    markup.add(item1)
    if checkadmin(message):
        item2 = types.KeyboardButton("Модерировать")
        markup.add(item2)
    return markup


@bot.message_handler(content_types=["text"])
def handle_admin_text(message):
    global imglist, datalist
    if message.text.strip() == 'Предложить':
        bot.send_message(message.chat.id, 'Пришли картинку с волком, я добавлю ее в очередь модерации.')

    if message.text.strip() == 'Модерировать':
        if checkadmin(message):
            logging.warning("User {0}, id{1} started moderating".format(message.from_user.first_name, str(message.from_user.id)))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # add buttons for moderation
            item1 = types.KeyboardButton("+")
            item2 = types.KeyboardButton("-")
            item3 = types.KeyboardButton("Пропуск")
            markup.add(item1)
            markup.add(item2)
            markup.add(item3)
            with open("moderationQueue.txt", "r") as modQueueFile:
                imglist = modQueueFile.readlines()  # list of image data, each element has format: image_id user_id
            if len(imglist) != 0:
                bot.send_message(message.chat.id, 'Включен режим модерации.')
                datalist = imglist[0].split()
                # take the last image data and split to [image_id, user_id]
                # maybe dict would be better here
                bot.send_photo(message.chat.id, photo=datalist[0])
                bot.send_message(message.chat.id, 'Картинка от {0}id{1}'.format('', datalist[1]), reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Предложка пуста.')
        else:
            bot.send_message(message.chat.id, 'Вы не можете модерировать.')
    if checkadmin(message) and len(imglist) != 0:  # handling moderator decision

        if message.text.strip() == '+':
            postQueueFile = open("postQueue.txt", "a")
            postQueueFile.write(datalist[0]+'\n')
            postQueueFile.close()
            imglist.pop(0)
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
            markup = makebuttons(message)
            bot.send_message(message.chat.id, 'Картинка добавлена в очередь, image id=' + datalist[0], reply_markup=markup)

        elif message.text.strip() == '-':
            imglist.pop(0)
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
            markup = makebuttons(message)
            bot.send_message(message.chat.id, 'Картинка снята с модерации.', reply_markup=markup)

        elif message.text.strip() == 'Пропуск':
            imglist.append(imglist.pop(0))  # move image to the start of list
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
            markup = makebuttons(message)
            bot.send_message(message.chat.id, 'Картинка перемещена в начало очереди.', reply_markup=markup)


@bot.message_handler(content_types=['photo'])  # receive an image from user
def handle_photo(message):
    received_image = message.photo[-1].file_id
    logging.info(
        'A photo has just received from user {0}, id {1}'.format(message.from_user.first_name, message.from_user.id))
    with open("moderationQueue.txt", "a") as modQueueFile:
        modQueueFile.write(received_image + ' ' + str(message.from_user.id) + '\n')
        modQueueFile.close()
    bot.send_message(message.chat.id, 'Отправил на проверку.')


bot.polling(none_stop=True, interval=0)
