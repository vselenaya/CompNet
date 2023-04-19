"""
Это код сервера, задача которого принять сообщение, передаваемое клиентом. Это сообщение разбито на несколько
пакетов, которые склеиваются здесь на сервере вместе и итоговое соощение хранится в переменной message. При получении
каждого пакета, сервер в ответ отправляет подтверждающий ack-пакет.

Как и клиент, сервер имитирует потерю 30% полученных пакетов функцией lose_package.
"""

import socket
import random

server_ip = "127.0.0.1"  # адрес и порт, где будет работать наш udp-сервер
server_port = 20001
timeout = 2

udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  # создаём udp-сокет
udp_server_socket.bind((server_ip, server_port))  # сервер ждёт клиентов
print("UDP-сервер ждёт клиента...", end="\n\n")


def lose_package(lost=0.3):  # с вероятностью lost (по умолчанию 30%) считаем, что пакет потерялся
    if random.uniform(0, 1) <= lost:
        return True
    else:
        return False


def get_data(socket_connection, timelimit=1):  # функция получения данных от клиента
    data = ""
    ip = None
    socket_connection.settimeout(timelimit)
    while True:
        try:
            data_slice, ip = socket_connection.recvfrom(1024)  # считываем 1024 байт и ip клиента
            socket_connection.settimeout(0.3)
        except socket.timeout:
            data_slice = None
        if data_slice:
            data += data_slice.decode("utf-8")
        else:
            break

    if ip is not None and not lose_package():
        return data, ip
    else:
        return None, None


message = ""  # здесь собираем сообщение, которое отправляем нам пакетами клиент
curr_num = 0  # номер (их всего два - 0 или 1; они чередуются от пакета к пакету) пакета, который  мы в данный момент
# ОЖИДАЕМ получить от клиента
try:
    while True:
        print("Текущее сообщение от клиента:\n{}\n\n".format(message))
        client_data, client_ip = get_data(udp_server_socket, timelimit=timeout)  # пытаемся получить сообщение

        if client_ip is None:  # если ничего не получили (тайм аут) -> просто продолжаем...
            continue
        else:  # иначе - получили пакет данных client_data от клиента с ip client_ip
            if client_data[0] == '0':  # если пакет начинается с 0 (то есть это пакет с номером 0)
                if curr_num == 0:  # проверяем, что мы ждём пакет с номером 0 ->
                    message += client_data[1:]  # -> если это так, то добавляем этот пакет ко всем полученным данным
                    # (заметим, что могла быть ситуация, что у нас был curr_num=1 - те мы ждал пакет с номером 1,
                    # но здесь нам пришёл пакет с номером 0 - такео могло быть, если предыдущее наше подтверждение о
                    # получении пакета 0 не долшло до клиента и он отправил нам пакет 0 повторно -> в этом случае
                    # нам не нужно добавлять (так как уже добавлии ранее) этот пакет ко всем полученным данным;)
                    curr_num = 1  # теперь ждём пакет с номером 1
                # в любом случае на получение пакета с номером 0, нам нужно ответить подтвеждающим пакетом ACK0 -
                # - который говорит отправителю, что пакет с номером 0 мы получили:
                udp_server_socket.sendto("ACK0".encode("utf-8"), client_ip)  # отправляем сообщение клиенту
            elif client_data[0] == '1':  # аналогично
                if curr_num == 1:
                    message += client_data[1:]
                    curr_num = 0
                udp_server_socket.sendto("ACK1".encode("utf-8"), client_ip)  # отправляем сообщение клиенту
finally:
    udp_server_socket.close()
