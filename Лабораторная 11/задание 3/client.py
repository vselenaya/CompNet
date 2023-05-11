import socket

# адрес сервера указываем, к нему подключаемся
HOST = "::1"
PORT = 12345
msg = "Привет! Как дела?"  # сообщение, отправляемое на сервер


# получаем данные от сервера (timelimit побольше, чем на сервере, чтрбы он успел ответить)
def get_data(socket_connection, timelimit=2):
    data = ""
    socket_connection.settimeout(timelimit)
    while True:
        try:
            data_slice = socket_connection.recv(1024)
        except socket.timeout:
            data_slice = None
        if data_slice:
            data += data_slice.decode("utf-8")
        else:
            break
    return data


with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:  # socket.AF_INET6 - используем IPv6!
    sock.connect((HOST, PORT))
    sock.sendall(msg.encode("utf-8"))
    answer = get_data(sock)
    print("Ответ от сервера: {}".format(answer))
