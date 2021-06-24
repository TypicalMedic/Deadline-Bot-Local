# реализация бота для уведомления о дедлайнах в телеграм
# на данном этапе есть возможность добавить, завершить (удалить) и просмотреть дедлайны пользоватля
# бот реализован с помощью библиотеки TelegramBotAPI для создания навигации использовались команды для бота
# и база флагов, индивидуальных для каждого пользователя, записанных в БД
# БД реализована в виде JSON файла, на данном этапе в ней содержатася дедлайны всех пользователей, список пользователей,
# флаги пользователей для ассинхронной навигации в меню бота
# работа с БД по большей части осуществляется через объект database_editing1
# присутсвует также наипростейшая система логов для отслеживания работы бота

# импорт библиотек
import telebot  # API телеграм бота
from datetime import datetime  # дата время для записи дат и времен
import json  # библиотека для работы с БД файлом
import database_editing1 as act  # класс для изменения БД


# функции
# запись лога в файл
def write_logs(mes):
    with open("Logs.txt", 'a', encoding='utf-8') as logs:
        logs.writelines(mes + "\n")


# сохранение изменений БД в файл
def saveJson():
    with open('Database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# открытие файла БД и загрузка его в словарь data
def openJson():
    global data
    with open('Database.json', 'r', encoding='utf-8') as openfile:
        json_object = json.load(openfile)
    data = dict(json_object)


# строка информации о некотором дедлайне
def get_deadline_info(item):
    strr = item["name"]
    strr += "\nОписание: " + item["description"]
    strr += "\nКОГДА ДЕДЛАЙН: " + item["expDate"]
    strr += "\nКогда тебя тормошить: в " + item["alarmTime"]
    return strr


# подключаемся к нашему боту
bot = telebot.TeleBot('1724637364:AAEPqLLPkSfd788vqvneH_dusnBVL5pd2mM')

# первичная загрузка БД в переменную data
with open('Database.json', 'r', encoding='utf-8') as openfile:
    json_object = json.load(openfile)
data = dict(json_object)


# работа с ботом
# обработка различных видов сообщений

# ***************************   ПРО @bot.message_handler()   ***************************************
# данная команда вызывает обработчик телеграм сообщений
# в списке параметров указывается при каких условиях вызывается именно данный обработчик
# условия могут быть командами (в данном случае старт и помощь), типу сообщения (текст/ изображение/ стикер)
# или функция возвращающая булевую переменную
@bot.message_handler(commands=['start', 'help'])        # вызов при командах старта или помощи
# здесь описывается функция, которая будет вызываться при вызове данного обработчика, как входной параметр она принимает
# сообщение пользователя и его информацию
def send_greeting(message):
    global data                                         # глобализируем БД чтобы польоваться именно ею в функции
    openJson()                                          # обновляем БД
    user_name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)  # получаем имя пользователя
    # на всякий случай
    data = act.add_user(message.from_user.id, user_name, data)  # добавление пользователя, если он новый

    # отправка обычно сообщения ботом, параметрами принимает id пользователя, которому он посылает сообщение
    # (в данном случае он отвечает тому, кто отправил сообщение) и само сообщение
    bot.send_message(message.from_user.id, "Чо хочешь сделать?\n\n1./add_deadline - добавь дедлайн"
                                           "\n\n2./finish_deadline - закрыть дедлайн\n\n"
                                           "3./show_deadlines - чекни свои дедлайны\n\n"
                                           "Просто нажми на одну из команд!!")
    saveJson()                                          # соханяем изменения в БД


@bot.message_handler(commands=['finish_deadline'])      # вызов при команде завершения дедлайна
def finish_deadline(message):
    global data
    openJson()
    count = 0                                           # создаем счетчик дедлайнов пользователя
    mes_beg = "Какой дедлайн закрыл м?\nПросто введи его имя!\n"
    mes = ""
    for x in data["Deadlines"]:
        if x['userId'] == message.from_user.id:
            count += 1
            mes += "Дедлайн №" + str(count) + ": " + x['name'] + "\n"  # записываем дедлайны пользователя в сообщение
    if count == 0:
        bot.send_message(message.from_user.id, "А ДЕДЛАЙНОВ ТО НЕТУ!!")
    else:
        mes_beg += mes
        data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete'] = True  # ставим флаг чтобы
        # пользователь ввел имя дедлайна для дальнейшей обработки (флаг именно этого пользователя)
        saveJson()
        bot.send_message(message.from_user.id, mes_beg)


@bot.message_handler(commands=['show_deadlines'])       # вызов при команде отображения всех дедлайнов пользователя
def display_deadlines(message):
    global data
    openJson()
    count = 0
    mes = ""
    for x in data["Deadlines"]:
        if x['userId'] == message.from_user.id:
            count += 1
            mes += "Дедлайн №" + str(count) + "\n"
            mes += get_deadline_info(x) + "\n\n"
    if count == 0:
        bot.send_message(message.from_user.id, "УРА ДЕДЛАЙНОВ НЕТУ!!")
    else:
        bot.send_message(message.from_user.id, mes)


@bot.message_handler(commands=['add_deadline'])        # вызов при команде добавления дедлайна
def send_deadline_request(message):
    global data
    openJson()
    bot.send_message(message.from_user.id, "Введи информацию о дедлайне таким образом одним сообщением:"
                                           "\nНазвание дедлайна\nОписание (можно оставить пустым)\n"
                                           "Дата окончания дедлайна (в формате дд.мм.гггг)\n"
                                           "Время в которое тебя тормошить (в формате чч:мм:сс)")
    data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = True  # ставим флаг чтобы пользователь
    # ввел данные о дедлайне и программа считала их
    saveJson()


@bot.message_handler(content_types=['text'])          # вызов при вводе простого текста в т.ч. данных нужных для
# изменения БД
def actions(message):
    global data
    openJson()
    # на всякий случай проверяем не новый ли это пользователь
    user_name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)
    data = act.add_user(message.from_user.id, user_name, data)
    saveJson()
    if data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline']:  # проверяем флаг добавления
        res = str(message.text).split("\n")           # разделяем сообщение на строки, чтобы каждую из них записать
        # как часть информации о дедлайне
        if len(res) == 4:  # проверяем, ввел ли пользователь нужное кол-во пунктов для заполнения
            is_unique = True                          # переменна проверки уникальности имени дедлайна
            for x in data['Deadlines']:
                if x['name'] == res[0] and x['userId'] == message.from_user.id:
                    is_unique = False
                    break
            if is_unique:                             # если у данного пользователя нет такого имени дедлайна продолжаем
                name = res[0]                         # имя дедлайна должно быть в 1 строке
                desc = res[1]                         # описание должно быть во 2 строке
                try:                                  # проверка корректности ввода даты/ времени (может вылести ошибка
                    # при парсировании строки)
                    final_date = datetime.strptime(res[2], "%d.%m.%Y")  # дата дедлайна должна быть в 3 строке
                    notification_time = datetime.strptime(res[3], "%H:%M:%S")  # время напоминания д. б. в 4 строке
                    if final_date.date() < datetime.now().date():       # проверяем не прошел ли дедлайн
                        bot.send_message(message.from_user.id, "А дедлайн то уже прошел! "
                                                               "Введи дату не раньше завтра!")
                    else:                             # если все проверки пройдены, записываем в БД
                        id = 0                        # id дедлайна
                        if len(data["Deadlines"]) != 0:
                            id = data["Deadlines"][-1]["id"] + 1  # для уникального id присваиваем id на 1 больше чем
                            # id последнего дедлайна в списке
                        # добавление дедлайна в БД ↓
                        data = act.add_deadline(id, name, message.from_user.id, desc, res[2], res[3], data)
                        bot.send_message(message.from_user.id, "Все деделайн добавился!")
                        # сообщение для записи в логи ↓
                        log = datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " user " + str(message.from_user.id) \
                              + " added deadline: " + name + "\n"
                        # запись успешного действия в лог ↓
                        write_logs(log)
                except ValueError:                    # ошибка при парсировании даты/ времени 
                    bot.send_message(message.from_user.id,
                                     "Ты чета не то ввел!\n"
                                     "Ровно 4 строки одним сообщением в правильном формате плз!"
                                     "\nДавай добавляй заново!")
            else:                                     # имя дедлайна не уникальное
                bot.send_message(message.from_user.id, "Дедлайн с таким именем уже есть! Давай другое!")
        else:                                         # количество строк не соответсвует требуемому
            bot.send_message(message.from_user.id,
                             "Ты чета не то ввел!\nРовно 4 строки одним сообщением в правильном формате плз!\n"
                             "Давай добавляй заново!")
        data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
        saveJson()
    elif data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete']:  # проверяем флаг завершения
        mes, data = act.delete_deadline(message.text, data)  # вызываем удаление дедлайна из БД, получаем сообщение 
        # успеха/ провала удаления дедлайна с данным именем
        bot.send_message(message.from_user.id, mes)          # уведомляем пользователя об успехе/ провале операции
        data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete'] = False  # снимаем флаг удаления
        saveJson()
    else:                                             # если ввели не команду и флагов не стояло
        bot.send_message(message.from_user.id, "Скажи команду!\nЕсли забыл напиши /start или /help !")
    saveJson()


bot.polling(none_stop=True)  # запускам бота, в данном случае он работает без перерывов, обязательно писать это в конце
# т.к. по сути запускается бесконечный цикл в ожидании команд пользователей
