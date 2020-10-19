import pymysql.cursors

connection = pymysql.connect(host="localhost",
                             user="root",
                             password="root",
                             db="engdb")

with connection.cursor() as cursor:  # создание пользователя в бд
    cursor.execute("""SELECT count FROM persons where id=""" + """0""")
    in_base = cursor.fetchone()
    if in_base is None:
        cursor.execute("""INSERT into persons VALUE (""" + """0""" + """, 0);""")
connection.commit()

with connection.cursor() as cursor:  # достать count
    cursor.execute("""SELECT count FROM persons where id=""" + """0""")
    print(cursor.fetchone())
connection.commit()

with connection.cursor() as cursor:  # инкремент файла на +1
    cursor.execute("""UPDATE persons SET count=count+1 WHERE id=""" + """0""")
connection.commit()

with connection.cursor() as cursor:  # инкремент файла на +1
    cursor.execute("""UPDATE persons SET count=0 WHERE id=""" + """0""")
connection.commit()
