import socket
import time

server_ip = "127.0.0.1"  # данные для подключния к серверу
server_port = 20001
messages = ["Ping {} ".format(i+1) for i in range(10)]  # сообщения, которые ему отправим

client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_data(socket_connection, timelimit=2):  # получаем ответ от сервера, не более timelimit секунд ждём данные
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


try:
    for m in messages:
        start_time = time.time()  # засекаем время отправки сообщения
        # отправляем сообщение на сервер (добавляем к нему время отправки сообщения):
        client_udp_socket.sendto((m + str(start_time)).encode("utf-8"), (server_ip, server_port))
        print("----сообщение на сервер отправлено----")
        response, resp_ip = get_data(client_udp_socket)  # получаем ответ от сервера

        RTT = time.time() - start_time  # после получения ответа от сервера - считаем RTT
        if resp_ip is None:
            print("Request timed out", end="\n\n")
        else:
            print("Ответ от сервера: " + response)
            print("RTT: {}".format(RTT), end="\n\n")

finally:
    client_udp_socket.close()
