import socket
import sys

ip = "127.0.0.1"  # ip-адрес по умолчанию
start = 0  # по умолчанию просматриваем все порты
finish = 65535

if len(sys.argv) == 4:  # считываем ip и границы, где искать свободные порты из командной строки
    _, ip, start, finish = sys.argv
    start = int(start)
    finish = int(finish)

free_ports = []
for port in range(start, finish + 1):
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serv.bind((ip, port))  # пытаемся подключиться
        free_ports.append(port)  # удаётся -> добавляем в массив
    except OSError:
        pass
    serv.close()

print("Свободные (доступные) номера портов в дипазоне от {} до {} для ip: {}:".format(start, finish, ip))
print(free_ports)
