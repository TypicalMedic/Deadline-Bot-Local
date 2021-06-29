# программа, проверябщая и высылающая уведомления
# в бесконечном цикле постоянно проверяются дедлайны из БД (с постоянным обновлением) и при нужных услвиях высылаются
# уведомления
import telebot
import database_editing1 as Act         # для работы с БД
import datetime as timeAmout            # для delta time
from datetime import datetime as time   # для даты/ времени сейчас
import json

# первичная запись БД в словарь
with open('Database.json', 'r', encoding='utf-8') as openfile:
    json_object = json.load(openfile)
data = dict(json_object)


# функция сохранения в файл JSON
def saveJson():
    with open('Database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# функция открытия файла
def openJson():
    global data  # объявляем data глобальной чтобы записать изменения именно во внешнюю переменную
    with open('Database.json', 'r', encoding='utf-8') as openfile:
        json_object = json.load(openfile)
    data = dict(json_object)


# бесконечный цикл
while True:
    try:                            # попытка открытия БД (постоянное обновление)
        openJson()
    except:                         # ошибка возникает, когда в БД вносятся изменения извне
        print("Обновление БД...")
        continue
    for x in data["Deadlines"]:     # перебор дедлайнов
        # если сегодня окончание дедлайна, то в 12:00:00 пользователю приходит соответствующее сообщение ↓
        if time.now().strftime("%d.%m.%Y") == x["expDate"] and time.now().strftime("%H:%M:%S") == "12:00:00":
            # подключаемся к боту
            bot = telebot.TeleBot('1724637364:AAEPqLLPkSfd788vqvneH_dusnBVL5pd2mM')
            mes = bot.send_message(x["userId"], "Важная информация! Ваш дедлайн " + x["name"] + " закончится уже сегодня!")
            photo = bot.send_photo(x["userId"], 'https://sun9-36.userapi.com/impg/5B8eU5DkgZ9x9GFXAVMBliFeFmooFbLKZ_XTAw/b8mT-MN9BmY.jpg?size=564x1003&quality=96&sign=bcc7c174c76e3d6afcc651c94b31a047&type=album')
            assert mes  # высылаем сообщение единоразово
            assert photo  # высылаем фото единоразово
        # если сегодня почти закончилось (23:00:00) и дедлайн заканчивается сегодня, то он удаляется и пользователю
        # приходит сообщение о закрытии дедлайна ↓
        elif time.now().strftime("%d.%m.%Y") == x["expDate"] and time.now().strftime("%H:%M:%S") == "23:00:00":
            bot = telebot.TeleBot('1724637364:AAEPqLLPkSfd788vqvneH_dusnBVL5pd2mM')
            mes = bot.send_message(x["userId"], "Ваш дедлайн " + x["name"] + " сегодня истекает!")
            photo = bot.send_photo(x["userId"],
                                   'https://sun9-69.userapi.com/impg/FAErur2_mf4gWCXMaI2dD7-4LX_pU1ul8UrKMw/lMjcxZXNmVw.jpg?size=236x314&quality=96&sign=0480974c88a6d380830a9e4a3c3055ec&type=album')
            data = Act.delete_exp_deadline(x["name"], data, x['userId'])  # удаление дедлайна
            assert mes
            assert photo
        # если предыдущие условия не выполняются, настало время уведомления и уведомление еще не было отправлено сегодня
        # то в указанное пользователем время ему приходит соответствующее сообщение ↓
        if time.now().strftime("%H:%M:%S") == x["alarmTime"] and\
                time.now().strftime("%d.%m.%Y") == x["lastNotificationDate"]:
            bot = telebot.TeleBot('1724637364:AAEPqLLPkSfd788vqvneH_dusnBVL5pd2mM')
            mes = bot.send_message(x["userId"], "Напоминание! Ваш дедлайн \"" + x["name"] + "\" закончится " +
                                   x["expDate"] + " и он до сих пор не закрыт!")
            photo = bot.send_photo(x["userId"],
                                   'https://sun9-58.userapi.com/impg/mthQVqSl6zptzSw5AgINRIdm9HJgpCwukJq6kg/FWw26ay2Bx8.jpg?size=564x828&quality=96&sign=88af1f8efde93df5a800549d65a32fee&type=album')
            # смещаем дату следующего напоминания на завтра ↓
            x["lastNotificationDate"] = (time.now() + timeAmout.timedelta(days=1)).strftime("%d.%m.%Y")
            saveJson()
            assert mes
            assert photo
