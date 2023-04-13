import socket
import time

server_ip = "127.0.0.1"
server_port = 20001
messages = ["Ping {} ".format(i+1) for i in range(10)]

client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_data(socket_connection, timelimit=2):
    data = ""
    ip = None
    socket_connection.settimeout(timelimit)
    while True:
        try:
            data_slice, ip = socket_connection.recvfrom(1024)
        except socket.timeout:
            data_slice = None
        if data_slice:
            data += data_slice.decode("utf-8")
        else:
            break
    return data, ip


RTT = 0
MIN_RTT = 100000000
MAX_RTT = 0
lost = 0  # счётчик потерянных пакетов
send = 0  # чётчик отправленных пакетов
try:
    for m in messages:
        send += 1

        start_time = time.time()

        client_udp_socket.sendto((m + str(start_time)).encode("utf-8"), (server_ip, server_port))
        print("----сообщение на сервер отправлено----")
        response, resp_ip = get_data(client_udp_socket)

        RTT = time.time() - start_time
        if resp_ip is None:
            print("Request timed out", end="\n\n")
            lost += 1
        else:
            MIN_RTT = min(RTT, MIN_RTT)
            MAX_RTT = max(RTT, MAX_RTT)
            print("Ответ от сервера: " + response)
            print("   MIN_RTT: {}".format(MIN_RTT))
            print("   MAX_RTT: {}".format(MAX_RTT))
            print("   RTT: {}".format(RTT))
            print("Текущаяя доля потерянных пакетов: {}%".format(lost / send * 100), end="\n\n")

finally:
    print("================")
    print("Итоговая доля потеряннх пакетов: {}%".format(lost / send * 100))
    print("================")
    client_udp_socket.close()
