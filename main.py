import telebot
from telebot import types
import logging

logging.basicConfig(level=logging.DEBUG)  # set logger to log all info

tokenFile = open("token.txt", 'r')
bot = telebot.TeleBot(tokenFile.read())
tokenFile.close()

channelName = '@testomeska'
adminid = 518283574


def checkadmin(message):
    if message.from_user.id == adminid:
        return True
    return False

#def moderate(message, i):
    # with open("moderationQueue.txt", "r") as modQueueFile:
    #     imglist = modQueueFile.readlines()
    #
    # datalist = imglist[i].split()
    # bot.send_photo(message.chat.id, photo=datalist[0])
    # bot.send_message(message.chat.id, 'Картинка от {0} id{1}'.format(datalist[1].username, datalist[1]))

@bot.message_handler(commands=["start"])
def start(message, res=False):
    logging.info("User {0}, id{1} entered /start".format(message.from_user.first_name, str(message.from_user.id)))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Предложить")
    markup.add(item1)
    if checkadmin(message):
        item2 = types.KeyboardButton("Модерировать")
        markup.add(item2)
    bot.send_message(message.chat.id,
                     'Здесь ты можешь предложить опубликовать свою мудрость Клыка.\nВыбери режим работы.',
                     reply_markup=markup)

imglist=[]
datalist=[]
@bot.message_handler(content_types=["text"])
def handle_admin_text(message):
    global imglist, datalist
    if message.text.strip() == 'Предложить':
        bot.send_message(message.chat.id, 'Пришли картинку с волком, я добавлю ее в очередь модерации.')

    if message.text.strip() == 'Модерировать':
        if checkadmin(message):
            bot.send_message(message.chat.id, 'Включен режим модерации.')
            logging.warning("User {0}, id{1} started moderating".format(message.from_user.first_name, str(message.from_user.id)))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("+")
            item2 = types.KeyboardButton("-")
            item3 = types.KeyboardButton("Пропуск")
            # with open("moderationQueue.txt", "r+") as modQueueFile:
            #     new_file = modQueueFile.readlines()
            #     modQueueFile.seek(0)
            #     for line in new_file:
            #         dataList = line.split()  # split line by spaces: dataList[0] = image id, [1] = user id
            #         bot.send_photo(message.chat.id, photo=dataList[0])
            #         bot.send_message(message.chat.id, 'Картинка от {0} id{1}'.format(dataList[1].username, dataList[1]))
            #     modQueueFile.truncate()
            with open("moderationQueue.txt", "r") as modQueueFile:
                imglist = modQueueFile.readlines()
            if len(imglist) != 0:
                datalist = imglist[0].split()
                bot.send_photo(message.chat.id, photo=datalist[0])
                bot.send_message(message.chat.id, 'Картинка от {0} id{1}'.format('username', datalist[1]))
                bot.send_message(message.chat.id, 'Модерируй, хуле. ', reply_markup=markup)
                #moderate(message, 0)
        else:
            bot.send_message(message.chat.id, 'Вы не можете модерировать.')
    if checkadmin(message) and len(imglist) != 0:
        if message.text.strip() == '+':
            postQueueFile = open("postQueue.txt", "a")
            postQueueFile.write(datalist[0]+'\n')
            postQueueFile.close()
            imglist.pop(0)
            bot.send_message(message.chat.id, 'Картинка добавлена в очередь, image id=' + datalist[0])
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
        elif message.text.strip() == '-':
            imglist.pop(0)
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
        elif message.text.strip() == 'Пропуск':
            imglist.append(imglist.pop(0))
            with open("moderationQueue.txt", "w") as modQueueFile:
                for line in imglist:
                    modQueueFile.write(line)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    receivedImages = []
    # for photo in message.photo:
    #     receivedImages.append(photo.file_id)
    receivedImages.append(message.photo[-1].file_id)
    logging.info(
        'A photo has just received from user {0}, id {1}'.format(message.from_user.first_name, message.from_user.id))
    for image in receivedImages:
        modQueueFile = open("moderationQueue.txt", "a")
        modQueueFile.write(image + ' ' + str(message.from_user.id) + '\n')
        modQueueFile.close()
        #bot.send_photo(message.chat.id, photo=image)


bot.polling(none_stop=True, interval=0)
