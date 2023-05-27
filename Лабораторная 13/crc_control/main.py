from random import randint

G = "1001"  # порождающий многочлен
r = len(G) - 1  # длина crc


def xor_part(D_bit, G_bit):  # аналогично вычитанию в столбик, делаем xor в столбик битовых строк D_bit на G_bit
    while len(D_bit) >= len(G_bit):
        res = int(D_bit, 2) ^ int(G_bit + '0' * (len(D_bit) - len(G_bit)), 2)  # выполнили xor
        D_bit = bin(res)[2:]  # превратили в битовую строку
    return D_bit


def get_packet_and_crc(data_bytes):  # по байтовой строке получаем битовый пакет и его crc (циклический код)
    D = bin(int(bytes.hex(data_bytes), 16))[2:]  # превращаем в биты
    R = xor_part(D + '0' * r, G)  # вычисляем crc
    R = '0' * (r - len(R)) + R  # дополняем нулями до длины ровно r
    return D, R


def check_crc(data_bits, crc_code):  # проверяем, что данные data_bits (битовая строка) вмете с кодом crc_code
    #                                  корректны (для этого xor в столбик должен дать нулевой остаток)
    return int(xor_part(data_bits + crc_code, G), 2) == 0


def falsify_bits(data_bits):  # в битовой строке data_bits искажаем несколько бит случанм образом
    def inverse_bit(bit):
        if bit == "1":
            return "0"
        elif bit == "0":
            return "1"

    if randint(1, 100) <= 80:  # с вероятностью 0.8 ничего не искажаем
        return data_bits, False

    m = randint(1, 3)  # искажаем от 1 до 3 бит
    for _ in range(m):
        i = randint(0, len(data_bits) - 1)  # выбираем номер бита который исказим
        data_bits = data_bits[:i] + inverse_bit(data_bits[i]) + data_bits[i+1:]  # инвертируем i-ый бит

    return data_bits, True


# ТЕСТИРОВАНИЕ
test1, crc1 = get_packet_and_crc("Привет! Как дела?".encode('utf-8'))
test2, crc2 = get_packet_and_crc("Hello, World!".encode('utf-8'))
test3, crc3 = get_packet_and_crc("egdy12t81`y98*&^1891US9H91Y239EQ8".encode('utf-8'))

assert check_crc(test1, crc1)
assert check_crc(test2, crc2)  # проверяем, что проверку циклического кода неискаженный пакет проходит
assert check_crc(test3, crc3)  # (искажённый пакет может и пройти, и не пройти... его не проверяем)
# ----------


text = """Мой дядя самых честных правил,
          Когда не в шутку занемог,
          Он уважать себя заставил
          И лучше выдумать не мог.
          Его пример другим наука;
          Но, боже мой, какая скука
          С больным сидеть и день и ночь,
          Не отходя ни шагу прочь!"""  # текст, который передаём по воображаемому каналу

bytes_text = text.encode("utf-8")  # превращаем в байты

k = 0
while True:
    bytes_packet = bytes_text[k: k+5]  # берём пакет - 5 байтов текста
    if bytes_packet == b'':
        break

    bin_packet, crc = get_packet_and_crc(bytes_packet)  # превращаем пакет в биты и получаем его crc

    new_bin_packet, falsified = falsify_bits(bin_packet)  # возможно, искажаем биты пакета

    print("Пакет: ", bytes_packet.decode("utf-8", errors='ignore'))  # выводим то, что кодирует пакет
    # (так как текст у нас русский, а на кодировку одной русской буквы в utf-8 уходит больше одного байта,
    # то из-за того, что текст bytes_text мы режем на пакеты неровно, может быть ситуация, что байты, отвечающие
    # за одну и ту же букву, окажутся в разных пакета... тогда при попытке расшифровать, будет ошибка...
    # чтобы ошибок при расшифровке не было, мы просто игнорируем ошибки (errors='ignore') -> из-за этого пакет
    # будет выведен не целиком, а только то, что удалось расшифровать - но не важно)
    print("Закодированный пакет: ", bin_packet)
    print()
    print("Пакет после передачи (возможно, искажён): ", new_bin_packet)
    print("Пакет был искажён? ", falsified)  # True - мы искажади пакет, False -  иначе
    print("Проверка crc прошла? ", check_crc(new_bin_packet, crc))  # проверяем, прошла ли проверка crc
    print("------------------------------------------------------")
    print()
    k += 5
