import socket
import struct
import sys
import time

HOST = "gaia.cs.umass.edu"  # сервер, куда посылать будем запрос
PORT = 1  # номер порта сервера - пусть 1...
num_packets = 5  # количество icmp-пакетов, которые будем посылать


# функция из библиотеки Pyping (пришлось её немного доработать - убрать ord, так как элемент байтовой строки
# автоматически в число переводится, ord не нужен...) для вычисления контрольной суммы:
def calculate_checksum(source_string):
    count_to = (int(len(source_string) / 2)) * 2
    sum_ = 0
    count = 0

    # Handle bytes in pairs (decoding as short ints)
    lo_byte = 0
    hi_byte = 0
    while count < count_to:
        if sys.byteorder == "little":
            lo_byte = source_string[count]
            hi_byte = source_string[count + 1]
        else:
            lo_byte = source_string[count + 1]
            hi_byte = source_string[count]
        sum_ = sum_ + (hi_byte * 256 + lo_byte)
        count += 2

    # Handle last byte if applicable (odd-number of bytes)
    # Endianness should be irrelevant in this case
    if count_to < len(source_string):  # Check for odd length
        lo_byte = source_string[len(source_string) - 1]
        sum_ += lo_byte

    sum_ &= 0xffffffff  # Truncate sum to 32 bits (a variance from ping.c, which
    #                     uses signed ints, but overflow is unlikely in ping)

    sum_ = (sum_ >> 16) + (sum_ & 0xffff)  # Add high 16 bits to low 16 bits
    sum_ += (sum_ >> 16)				   # Add carry from above (if any)
    answer = ~sum_ & 0xffff				# Invert and truncate to 16 bits
    answer = socket.htons(answer)

    return answer


def gen_message(identifier, seq_num):
    icmp_echo = 8  # тип ICMP сообщения для эхо-запроса
    icmp_code = 0  # код ICMP сообщения
    checksum = 0  # изначально контрольную сумму стоавим 0
    header = struct.pack(
        "!BBHHH", icmp_echo, icmp_code, checksum, identifier, seq_num
    )  # собираем заголовок для ICMP пакета, где поле контрольной суммы 0

    checksum = calculate_checksum(header)  # считаем контрольную сумму (от только заголовка, полезной нагрузки нет)
    header = struct.pack(
        "!BBHHH", icmp_echo, icmp_code, checksum, identifier, seq_num
    )  # собираем заголовок для ICMP пакета с правильной контрольной суммой

    packet = header  # пакет, который отправляем будет состоять только из загловка - полезной нагрузки у нас не будет!
    return packet


# получаем данные от сервера (timelimit побольше, чем на сервере, чтрбы он успел ответить)
def get_answer(socket_connection, timelimit=2):
    socket_connection.settimeout(timelimit)
    try:
        data = socket_connection.recv(1024)
    except socket.timeout:
        data = None
    return data


arr_RTT = []
lost = 0

# создаём ICMP сокет:
with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
    for i in range(num_packets):
        # пусть именно такие идентификатор и номер последовательности будем использовать:
        identifier, sequence_number = i + 1, i + 1
        icmp_packet = gen_message(identifier, sequence_number)  # создали пакет

        print("Пакет номер {} отправлен".format(i + 1))
        start_time = time.time()
        sock.sendto(icmp_packet, (HOST, PORT))  # отправляем пакет
        answer = get_answer(sock, timelimit=1)  # ждём ответ не дольше 1 секунды
        RTT = time.time() - start_time  # время от отправления ззапроса до прихода ответа

        if answer is None:
            lost += 1  # пакет потерян
            _ = get_answer(sock, 8)  # ждём еще 8 секунд
            print("Пакет потерян...")
            print("Потеряно: {}% пакетов".format(lost / (i+1) * 100))
        else:
            ans_header = answer[20:28]  # icmp заголовок пакета берём
            ans_type, ans_code, ans_checksum, ans_id, ans_seq_num = struct.unpack('!BBHHH', ans_header)

            if ans_type == 3:
                print("Ошибка!")
                if ans_code == 0:
                    print("Сеть недостижима!")
                elif ans_code == 1:
                    print("Получаетель недостижим")
            else:
                # проверяем, что дошёл правильный ответ на посланный пакет:
                assert (ans_type == 0) and (ans_code == 0) and (ans_id == identifier) and (ans_seq_num == sequence_number)

            arr_RTT.append(RTT)
            print("Ответ от сервера {} получен за {} секунд.".format(HOST, RTT))
            print("Минимальное RTT = {}, максимально: {}, среднее: {}".format(min(arr_RTT),
                                                                              max(arr_RTT),
                                                                              sum(arr_RTT) / len(arr_RTT)))
            print("Потеряно: {}% пакетов".format(lost / (i + 1) * 100))
        print()

        time.sleep(1)  # ждём секунду перед отправкой другого пакета
