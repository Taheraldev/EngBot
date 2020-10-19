#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import telebot
import pymysql.cursors
import os
import random
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root",
                             db="engdb")


def mainmenu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_task = types.InlineKeyboardButton("Задание", callback_data="Task")
    button_text = types.InlineKeyboardButton("Текст", callback_data="Text")
    markup.add(button_task, button_text)
    return markup


@bot.message_handler(commands=['start'])
def welcome(message):
    id = message.chat.id
    bot.send_message(id, "Введите кодовое слово")


@bot.message_handler(content_types=['text'])
def text(message):
    id = message.chat.id
    if message.chat.type == 'private':
        with connection.cursor() as cursor:
            cursor.execute("""SELECT count FROM persons where id=""" + str(id))
            in_base = cursor.fetchone()
            if in_base is None:
                if message.text == 'К':
                    cursor.execute("""INSERT into persons VALUES (""" + str(id) + """, 0);""")
                    connection.commit()
                    bot.send_message(id, 'Привет, {0.first_name}!'.format(message.from_user, bot.get_me()),
                                     parse_mode='html',
                                     reply_markup=mainmenu())
                else:
                    bot.send_message(id, "Неверное кодовое слово!")
            else:
                listFiles = []
                way = os.walk(os.path.abspath('./Units/Unit' + message.text + '/task'))
                for i in way:
                    listFiles.append(i)
                Nfile = 0
                for address, dirs, files in listFiles:
                    rand = random.randint(0, len(files))
                    print(len((files)))
                    for file in files:
                        if Nfile == rand:
                            img = open(os.path.abspath('./Units/Unit' + message.text + '/task/' + file), 'rb')
                            bot.send_photo(id, img)
                            break
                        Nfile += 1


@bot.callback_query_handler(func=lambda c: True)  # Обработка кнопки в главном меню
def inline(c):
    listFiles = []
    if c.data == 'Text':  # Работа с БД, проверяет какое последнее задание делал человек, и отсылает при запросе
        # следующее
        idUser = c.from_user.id
        way = os.walk(os.path.abspath('./photo/'))
        with connection.cursor() as cursor1:  # достать count
            cursor1.execute("""SELECT count FROM persons where id=""" + str(idUser))
            bd = cursor1.fetchone()[0]
            flag = False
            for i in way:
                listFiles.append(i)
            for address, dirs, files in listFiles:
                if bd == len(files):
                    bot.send_message(idUser, "Ты ")
                    break
                for file in files:
                    Nfile = file.rsplit('.', 1)[0]
                    if (int(Nfile) == (bd + 1)) & (int(Nfile) <= len(files)):
                        img = open(os.path.abspath('./photo/' + file), 'rb')
                        bot.send_photo(idUser, img, reply_markup=mainmenu())
                        with connection.cursor() as cursor2:  # инкремент файла на +1
                            cursor2.execute("""UPDATE persons SET count=count+1 WHERE id=""" + str(idUser))
                        connection.commit()
                    if flag:
                        break
        connection.commit()


bot.polling(none_stop=True)
