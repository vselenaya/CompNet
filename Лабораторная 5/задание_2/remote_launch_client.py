import socket

HOST = "127.0.0.1"
PORT = 12345

print("Введите команду, которую хотите выполнить на сервере:")
command = input()
if command == "":
    command = "ls"  # дефолтная команда (или dir - аналог ls в windows)


def get_data(socket_connection, timelimit=15):  # здесь timelimit побольше, чтобы команда на сервере успела выполниться
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


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(command.encode("utf-8"))
    answer = get_data(sock)
    print(answer)
