#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import telebot
import pymysql.cursors
import os
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
                    cursor.execute("""CREATE TABLE IF NOT EXISTS """ + """person""" + str(id) +
                                   """(Theme char(50), count int)""")
                    connection.commit()
                    bot.send_message(id, 'Привет, {0.first_name}! Добро пожаловать в кладовку с заданиями по '
                                         'английскому языку!\nпри пользовании ботом, пожалуйста, помни:\n1. оценку '
                                         'тебе '
                                         'никто ставить не будет\n2. результат оцениваешь только ты сам\n3. ошибаться '
                                         'это '
                                         'нормально\n4. ты можешь выполнять столько заданий, сколько тебе хочется\n5. '
                                         'нужно обязательно вникнуть в само задание, прочитать внимательно, '
                                         'что от тебя требуется, и только в конце ознакомиться с текстом задания\n6. с '
                                         'вопросами и замечаниями можно (и нужно) обратиться ко мне\n7. не все не '
                                         'совпавшие ответы являются неправильными, иногда они просто менее '
                                         'предпочтительные'.format(message.from_user, bot.get_me()),
                                     parse_mode='html',
                                     reply_markup=mainmenu())
                else:
                    bot.send_message(id, "Неверное кодовое слово!")
            else:
                with connection.cursor() as cursor1:
                    cursor1.execute("""SELECT task FROM engdb.activetasks where id=""" + str(id))
                    connection.commit()
                    activeTask = cursor1.fetchone()
                    if activeTask is None:
                        listFiles = []
                        path = './Units/Unit' + message.text + '/tasks'
                        if os.path.exists(path):
                            way = os.walk(os.path.abspath(path))
                            for i in way:
                                listFiles.append(i)
                            with connection.cursor() as cursor1:  # достать count
                                cursor1.execute(
                                    """SELECT count FROM """ + """person""" + str(id) + """ where theme =""" +
                                    message.text)
                                bd = cursor1.fetchone()
                                if bd is None:
                                    bd = 0
                                    cursor1.execute("""INSERT INTO """ + """person""" + str(id) + """ VALUE(""" +
                                                    message.text + """, 0)""")
                                else:
                                    bd = bd[0]

                                connection.commit()
                            for address, dirs, files in listFiles:
                                for file in files:
                                    if bd == len(files):
                                        bot.send_message(id, "Ты сделал все задания в этой теме")
                                        bd = -1
                                    Nfile = file.rsplit('.', 1)[0]
                                    if (int(Nfile) == (int(bd) + 1)) & (int(Nfile) <= len(files)):
                                        img = open(os.path.abspath('./Units/Unit' + message.text + '/tasks/' + file),
                                                   'rb')
                                        bot.send_document(id, img)
                                        with connection.cursor() as cursor1:
                                            cursor1.execute(
                                                """INSERT INTO engdb.activetasks VALUE (""" + str(id) + """, """ +
                                                message.text + """, """ + str(bd) + """)""")
                                            connection.commit()
                                        break
                        else:
                            bot.send_message(id, "Нет такой темы")
                    else:
                        with connection.cursor() as cursor1:
                            cursor1.execute("""SELECT unit FROM engdb.activetasks where id=""" + str(id))
                            connection.commit()
                            unitNumber = cursor1.fetchone()[0]
                            cursor1.execute("""SELECT task FROM engdb.activetasks where id=""" + str(id))
                            connection.commit()
                            taskNumber = cursor1.fetchone()[0]
                            with open(os.path.abspath('./Units/Unit' + str(unitNumber) + '/answers/'
                                                        + str(taskNumber + 1) + '.txt'), 'r') as file:
                                massAnswer = file.read().splitlines()
                                print(massAnswer)
                            arr = message.text.split('\n')
                            listOuter = []
                            for item in massAnswer:
                                if item not in arr:
                                    listOuter.append(item)
                            answerToPerson = '\n'.join(listOuter)
                            if len(listOuter) == 0:
                                bot.send_message(id, 'несовпадений нет')
                            else:
                                bot.send_message(id, "несовпадения: \n" + answerToPerson)
                            with connection.cursor() as cursor2:  # инкремент файла на +1
                                cursor2.execute("""UPDATE person""" + str(id) + """ SET count=count+1 WHERE Theme=""" +
                                                str(unitNumber))
                                cursor2.execute("""DELETE FROM engdb.activetasks where id =""" + str(id))
                            connection.commit()


@bot.callback_query_handler(func=lambda c: True)  # Обработка кнопки в главном меню
def inline(c):
    idUser = c.from_user.id
    listFiles = []
    if c.data == 'Text':  # Работа с БД, проверяет какое последнее задание делал человек, и отсылает при запросе
        # следующее
        way = os.walk(os.path.abspath('./photo/'))
        with connection.cursor() as cursor1:  # достать count
            cursor1.execute("""SELECT count FROM persons where id=""" + str(idUser))
            bd = cursor1.fetchone()[0]
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
        connection.commit()
    if c.data == 'Task':
        bot.send_message(idUser,  'Помимо этого нужно знать несколько правил пользования:\n1. все с маленькой '
                                  'буквы\n2. '
                                  'никаких знаков препинания\n3. ответы только в полной форме (did not вместо '
                                  'didn\'t)\n4. ответы записываются под номерами и столбиком\n(\n1.\n2.\n3.\n)\n5. если '
                                  'под одной '
                                  'цифрой несколько ответов, пишите их через точку с запятой (1. did not; can not; '
                                  'will not)')


bot.polling(none_stop=True)




