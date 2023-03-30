import socket
import subprocess

HOST = "127.0.0.1"
PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)


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


while True:
    print("Ожидается подключение...")
    connection, client_address = sock.accept()
    print("... подключено")
    try:
        command = get_data(connection)  # получаем команду от клиента
        print("команда от клиента получена")

        # выполняем её:
        # shell=True - это мы как будто открываем командную строку и в ней выполняем команду command
        # stdout=subprocess.PIPE, stderr=subprocess.PIPE - это чтобы запомнить в result вывод и ошибки команды
        # timeout=10 - ограничение на время выполнения команды
        # encoding="cp866" - это кодировка в командной строке (у меня в windows кодировка оказалась 866 (узнать можно
        # через команду chcp) - её и используем; но можно и другие кодировки...)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                timeout=10, encoding="cp866")
        print("команда выполнена")

        connection.sendall(("Команда {} запущена и вывела:\n\n{}\n\n,\
        а в поток ошибок:\n\n{}\n\n".format(command, result.stdout, result.stderr)).encode("utf-8"))
        print()
    finally:  # на всякий случай, чтобы при любых ошибках закрывать соединение
        connection.close()
