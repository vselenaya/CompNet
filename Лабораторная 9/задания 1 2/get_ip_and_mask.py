import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # создаём UDP-сокет

sock.connect(('128.119.245.12', 64000))  # пытаемся подключиться куда-нибудь
ip = sock.getsockname()[0]  # получаем наш ip
sock.close()


print("ip-адрес: {}".format(ip))
# что такое маска и как ее получить - я не понял...
