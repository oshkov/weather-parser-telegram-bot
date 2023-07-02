# Погодный телеграм-бот

Бот использует парсер, который собирает информацию с сайта [Gismeteo.ru](https://www.gismeteo.ru/)

### Возможности
- Возможность выбрать любой город
- После выбора города, он привязывается к вашему аккаунту
- Возможность узнать погоду сейчас, на сегодня, на завтра и на 10 дней вперед
- Уведомление о погоде на день в 7.00 и на завтра в 21.00
- Возможность включить и выключить уведомления от бота
- Возможность узнать сколько людей и кто именно пользуется ботом

### Используемые библиотеки
- pyTelegramBotAPI - библиотека для создания тг-ботов
- requests и BeautifulSoup4 - используется для парсинга
- sqlite3 - база данных
- fake_useragent - библиотека для создания фэйкового юзер-агента

### В БД можно узнать:
- Когда пользователь включил бота
- Id пользователя
- Username пользователя
- Имя пользователя
- Фамилию пользователя
- Город, выбранный пользователем
- Ссылку на выбранный город
- Вкл/выкл уведомления для пользователя
- Последний запрос пользователя

### Команды
| Команда | Действие |
| ------ | ------ |
| /start | Запуск/перезапуск бота
| /weather | Узнать погоду сейчас
| /about | Информация о боте
| /stats | Узнать статистику бота

### Пользование
Воспользоваться ботом можно по [ссылке](https://t.me/weathersupporttgbot)