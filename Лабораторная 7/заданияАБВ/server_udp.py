import socket
import random

server_ip = "127.0.0.1"  # адрес и порт, где будет работать наш udp-сервер
server_port = 20001

udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)  # создаём udp-сокет
udp_server_socket.bind((server_ip, server_port))  # сервер ждёт клиентов
print("UDP-сервер ждёт клиента...", end="\n\n")


def get_data(socket_connection, timelimit=1):  # функция получения данных от клиента, ждём данные не более timelimit сек
    data = ""
    ip = None
    socket_connection.settimeout(timelimit)
    while True:
        try:
            data_slice, ip = socket_connection.recvfrom(1024)  # считываем 1024 байт и ip клиента
        except socket.timeout:
            data_slice = None
        if data_slice:
            data += data_slice.decode("utf-8")
        else:
            break
    return data, ip


def lose_package(lost=0.2):  # с вероятностью lost (по умолчанию 20%) считаем, что пакет потерялся
    if random.uniform(0, 1) <= lost:
        return True
    else:
        return False


try:
    while True:
        # черпаем данные из сокета (тк это udp, то для всех клиентов у нас один и тот же сокет - udp_server_socket)
        # (в tcp для общения с каждым клиентом был свой сокет):
        client_data, client_ip = get_data(udp_server_socket)
        print("Получили сообщение: {}\nот клиента с адресом: {}".format(client_data, client_ip))

        if client_ip is None:
            print()
            continue
        if lose_package():
            print("!!! Считаем, что пакет потерян...", end="\n\n")
            continue
        else:
            print()
            udp_server_socket.sendto(client_data.upper().encode("utf-8"), client_ip)  # отправляем сообщение клиенту
finally:
    udp_server_socket.close()
