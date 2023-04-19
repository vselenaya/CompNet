k = 16  # размер кусков, на которую разбиваем входящую битовую строку (затем эти куски складываем)


def get_checksum(binary_str):  # функция получает на вход битовую (из 0 и 1) строку
    left = 0
    invert_checksum = 0  # сумма кусков входной строки (десятичное число)
    while True:  # в этом цикле суммируем k-разрядные части входной строки
        if left >= len(binary_str):
            break
        invert_checksum += int(binary_str[left:left+k], 2)
        left += k

    # получаем контрольную сумму, инвертируя её биты (для этого делаем xor с числом из одних единиц - в десятичном
    # представлении это 2^n-1, где n - длина числа)
    checksum = (2 ** len(bin(invert_checksum)[2:]) - 1) ^ invert_checksum
    return checksum


def check_checksum(binary_str, checksum):
    left = 0
    invert_checksum = 0
    while True:
        if left >= len(binary_str):
            break
        invert_checksum += int(binary_str[left:left + k], 2)
        left += k

    # проверяем, что сумма кусочков входной битововй строки и контроьной суммы - это число из единиц:
    return invert_checksum + checksum == 2 ** len(bin(invert_checksum)[2:]) - 1


# ТЕСТЫ:
str1 = "Привет! Как дела?".encode("utf-8")  # кодируем различные строки
str2 = "Hello World".encode("ascii")
str3 = "18t76812__  2277@$#9  nytwu22xbhjaa !?``,".encode("utf-8")

binary_str1 = bin(int(bytes.hex(str1), 16))[2:]  # получаем битовые последоваетльности
binary_str2 = bin(int(bytes.hex(str2), 16))[2:]
binary_str3 = bin(int(bytes.hex(str3), 16))[2:]

cs1 = get_checksum(binary_str1)  # получаем контрольную сумму
cs2 = get_checksum(binary_str2)
cs3 = get_checksum(binary_str3)

assert check_checksum(binary_str1, cs1)  # проверяем
assert check_checksum(binary_str2, cs2)
assert check_checksum(binary_str3, cs3)
assert not check_checksum(binary_str1 + '1', cs1)
assert not check_checksum(binary_str2[:-1], cs2)
if binary_str3[3] == '0':
    assert not check_checksum(binary_str3[:3] + '1' + binary_str3[4:], cs3)
else:
    assert not check_checksum(binary_str3[:3] + '0' + binary_str3[4:], cs3)
