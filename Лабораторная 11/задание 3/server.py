import socket

# адрес, на котором работает сервер:
# (если для IPv4 существовал адрес 127.0.0.1 - так называемый localhost, который в Интернет не выходит, а является
# адресом компьютера, на котором запущен (поэтому клиент-серверные приложения с таким localhost работают только
# внутри компьютера (не выходя во внешнюю сеть), но при этом используеют все сетевые и траспортные протоколы,
# как если бы общение было по сети), то для IPv6 таким адресом является ::1 (длинная запись: 0:0:0:0:0:0:0:1))
HOST = "::1"  # localhost указываем - сервер внутри компьютера работает
PORT = 12345

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)  # socket.AF_INET6 - Ipv6 используем,
#                                                            socket.SOCK_STREAM - используем tcp
sock.bind((HOST, PORT))
sock.listen(1)


def get_data(socket_connection, timelimit=1):
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


while True:
    print("Ожидается подключение...")
    connection, client_address = sock.accept()
    print("... подключено")
    try:
        msg = get_data(connection)  # получаем сообщение от клиента
        print("Сообщение от клиента: {}".format(msg))
        connection.sendall((msg.upper()).encode("utf-8"))  # клиенту отправляем сообщение заглавными буквами
        print("Сообщение клиенту отправили")
        print()
    finally:  # на всякий случай, чтобы при любых ошибках закрывать соединение
        connection.close()
