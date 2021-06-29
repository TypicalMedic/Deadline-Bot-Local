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
from telebot import types  # кнопки

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
    strr += "\nОписание дедлайна: " + item["description"]
    strr += "\nДата дедлайна: " + item["expDate"]
    strr += "\nВремя дедлайна: " + item["alarmTime"]
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
@bot.message_handler(commands=['start'])        # вызов при командах старта или помощи
def start(message):
    bot.send_message(message.from_user.id, 'Здравствуйте, ' + message.from_user.first_name + '!')
    bot.send_message(message.from_user.id, 'Введите команду /menu для доступа к функциям бота')
# здесь описывается функция, которая будет вызываться при вызове данного обработчика, как входной параметр она принимает
# сообщение пользователя и его информацию


@bot.message_handler(commands=['menu'])
def send_greeting(message):
    global data                                         # глобализируем БД чтобы польоваться именно ею в функции
    openJson()                                          # обновляем БД
    user_name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)  # получаем имя пользователя
    # на всякий случай
    data = act.add_user(message.from_user.id, user_name, data)  # добавление пользователя, если он новый
    data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete'] = False  # снимаем флаг удаления
    data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
    # отправка обычно сообщения ботом, параметрами принимает id пользователя, которому он посылает сообщение
    # (в данном случае он отвечает тому, кто отправил сообщение) и само сообщение
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=2)  # создаём клавиатуру
    btn1 = types.KeyboardButton('Добавить дедлайн')
    btn2 = types.KeyboardButton('Закрыть дедлайн')
    btn3 = types.KeyboardButton('Посмотреть свои дедлайны')
    keyboard.add(btn1, btn2, btn3)  # добавляем кнопки
    msg = bot.send_message(message.from_user.id, 'Выберите необходимое действие:', reply_markup=keyboard)
    bot.register_next_step_handler(msg, user_answer)  # переходим в другую функцию для анализа ответа пользователя

    saveJson()    # соханяем изменения в БД


def user_answer(message):  # функция перехода от меню к другим функциям
    if message.text == "Добавить дедлайн":
        send_deadline_request(message)
    elif message.text == "Закрыть дедлайн":
        finish_deadline(message)
    elif message.text == "Посмотреть свои дедлайны":
        display_deadlines(message)
    else:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Вернуться в главное меню')
        keyboard.add(btn1)
        msg = bot.send_message(message.from_user.id, "К сожалению, бот не понимает, введённые вами данные!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, send_greeting)


def finish_deadline(message):
    global data
    openJson()
    count = 0                                           # создаем счетчик дедлайнов пользователя
    mes_beg = "Введите название дедлайна, который необходимо закрыть:\n"
    mes = ""
    for x in data["Deadlines"]:
        if x['userId'] == message.from_user.id:
            count += 1
            mes += "Дедлайн №" + str(count) + ": " + x['name'] + "\n"  # записываем дедлайны пользователя в сообщение
    if count == 0:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Вернуться в главное меню')
        keyboard.add(btn1)
        msg = bot.send_message(message.from_user.id, "Нет ни одного активного дедлайна! Закрытие невозможно!", reply_markup=keyboard)
        bot.register_next_step_handler(msg, send_greeting)
    else:
        mes_beg += mes
        data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete'] = True  # ставим флаг чтобы
        # пользователь ввел имя дедлайна для дальнейшей обработки (флаг именно этого пользователя)
        saveJson()
        bot.send_message(message.from_user.id, mes_beg)


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
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Вернуться в главное меню')
        keyboard.add(btn1)
        msg = bot.send_message(message.from_user.id, 'У Вас нет ни одного активного дедлайна!', reply_markup=keyboard)
        bot.send_photo(message.from_user.id,  # бот присылает фото
                       'https://64.media.tumblr.com/5a15661755365d8f5919f8c67e17be53/tumblr_nqik67QsUZ1uzt9pko1_500.gifv')
        bot.register_next_step_handler(msg, send_greeting)
    else:
        bot.send_message(message.from_user.id, mes)
        send_greeting(message)


def send_deadline_request(message):
    global data
    openJson()
    bot.send_message(message.from_user.id, "Введите информацию о дедлайне в виде одного сообщения следующим образом:"
                                           "\nНазвание дедлайна\nОписание (можно оставить пустым)\n"
                                           "Дата окончания (в формате дд.мм.гггг)\n"
                                           "Время оповещения (в формате чч:мм:сс)")
    data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = True  # ставим флаг чтобы пользователь
    # ввел данные о дедлайне и программа считала их
    saveJson()


def move_menu(message):  # функция перехода
    if message.text == 'Вернуться в главное меню':
        send_greeting(message)
    elif message.text == 'Добавить дедлайн заново':
        send_deadline_request(message)
    else:
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn1 = types.KeyboardButton('Вернуться в главное меню')
        keyboard.add(btn1)
        msg = bot.send_message(message.from_user.id, "К сожалению, бот не понимает введённые вами данные!",
                               reply_markup=keyboard)
        bot.register_next_step_handler(msg, send_greeting)


@bot.message_handler(content_types=['text'])          # вызов при вводе простого текста в т.ч. данных нужных для
def actions(message):
    global data
    openJson()
    # на всякий случай проверяем не новый ли это пользователь
    user_name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)
    data = act.add_user(message.from_user.id, user_name, data)
    saveJson()
    if data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline']:  # проверяем флаг добавления
        res = str(message.text).split("\n")  # разделяем сообщение на строки, чтобы каждую из них записать
        # как часть информации о дедлайне
        if len(res) == 4:  # проверяем, ввел ли пользователь нужное кол-во пунктов для заполнения
            is_unique = True  # переменна проверки уникальности имени дедлайна
            for x in data['Deadlines']:
                if x['name'] == res[0] and x['userId'] == message.from_user.id:
                    is_unique = False
                    break
            if is_unique:  # если у данного пользователя нет такого имени дедлайна продолжаем
                name = res[0]  # имя дедлайна должно быть в 1 строке
                desc = res[1]  # описание должно быть во 2 строке
                try:  # проверка корректности ввода даты/ времени (может вылести ошибка
                    # при парсировании строки)
                    final_date = datetime.strptime(res[2], "%d.%m.%Y")  # дата дедлайна должна быть в 3 строке
                    notification_time = datetime.strptime(res[3], "%H:%M:%S")  # время напоминания д. б. в 4 строке
                    if final_date.date() < datetime.now().date():  # проверяем не прошел ли дедлайн
                        bot.send_message(message.from_user.id, "Введённый Вами день уже прошёл! "
                                                               "Укажите актуальную дату (сегодня или позднее)")
                        data['UsersFlags'][str(message.from_user.id)][
                            'isAddingDeadline'] = False  # снимаем флаг добавления
                        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
                        btn1 = types.KeyboardButton('Вернуться в главное меню')
                        btn2 = types.KeyboardButton('Добавить дедлайн заново')
                        keyboard.add(btn1, btn2)
                        msg = bot.send_message(message.from_user.id, "Выберите необходимое действие:",
                                               reply_markup=keyboard)
                        bot.register_next_step_handler(msg, move_menu)
                    else:  # если все проверки пройдены, записываем в БД
                        id = 0  # id дедлайна
                        if len(data["Deadlines"]) != 0:
                            id = data["Deadlines"][-1]["id"] + 1  # для уникального id присваиваем id на 1 больше чем
                            # id последнего дедлайна в списке
                        # добавление дедлайна в БД ↓
                        data = act.add_deadline(id, name, message.from_user.id, desc, res[2], res[3], data)
                        # сообщение для записи в логи ↓
                        log = datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " user " + str(message.from_user.id) \
                              + " added deadline: " + name + "\n"
                        # запись успешного действия в лог ↓
                        write_logs(log)
                        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                        btn4 = types.KeyboardButton('Вернуться в главное меню')
                        keyboard1.add(btn4)
                        msg = bot.send_message(message.from_user.id, "Ваш дедлайн успешно добавлен!",
                                               reply_markup=keyboard1)
                        bot.register_next_step_handler(msg, send_greeting)
                except ValueError:  # ошибка при парсировании даты/ времени
                    bot.send_message(message.from_user.id,
                                     "Вы ввели некорректную дату или некорректное время!\n"
                                     "Необходимо ввести ровно 4 строки одним сообщением в правильном формате"
                                     "\nДобавьте, пожалуйста, дедлайн заново!")
                    data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
                    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
                    btn1 = types.KeyboardButton('Вернуться в главное меню')
                    btn2 = types.KeyboardButton('Добавить дедлайн заново')
                    keyboard.add(btn1, btn2)
                    msg = bot.send_message(message.from_user.id, "Выберите необходимое действие:",
                                           reply_markup=keyboard)
                    bot.register_next_step_handler(msg, move_menu)
            else:  # имя дедлайна не уникальное
                bot.send_message(message.from_user.id, "Дедлайн с таким названием уже существует!\nНеобходимо выбрать другое название!")
                data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
                keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
                btn1 = types.KeyboardButton('Вернуться в главное меню')
                btn2 = types.KeyboardButton('Добавить дедлайн заново')
                keyboard.add(btn1, btn2)
                msg = bot.send_message(message.from_user.id, "Выберите необходимое действие:",
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, move_menu)
        elif len(res) < 4:  # количество строк не соответсвует требуемому
            bot.send_message(message.from_user.id,
                             "Вы ввели недостаточное количество строк (" + str(len(res)) + " из 4)!\n"
                             "Необходимо ввести ровно 4 строки одним сообщением в правильном формате"
                             "\nДобавьте, пожалуйста, дедлайн заново!")
            data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
            btn1 = types.KeyboardButton('Вернуться в главное меню')
            btn2 = types.KeyboardButton('Добавить дедлайн заново')
            keyboard.add(btn1, btn2)
            msg = bot.send_message(message.from_user.id, "Выберите необходимое действие:",
                                   reply_markup=keyboard)
            bot.register_next_step_handler(msg, move_menu)
        else:  # количество строк не соответсвует требуемому
            bot.send_message(message.from_user.id,
                             "Вы ввели избыточное количество строк (" + str(len(res)) + " из 4)!\n"
                             "Необходимо ввести ровно 4 строки одним сообщением в правильном формате"
                             "\nДобавьте, пожалуйста, дедлайн заново!")
            data['UsersFlags'][str(message.from_user.id)]['isAddingDeadline'] = False  # снимаем флаг добавления
            keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
            btn1 = types.KeyboardButton('Вернуться в главное меню')
            btn2 = types.KeyboardButton('Добавить дедлайн заново')
            keyboard.add(btn1, btn2)
            msg = bot.send_message(message.from_user.id, "Выберите необходимое действие:",
                                   reply_markup=keyboard)
            bot.register_next_step_handler(msg, move_menu)
        saveJson()
    elif data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete']:  # проверяем флаг завершения
        mes, data = act.delete_deadline(message.text, data, message.from_user.id)  # вызываем удаление дедлайна из БД, получаем сообщение
        # успеха/ провала удаления дедлайна с данным именем
        bot.send_message(message.from_user.id, mes)  # уведомляем пользователя об успехе/ провале операции
        if mes == 'Дедлайн успешно завершен!':
            bot.send_photo(message.from_user.id,
                           'https://sun9-86.userapi.com/impg/AuXuHJcyKfKes-5FMsBpw-Ouzb-2PfDoBIRcVQ/HptccRO45A8.jpg?size=225x225&quality=96&sign=5646e2a1472fb4a35d29d9ed3286cc5b&type=album')
        data['UsersFlags'][str(message.from_user.id)]['choosingWhatToDelete'] = False  # снимаем флаг удаления
        saveJson()
        send_greeting(message)
    else:  # если ввели не команду и флагов не стояло
        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        btn4 = types.KeyboardButton('Вернуться в главное меню')
        keyboard1.add(btn4)
        msg = bot.send_message(message.from_user.id, "К сожалению, бот не понимает введённые вами данные!", reply_markup=keyboard1)
        bot.register_next_step_handler(msg, send_greeting)
    saveJson()


bot.polling(none_stop=True)  # запускам бота, в данном случае он работает без перерывов, обязательно писать это в конце
# т.к. по сути запускается бесконечный цикл в ожидании команд пользователей