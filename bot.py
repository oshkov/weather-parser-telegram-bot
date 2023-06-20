import telebot
from telebot import types
import config
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import fake_useragent

print("@weathersupporttgbot\n\nБот начал работу (",time.strftime('%d.%m.%Y / %X'),")\n")

bot = telebot.TeleBot(config.TOKEN)

# Команды /start и /edit
@bot.message_handler(commands=["start", "edit"])
def welcome(message):

    db = sqlite3.connect("users.db")
    sql = db.cursor()

    # Создается таблица с пользователями, если до этого ее не было
    sql.execute("""CREATE TABLE IF NOT EXISTS users (
    enter TEXT,
    id TEXT,
    username TEXT,
    name TEXT,
    lastname TEXT,
    city TEXT,
    url TEXT,
    notification INT
)""")
    db.commit()

    # Пользователь добавляется в таблицу, если его до этого не было
    sql.execute(f"SELECT id FROM users WHERE id = ?", (message.from_user.id, ))
    if sql.fetchone() is None:
        jointime = time.strftime('%d.%m.%Y / %X')
        sql.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (jointime ,message.from_user.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 0, 0, 1))
        db.commit()
    else:
        pass

    # Бот спрашивает город пользователя
    global messageWriteCity
    messageWriteCity = bot.send_message(message.chat.id, "Напиши название города")
    bot.register_next_step_handler(message, addCity);

# Функция добавления города пользователя в таблицу
def addCity(message):
    db = sqlite3.connect("users.db")
    sql = db.cursor()

    search = "https://www.gismeteo.ru/search/" # Ссылка где будут парситься результаты поиска по городу
    city = message.text # В переменную добавляется сообщение пользователя
    link = search + city # Создание ссылки с нужным городом
    HEADERS = {'User-Agent': fake_useragent.UserAgent().random} # Создание фэйк юзер агент
    page = requests.get(link, headers=HEADERS)
    html = BeautifulSoup(page.text, 'lxml') # Получение кода страницы
    try:
        try:
            list = html.find_all("div", {"class": "catalog-list"})[1] # Если есть аэропорты выбирается список с населенными пунктами
        except:
            list = html.find_all("div", {"class": "catalog-list"})[0] # Если нет аэропортов

        # Проверка на количество найденных городов (Максимум 3 города)
        try: 
            city0 = list.find_all("div", {"class": "catalog-item"})[0] # Выбирается первый город из списка
            nameOfCity0 = city0.find("a", {"class": "link-item"}).get_text(strip=True) # Получает название первого города из списка
            district0 = city0.find("a", {"class": "link district"}).get_text(strip=True) # Получает республику
            country0 = city0.find("a", {"class": "link country"}).get_text(strip=True) # Получает страну
            global urlOfCity0
            urlOfCity0 = "https://www.gismeteo.ru/" + city0.find("a", {"class": "link-item"}).get('href'); # Получает ссылку на погоду первого города из списка

            # Создается клавиатура с одним городом, если другие не найдены
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton(f"{nameOfCity0} ({district0} {country0})", callback_data='firstCity')
            btn2 = types.InlineKeyboardButton("Выбрать другой город", callback_data='edit')
            markup.add(btn1, btn2)
            try:
                city1 = list.find_all("div", {"class": "catalog-item"})[1] #Выбирается второй город из списка
                nameOfCity1 = city1.find("a", {"class": "link-item"}).get_text(strip=True) #Получает название первого города из списка
                district1 = city1.find("a", {"class": "link district"}).get_text(strip=True) #Получает республику
                country1 = city1.find("a", {"class": "link country"}).get_text(strip=True) #Получает страну
                global urlOfCity1
                urlOfCity1 = "https://www.gismeteo.ru/" + city1.find("a", {"class": "link-item"}).get('href')

                # Создается клавиатура с двумя городами, если другие не найдены
                markup = types.InlineKeyboardMarkup(row_width=1)
                btn1 = types.InlineKeyboardButton(f"{nameOfCity0} ({district0} {country0})", callback_data='firstCity')
                btn2 = types.InlineKeyboardButton(f"{nameOfCity1} ({district1} {country1})", callback_data='secondCity')
                btn3 = types.InlineKeyboardButton("Выбрать другой город", callback_data='edit')
                markup.add(btn1, btn2, btn3)
                try:
                    city2 = list.find_all("div", {"class": "catalog-item"})[2] # Выбирается третий город из списка
                    nameOfCity2 = city2.find("a", {"class": "link-item"}).get_text(strip=True) # Получает название первого города из списка
                    district2 = city2.find("a", {"class": "link district"}).get_text(strip=True) # Получает республику
                    country2 = city2.find("a", {"class": "link country"}).get_text(strip=True) # Получает страну
                    global urlOfCity2
                    urlOfCity2 = "https://www.gismeteo.ru/" + city2.find("a", {"class": "link-item"}).get('href')

                    # Создается клавиатура с тремя городами, даже если другие найдены
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    btn1 = types.InlineKeyboardButton(f"{nameOfCity0} ({district0} {country0})", callback_data='firstCity')
                    btn2 = types.InlineKeyboardButton(f"{nameOfCity1} ({district1} {country1})", callback_data='secondCity')
                    btn3 = types.InlineKeyboardButton(f"{nameOfCity2} ({district2} {country2})", callback_data='thirdCity')
                    btn4 = types.InlineKeyboardButton("Выбрать другой город", callback_data='edit')
                    markup.add(btn1, btn2, btn3, btn4)
                except:
                    pass
            except:
                pass
        except:
            pass

        bot.send_message(message.chat.id, "Выбери город из предложенных", reply_markup=markup)

        # Город добавляется в базу данных
        sql.execute(f"UPDATE users SET city = ? WHERE id = ?", (message.text, message.from_user.id))
        db.commit()

        bot.delete_message(message.chat.id, message.message_id) # Сообщение с выбором города удаляется

        try:
            bot.delete_message(message.chat.id, messageWriteCity.message_id)
        except:
            bot.delete_message(message.chat.id, messageWriteCity1.message_id)

    # Исключение, если город не найден
    except:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Выбрать другой город", callback_data='edit')
        markup.add(btn1)
        bot.send_message(message.chat.id, "По вашему запросу ничего не найдено", reply_markup=markup)

# Команда /about
@bot.message_handler(commands=["about"])
def weather(message):

    bot.send_message(message.chat.id, config.INFORMATION)

# Команда /stats, показывает количество пользователей в боте
@bot.message_handler(commands=["stats"])
def weather(message):

    # Создается клавиатура
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Показать список", callback_data='list') # Выведется переменная mes как сообщение (строка 182)
    markup.add(btn1)

    db = sqlite3.connect("users.db")
    sql = db.cursor()

    sql.execute("SELECT username FROM users")
    users = sql.fetchall()
    sql.execute("SELECT id FROM users")
    ids = sql.fetchall()

    # Собирается количество пользователей из таблицы
    try:
        num = 0
        u = []
        i = []
        while True:
            for user in users[num]:
                for id in ids[num]:
                    if user == None:
                        for i in sql.execute("SELECT name FROM users WHERE id = ?", (id,)):
                            name = i[0]
                        for i in sql.execute("SELECT url FROM users WHERE id = ?", (id,)):
                            city = i[0]
                        u.append(name)
                        num = num + 1
                    else:
                        for i in sql.execute("SELECT url FROM users WHERE id = ?", (id,)):
                            city = i[0]
                        user = "@" + user
                        u.append(user)
                        num = num + 1
    except:
        bot.send_message(message.chat.id, f"Всего пользоваетелей: {num}", reply_markup=markup)

        # В переменную mes добавляются id каждого пользователя в каждую строку
        try:
            num = 0
            global mes
            mes = ""
            while True:
                mes = mes + f"{u[num]}\n"
                num = num + 1
        except:
            pass

# Команда /weather
@bot.message_handler(commands=["weather"])
def weather(message):

    db = sqlite3.connect("users.db")
    sql = db.cursor()

    # Из таблицы берется значение, отвечающее за уведомления (0 - выкл, 1 - вкл)
    for i in sql.execute("SELECT notification FROM users WHERE id = ?", (message.from_user.id, )):
        notif = i[0]

    # Создается клавиатура
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
    btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
    btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
    markup.row(btn1, btn2, btn3)

    # Проверка на уведомления
    if notif == 0:
        btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
        btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifNow')
        markup.add(btn4, btn5)
    else:
        btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
        btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifNow')
        markup.add(btn4, btn5)

    # Поиск погоды по городу пользователя
    while True:
        try:
            for i in sql.execute("SELECT url FROM users WHERE id = ?", (message.from_user.id, )):
                url = i[0]
            url1 = url + "now"
            HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
            page = requests.get(url1, headers=HEADERS)
            html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
            title = html.find("div", {"class": "page-title"})
            titleText = title.find("h1").get_text()
            tempNow = html.find_all("span", {"class": "unit unit_temperature_c"})[0].get_text(strip=True)
            status = html.find("div", {"class": "now-desc"}).get_text(strip=True)
            tempFeel = html.find_all("span", {"class": "unit unit_temperature_c"})[7].get_text(strip=True)
            wind = html.find("div", {"class": "unit unit_wind_m_s"})
            wind.select_one('.item-measure').decompose()
            wind = wind.get_text()

            bot.send_message(message.chat.id, f"""{titleText}:

*{status}, {tempNow}°, {wind} м/c*

По ощущению {tempFeel}""", reply_markup=markup, parse_mode="Markdown")
                
            break

        # Повтор запроса, если не получилось спарсить информацию
        except:
            print(f"Не получилось спарсить информацию")
            time.sleep(2)

# Команды при нажатии на кнопки клавиатуры
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    db = sqlite3.connect("users.db")
    sql = db.cursor()

# Функции

    # Функция парсинга температуры
    def temp(num):
        temp = html.find_all("span", {"class": "unit unit_temperature_c"})[num].get_text(strip=True)
        return temp

    # Функция парсинга времени
    def timings(num):
        time = html.find_all("div", {"class": "row-item"})[num]
        time = time.find("span")
        time.select_one('.time-sup').decompose()
        time = time.get_text(strip=True)
        return time

    # Функция парсинга погоды
    def status(num):
        status = html.find_all("div", {"class": "weather-icon tooltip"})[num].get('data-text')
        return status

    # Функция парсинга дня недели
    def day(num):
        day = html.find_all("div", {"class": "day"})[num].get_text()
        return day

    # Функция парсинга даты
    def date(num):
        date = html.find_all("div", {"class": "date"})[num].get_text()
        return date

    # Функция парсинга скорости ветра
    def wind(num):
        wind = html.find_all("span", {"class": "wind-unit unit unit_wind_m_s"})[num].get_text()
        return wind

    # Функция выключения уведомлений для пользователя
    def notifOff():
        db = sqlite3.connect("users.db")
        sql = db.cursor()

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]
        sql.execute(f"UPDATE users SET notification = ? WHERE id = ?", (0, call.from_user.id))
        db.commit()
        bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Уведомления выключены🔕")

    # Функция включения уведомлений для пользователя
    def notifOn():
        db = sqlite3.connect("users.db")
        sql = db.cursor()

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]
        sql.execute(f"UPDATE users SET notification = ? WHERE id = ?", (1, call.from_user.id))
        db.commit()
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Уведомления включены🔔\n\nВы будете получать уведомления в 7.00 и 21.00 каждый день")

    # Функция, показывающая погоду сейчас после добавления города в базу данных
    def pogodaAdd(url):
        while True:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 • · ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                url = url + "now"
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · • ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                status = html.find("div", {"class": "now-desc"}).get_text(strip=True)
                wind = html.find("div", {"class": "unit unit_wind_m_s"})
                wind.select_one('.item-measure').decompose()
                wind = wind.get_text()
                temp = html.find_all("span", {"class": "unit unit_temperature_c"})[0].get_text(strip=True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · · •", reply_markup=markup) # Сообщение, показывающее поиск информации
                temp1 = html.find_all("span", {"class": "unit unit_temperature_c"})[1].get_text(strip=True)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText}:

*{status}, {temp}°, {wind} м/с*

По ощущению {temp1}""", reply_markup=markup, parse_mode="Markdown")
                
                break

            except:
                # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Что то пошло не так, повторите попытку чуть позже", reply_markup=markup)
                time.sleep(2)

    # Проверка на уведомления, от которого зависит последняя кнопка в клавиатуре
    for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
        notif = i[0]
    if notif == 1:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
        btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
        btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
        btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
        btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifNow')
        markup.row(btn1, btn2, btn3)
        markup.add(btn4, btn5)
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
        btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
        btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
        btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
        btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifNow')
        markup.row(btn1, btn2, btn3)
        markup.add(btn4, btn5)

    # Исход при выборе первого города из списка
    if call.data == 'firstCity':
        sql.execute("UPDATE users SET url = ? WHERE id = ?", (urlOfCity0, call.from_user.id))
        db.commit()
        pogodaAdd(urlOfCity0)

    # Исход при выборе второго города из списка
    elif call.data == 'secondCity':
        sql.execute("UPDATE users SET url = ? WHERE id = ?", (urlOfCity1, call.from_user.id))
        db.commit()
        pogodaAdd(urlOfCity1)

    # Исход при выборе третьего города из списка
    elif call.data == 'thirdCity':
        sql.execute("UPDATE users SET url = ? WHERE id = ?", (urlOfCity2, call.from_user.id))
        db.commit()
        pogodaAdd(urlOfCity2)

    # Исход при нажати на кнопку "сейчас"
    elif call.data == 'pogodaNow':

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        # Проверка на уведомления
        if notif == 1:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifNow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifNow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)

        # Парсинг информации
        while True:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 • · ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                url1 = url + "now"
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                page = requests.get(url1, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()
                status = html.find("div", {"class": "now-desc"}).get_text(strip=True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · • ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                wind = html.find("div", {"class": "unit unit_wind_m_s"})
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · · •", reply_markup=markup) # Сообщение, показывающее поиск информации
                wind.select_one('.item-measure').decompose()
                wind = wind.get_text()

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText}:

*{status}, {temp(0)}°, {wind} м/с*

По ощущению {temp(1)}""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Исход при нажатии на кнопку "сегодня"
    elif call.data == "pogodaToday":

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 1:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifToday')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifToday')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)

        # Парсинг информации
        while True:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 • · ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · • ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · · •", reply_markup=markup) # Сообщение, показывающее поиск информации
                date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText} сегодня ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Исход при нажатии на кнопку "завтра"
    elif call.data == 'pogodaTomorrow':

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 1:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifTomorrow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifTomorrow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)

        # Парсинг информации
        while True:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 • · ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                url = url + "tomorrow"
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · • ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                title = html.find("div", {"class": "page-title"})
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · · •", reply_markup=markup) # Сообщение, показывающее поиск информации
                titleText = title.find("h1").get_text()
                date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText} ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except :
                print(f"Не получилось спарсить информацию")
                time.sleep(2)
         
    # Исход при нажатии на кнопку "10 дней"
    elif call.data == 'pogoda10d':

        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 1:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notif10d')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notif10d')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)

        # Парсинг информации
        while True:
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 • · ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                url = url + "10-days/"
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · • ·", reply_markup=markup) # Сообщение, показывающее поиск информации
                title = html.find("div", {"class": "page-title"})
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Поиск информации 🔍 · · •", reply_markup=markup) # Сообщение, показывающее поиск информации
                titleText = title.find("h1").get_text()

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText}:

*{day(0)} ({date(0)}):* {temp(1)}°, {status(0)}
*{day(1)} ({date(1)}):* {temp(3)}°, {status(1)}
*{day(2)} ({date(2)}):* {temp(5)}°, {status(2)}
*{day(3)} ({date(3)}):* {temp(7)}°, {status(3)}
*{day(4)} ({date(4)}):* {temp(9)}°, {status(4)}
*{day(5)} ({date(5)}):* {temp(11)}°, {status(5)}
*{day(6)} ({date(6)}):* {temp(13)}°, {status(6)}
*{day(7)} ({date(7)}):* {temp(15)}°, {status(7)}
*{day(8)} ({date(8)}):* {temp(17)}°, {status(8)}
*{day(9)} ({date(9)}):* {temp(19)}°, {status(9)}""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Вывод погоды при изменении параметра уведомлений при показе погоды "сейчас"
    elif call.data == 'notifNow':
        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifNow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOn()
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifNow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)

            notifOff()

        # Парсинг информации
        while True:
            try:
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                url1 = url + "now"
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                page = requests.get(url1, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()
                status = html.find("div", {"class": "now-desc"}).get_text(strip=True)
                wind = html.find("div", {"class": "unit unit_wind_m_s"})
                wind.select_one('.item-measure').decompose()
                wind = wind.get_text()

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText}:

*{status}, {temp(0)}°, {wind} м/с*

По ощущению {temp(1)}""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Вывод погоды при изменении параметра уведомлений при показе погоды "сегодня"
    elif call.data == 'notifToday':
        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifToday')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOn()
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifToday')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOff()

        # Парсинг информации
        while True:
            try:
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()

                date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText} сегодня ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)


    # Вывод погоды при изменении параметра уведомлений при показе погоды "завтра"
    elif call.data == 'notifTomorrow':
        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifTomorrow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOn()
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notifTomorrow')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOff()

        # Парсинг информации
        while True:
            try:
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                url = url + "tomorrow"
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()

                date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText} ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Вывод погоды при изменении параметра уведомлений при показе погоды "10 дней"
    elif call.data == 'notif10d':
        for i in sql.execute("SELECT notification FROM users WHERE id = ?", (call.from_user.id, )):
            notif = i[0]

        if notif == 0:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notif10d')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOn()
        else:
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
            btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
            btn3 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
            btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
            btn5 = types.InlineKeyboardButton("Вкл. уведомления", callback_data='notif10d')
            markup.row(btn1, btn2, btn3)
            markup.add(btn4, btn5)
            notifOff()

        # Парсинг информации
        while True:
            try:
                for i in sql.execute("SELECT url FROM users WHERE id = ?", (call.from_user.id, )):
                    url = i[0]
                HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                url = url + "10-days/"
                page = requests.get(url, headers=HEADERS)
                html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы

                title = html.find("div", {"class": "page-title"})
                titleText = title.find("h1").get_text()

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"""{titleText}:

*{day(0)} ({date(0)}):* {temp(1)}°, {status(0)}
*{day(1)} ({date(1)}):* {temp(3)}°, {status(1)}
*{day(2)} ({date(2)}):* {temp(5)}°, {status(2)}
*{day(3)} ({date(3)}):* {temp(7)}°, {status(3)}
*{day(4)} ({date(4)}):* {temp(9)}°, {status(4)}
*{day(5)} ({date(5)}):* {temp(11)}°, {status(5)}
*{day(6)} ({date(6)}):* {temp(13)}°, {status(6)}
*{day(7)} ({date(7)}):* {temp(15)}°, {status(7)}
*{day(8)} ({date(8)}):* {temp(17)}°, {status(8)}
*{day(9)} ({date(9)}):* {temp(19)}°, {status(9)}""", reply_markup=markup, parse_mode="Markdown")
                
                break

            # Повтор запроса, если не получилось спарсить информацию
            except:
                print(f"Не получилось спарсить информацию")
                time.sleep(2)

    # Исход при нажатии на кнопку "изменить город"
    elif call.data == 'edit':
        global messageWriteCity1
        messageWriteCity1 = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Напиши название города")
        bot.register_next_step_handler(messageWriteCity1, addCity); # Переход на функцию добавления города в базу данных

    # Исход при запросе подробного списка пользователей с id
    elif call.data == 'list':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Список пользователей:\n\n{mes}")

# Ответ на сообщения от пользователя
@bot.message_handler(content_types=["text"])
def basic_commands(message):

    db = sqlite3.connect("users.db")
    sql = db.cursor()

    if message.text == message.text:
        bot.send_message(message.chat.id, "Воспользуйтесь командами, либо перезапустите бота командой /start")
    else:
        bot.send_message(message.chat.id, "Воспользуйтесь командами, либо перезапустите бота командой /start")

if __name__ == '__main__':
    bot.infinity_polling()
