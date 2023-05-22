import telebot
from telebot import types
import config
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import fake_useragent

bot = telebot.TeleBot(config.TOKEN)

db = sqlite3.connect("users.db")
sql = db.cursor()

def temp(num):
    temp = html.find_all("span", {"class": "unit unit_temperature_c"})[num].get_text(strip=True)
    return temp

def timings(num):
    time1 = html.find_all("div", {"class": "row-item"})[num]
    time1R = time1.find("span")
    time1R.select_one('.time-sup').decompose()
    time = time1R.get_text(strip=True)
    return time

def status(num):
    status = html.find_all("div", {"class": "weather-icon tooltip"})[num].get('data-text')
    return status

def wind(num):
    wind = html.find_all("span", {"class": "wind-unit unit unit_wind_m_s"})[num].get_text()
    return wind

num = 0
while True:
    timeNow = time.strftime('%H:%M')
    time.sleep(1)

    if timeNow == "07:00":
        a = True
        while a == True:
            sql.execute("SELECT id FROM users WHERE notification = ?", (1,))
            rows = sql.fetchall()
            try:
                for id in rows[num]:

                    for i in sql.execute("SELECT url FROM users WHERE id = ?", (id, )):
                        url = i[0]
                    HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                    page = requests.get(url, headers=HEADERS)
                    html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                    title = html.find("div", {"class": "page-title"})
                    titleText = title.find("h1").get_text()
                    date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)

                    markup = types.InlineKeyboardMarkup(row_width=2)
                    btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
                    btn2 = types.InlineKeyboardButton("Завтра", callback_data='pogodaTomorrow')
                    btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
                    btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
                    btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifToday')
                    markup.row(btn1, btn2, btn3)
                    markup.add(btn4, btn5)

                    bot.send_message(id, f"""{titleText} сегодня ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")

                    print(f"{timeNow}) {num + 1} - {id} получил сообщение")
                    num = num + 1
                    time.sleep(1)
            except telebot.apihelper.ApiTelegramException:
                print(f"{id} заблочил бота")
                time.sleep(1)
                num = num + 1
            except AttributeError:
                print(f"Не получилось спарсить инфу для {num + 1}")
                time.sleep(1)
            except IndexError:
                timeNow = 0
                num = 0
                a = False
            except Exception as ex:
                print(f"Произошла ошибка {ex} --- для пользователя {id}")
                time.sleep(1)
                num = num + 1
        print("Рассылка окончена\n\n")
        time.sleep(60)

    if timeNow == "21:00":
        a = True
        while a == True:
            sql.execute("SELECT id FROM users WHERE notification = ?", (1,))
            rows = sql.fetchall()
            try:
                for id in rows[num]:

                    for i in sql.execute("SELECT url FROM users WHERE id = ?", (id, )):
                        url = i[0]
                    HEADERS = {'User-Agent': fake_useragent.UserAgent().random} #Создание фэйк юзер агент
                    url = url + "tomorrow"
                    page = requests.get(url, headers=HEADERS)
                    html = BeautifulSoup(page.text, 'lxml') #Получение кода страницы
                    title = html.find("div", {"class": "page-title"})
                    titleText = title.find("h1").get_text()
                    date = html.find_all("div", {"class": "date"})[1].get_text(strip=True)

                    markup = types.InlineKeyboardMarkup(row_width=2)
                    btn1 = types.InlineKeyboardButton("Сейчас", callback_data='pogodaNow')
                    btn2 = types.InlineKeyboardButton("Сегодня", callback_data='pogodaToday')
                    btn3 = types.InlineKeyboardButton("10 дней", callback_data='pogoda10d')
                    btn4 = types.InlineKeyboardButton("Изменить город", callback_data='edit')
                    btn5 = types.InlineKeyboardButton("Выкл. уведомления", callback_data='notifTomorrow')
                    markup.row(btn1, btn2, btn3)
                    markup.add(btn4, btn5)

                    bot.send_message(id, f"""{titleText} ({date}):

*{timings(3)}.00:* {temp(9)}°, {status(3)}, {wind(3)} м/с
*{timings(4)}.00:* {temp(10)}°, {status(4)}, {wind(4)} м/с
*{timings(5)}.00:* {temp(11)}°, {status(5)}, {wind(5)} м/с
*{timings(6)}.00:* {temp(12)}°, {status(6)}, {wind(6)} м/с
*{timings(7)}.00:* {temp(13)}°, {status(7)}, {wind(7)} м/с""", reply_markup=markup, parse_mode="Markdown")

                    print(f"{timeNow}) {num + 1} - {id} получил сообщение")
                    num = num + 1
                    time.sleep(1)
            except telebot.apihelper.ApiTelegramException:
                print(f"{id} заблочил бота")
                time.sleep(1)
                num = num + 1
            except AttributeError:
                print(f"Не получилось спарсить инфу для {num + 1}")
                time.sleep(1)
            except IndexError:
                timeNow = 0
                num = 0
                a = False
            except Exception as ex:
                print(f"Произошла ошибка {ex} --- для пользователя {id}")
                time.sleep(1)
                num = num + 1
        print("Рассылка окончена\n\n")
        time.sleep(60)

if __name__ == '__main__':
    bot.infinity_polling()
