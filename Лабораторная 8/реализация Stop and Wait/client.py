"""
Здесь представлен код клиента, который должен отправить на сервер файл (в нашем случае - просто строку file),
разбитый на несколько пакетов. Отправка пакетов производится по схеме, представленной в условии задачи; то есть
клиент работает как конечный автомат, отправляя эти пакеты. Для написания конечного автомата, я использовал
библиотеку transitions, хотя здесь можно было бы и без неё обойтись, храня в одной переменной текущее состояние
автомата (то есть клиента).
"""

import socket
import random
from transitions import Machine  # библиотека для написания конечного автомата (используем схему из условия задания)


server_ip = "127.0.0.1"  # адрес и порт, где будет работать наш udp-сервер
server_port = 20001
timeout = 2  # таймаут (в секундах) на получение подтверждение о том, что сервер получил пакет
part_size = 10  # размер пакета (в символах)
file = """Реализуйте свой протокол надежной передачи данных типа Stop and Wait на основе ненадежного
транспортного протокола UDP. В вашем протоколе, реализованном на прикладном уровне,
отправитель отправляет пакет (frame) с данными, а затем ожидает подтверждения перед
продолжением."""  # файл (просто текст), который отправляем
packages = [file[i:i+part_size] for i in range(0, len(file), part_size)]  # делим на пакеты
n = len(packages)  # количетсво пакетов
client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class Host:  # объект класса с состояниями (в него будут состояния конечного автомата встроены)
    pass


def lose_package(lost=0.3):  # с вероятностью lost (по умолчанию 30%) считаем, что пакет потерялся
    if random.uniform(0, 1) <= lost:
        return True
    else:
        return False


def get_data(socket_connection, timelimit=1):  # функция получения данных от собеседника
    data = ""
    ip = None
    socket_connection.settimeout(timelimit)  # изначально устанавливаем лимит по времени тот, который нам передали
    # - это будет лимит, в течении которого мы будем ждать первый куска данных
    while True:
        try:
            data_slice, ip = socket_connection.recvfrom(1024)  # считываем 1024 байт данных и ip отправителя
            socket_connection.settimeout(0.3)  # дальше куски данных будем ждать <=0.3 сек
        except socket.timeout:
            data_slice = None
        if data_slice:
            data += data_slice.decode("utf-8")
        else:
            break

    # на данной строчке ip может быть None только, если мы не дождались даже первого куска данных (на получение
    # которого у нас был переданный в функцию timelimit) - то есть произошёл тайм аут (в рамках нашей лабораторной
    # это значит, что данные просто потерялись по пути в сети); также с помощью функции lose_package() в данной
    # лабораторной мы моделируем потерю пакета -> так что если lose_package() = True - это значит, что мы считаем, что
    # произошла потеря данных (вне зависимости от того, произошла ли реальная потеря даннхы (то есть ip=None) или нет).

    # Короче говоря, если произошла потеря данных (реальная (ip=None) или смоделированная нами (lose_package=True)),
    # мы возвращаем None из функции (в коде этот None будет интерпретироваться к тайм аут, так как в реальности
    # если данные теряются, то происходит тайм аут); иначе вовзращаем полученные данные.:
    if ip is not None and not lose_package():
        return data, ip
    else:
        return None, None


client = Host()

# Полный список состояний конечного автомата - просто берем 4 состояния со схемы в условии задания
# (wait_call_... - состояние, в котором ждётся вызов; wait_ack... - ожидание ack-пакета)
states = ['wait_call_0', 'wait_call_1', 'wait_ack_0', 'wait_ack_1']

# Добавляем таблицу переходов — из какое в какое состояние мы можем попасть
# trigger - название перехода (событие, которое вызывает этот переход); source и dest - откуда и куда переход
transitions = [
    {'trigger': 'receive_ok_ACK', 'source': 'wait_ack_0', 'dest': 'wait_call_1'},  # получичли верный ack-пакет
    {'trigger': 'receive_ok_ACK', 'source': 'wait_ack_1', 'dest': 'wait_call_0'},

    {'trigger': 'receive_bad_ACK', 'source': 'wait_ack_0', 'dest': 'wait_ack_0'},  # получили неправильный ack-пакет
    {'trigger': 'receive_bad_ACK', 'source': 'wait_ack_1', 'dest': 'wait_ack_1'},

    {'trigger': 'timeout', 'source': 'wait_ack_0', 'dest': 'wait_ack_0'},  # таймаут на получение ack-пакета
    {'trigger': 'timeout', 'source': 'wait_ack_1', 'dest': 'wait_ack_1'},

    {'trigger': 'send', 'source': 'wait_call_0', 'dest': 'wait_ack_0'},  # отправили ack-пакет
    {'trigger': 'send', 'source': 'wait_call_1', 'dest': 'wait_ack_1'},

    {'trigger': 'receive', 'source': 'wait_call_0', 'dest': 'wait_call_0'},  # просто получили пакет (не используется,
    {'trigger': 'receive', 'source': 'wait_call_1', 'dest': 'wait_call_1'}  # так как этот код только для односторонней
    # передачи файла - с клиента на сервер)
]

# Инициализация машины (конечного автомата) -> весь автомат создаётся на client - образце класса Host
machine = Machine(client, states=states, transitions=transitions, initial='wait_call_0')


# Итак, далее наш клинет, код которого сейчас пишется, должен передать на сервер n пакетов (вместе они
# состоавляют file) -> делать мы это будем в цикле далее:

next_pack = 0  # номер пакета, который нужно передать
try:
    while True:
        if next_pack == n:  # если передали все пакеты, выходим из цикла
            break
        print("Клиент в состоянии: {}".format(client.state))

        if client.state == 'wait_call_0':
            snd_packet = ('0' + packages[next_pack]).encode('utf-8')  # создаём пакет, который будем передавать
            # (в начало пакета добавляем его номер - их всегт два: 0 или 1)
            client_udp_socket.sendto(snd_packet, (server_ip, server_port))
            print("--- Отправлено сообщение: ", snd_packet.decode('utf-8'))
            client.trigger('send')  # итак, пакет отправили -> переходм в следующее состояние конечного автомата
            continue

        if client.state == 'wait_call_1':  # аналогично, но в этом состоянии передаём пакет с номером 1
            snd_packet = ('1' + packages[next_pack]).encode('utf-8')
            client_udp_socket.sendto(snd_packet, (server_ip, server_port))
            print("--- Отправлено сообщение: ", snd_packet.decode('utf-8'))
            client.trigger('send')
            continue

        if client.state == 'wait_ack_0':  # в этом состоянии ждём подтверждение, что сервер получил пакет 0
            receive_data, receive_ip = get_data(client_udp_socket, timelimit=timeout)  # пытаемся получить подтверждение
            if receive_ip is None:  # это значт, что пакет с номером 0, который мы отправляли, скорее всего
                # потерялся (так как произошёл тайм аут - то есть истекло время на получение пакета-подтверждения) ->
                # в этом случае повторно отправляем пакет:
                snd_packet = ('0' + packages[next_pack]).encode('utf-8')
                client_udp_socket.sendto(snd_packet, (server_ip, server_port))
                print("------ ПОВТОРНО отправлено сообщение: ", snd_packet.decode('utf-8'))
                client.trigger('timeout')
                continue
            elif receive_data != "ACK0":  # это значт, что нам пришёл некорректное подтверждение -> прсото ждём дальше
                client.trigger('receive_bad_ACK')
                continue
            else:  # иначе - нам пришло корректное подтверждение -> мы уверены, что пакет 0 доставлен ->
                next_pack += 1  # -> будем отправлять новый пакет
                client.trigger('receive_ok_ACK')
                continue

        if client.state == 'wait_ack_1':  # аналогично для подтверждения пакета с номером 1
            receive_data, receive_ip = get_data(client_udp_socket, timelimit=timeout)
            if receive_ip is None:
                snd_packet = ('1' + packages[next_pack]).encode('utf-8')
                client_udp_socket.sendto(snd_packet, (server_ip, server_port))
                print("------ ПОВТОРНО отправлено сообщение: ", snd_packet.decode('utf-8'))
                client.trigger('timeout')
                continue
            elif receive_data != "ACK1":
                client.trigger('receive_bad_ACK')
                continue
            else:
                next_pack += 1
                client.trigger('receive_ok_ACK')
                continue
finally:
    client_udp_socket.close()
