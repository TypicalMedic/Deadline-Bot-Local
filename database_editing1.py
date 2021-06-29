# код работы с БД
# суть заключается изменении data полученной из внешнего кода здесь и запись в файл уже в коде извне
import json
from datetime import datetime  # для доступа к дате и времени сейчас
import datetime as delta  # для доступа к переменной delta time


# запись в лог
def write_logs(mes):
    with open("Logs.txt", 'a', encoding='utf-8') as logs:
        logs.writelines(mes + "\n")


# удаление дедлайна под именем name, принимает также data из внешнего кода
def delete_deadline(name, data, user_id):
    count = 0  # счетчик для имитации цикла for с индексами, требуется для pop
    mes = ""  # сообщение об исходе операции
    found = False  # найден ли дедлайн с данным именем
    for x in data['Deadlines']:
        if x['name'] == name and x['userId'] == user_id:
            item = data['Deadlines'].pop(count)  # достаем дедлайн из словаря, тем самым красиво удаляя его
            found = True
            break
        count += 1
    if found:
        mes = 'Дедлайн успешно завершен!'
        # лог об успешном удалении
        log = datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " user " + str(item['userId']) + " deleted deadline: " \
              + name + "\n"
        write_logs(log)
    else:  # если дедлайн не найден
        mes = "Введённого Вами дедлайна не существует!"
    # записываем данные в файл на всякий пожарный
    with open('Database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return mes, data


# удаление просроченного дедлайна
def delete_exp_deadline(name, data, user_id):
    # суть работы такая же как в обычном удалении
    count = 0
    for x in data['Deadlines']:
        if x['name'] == name and x['userId'] == user_id:
            data['Deadlines'].pop(count)
            break
        count += 1
    with open('Database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data


# добавление дедлайна, аргументами принимает id дедлайна, имя, id пользователя, описание, дату окончания,
# время уведомления, саму БД
def add_deadline(id, name, userId, description, expDate, alarmTime, data):
    notific = datetime.now().strftime("%d.%m.%Y")  # ставим дату, когда бот в след. раз уведомит пользователя (сегодня)
    if datetime.now().time() > datetime.strptime(alarmTime, "%H:%M:%S").time():  # если время уведомления сегодня уже
        # прошло, то следующее уведомление переносится на завтра
        notific = (datetime.now() + delta.timedelta(days=1)).strftime("%d.%m.%Y")
    # добавляем запись в словарь
    data['Deadlines'].append(
        {
            "id": id,
            "name": name,
            "userId": userId,
            "description": description,
            "expDate": expDate,
            "alarmTime": alarmTime,
            "lastNotificationDate": notific
        }
    )
    return data


# добавление пользователя, принимает id пользователя, его имя в телеграмме (зачем оно вообще хз) и БД
def add_user(id, name, data):
    isok = True                        # новый ли пользователь
    for x in data["Users"]:
        if x["id"] == id:              # проверяем есть ли пользователь в БД
            isok = False
    if isok:
        data["Users"].append(
            {
                "id": id,
                "name": name
            }
        )
        # добавляем список флагов для пользователя
        data["UsersFlags"][str(id)] = {
            "isAddingDeadline": False,
            "choosingWhatToDelete": False
        }
        log = datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " user " + str(id) + " is added. Name: " + name + "\n"
        write_logs(log)
        with open('Database.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    return data
