import socket
import os

HOST = "127.0.0.1"  # это адрес нашего сервера - в данном случае это ip-адрес самого компьютера (localhost)
PORT = 32000

# чтобы получить доступ к серверу, нужно, запустив сервер, перейти в браузер и в адресной строке
# набрать: http://localhost:32000/  (или http://127.0.0.1:32000/table.html) (ip 127.0.0.1 и localhost -
# одно и то же); чтобы получить конкретный файл, нужно сделать GET-запрос на этот сервер - в случае браузера GET
# запрос делается автоматически через адресную строку - просто после имени сервера вводим название файла;
# например: http://localhost:32000/table.html
# также можно воспользоваться клиентом (файл http_client.py), который тоже делает GET запрос...


def process_request(message, directory="./files/"):  # directory - локальная директория с фалами
    request, file, *_ = message.split()
    if request == "GET":  # сервер работает только с GET запросом
        path = directory + file
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                answer = "".join(["HTTP/1.1 200 OK\r\n",
                                  "Server: vsel_23\r\n",
                                  "Content-Type: text/html; charset=utf-8\r\n",  # обязяательно передаём кодировку
                                  # utf-8, чтобы корректно отображался русский язык
                                  "\r\n",
                                  f.read()])  # здесь данные - запрошенный файл
        else:
            answer = "".join(["HTTP/1.1 404 NOT FOUND\r\n",  # если файла нет, возвращает ошибку 404
                              "Server: vsel_23\r\n",
                              "\r\n"])
    else:
        answer = "некорректный запрос"
    return answer


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

while True:
    print("Ожидается подключение...")
    connection, client_address = sock.accept()
    print("... подключено")
    message = ""
    try:
        while True:
            try:
                connection.settimeout(2)  # устанавливаем timelimit 2 секунды на получение данных от клиента
                data = connection.recv(1024)  # получаем по 1024 байт
            except socket.timeout:  # если в течении 2 секунд данные не приходят, будет ошибка, которую мы ловим,
                data = None  # а данные считаем None
            if data:
                message += data.decode("utf-8")  # собираем из кусков по 1024 байта цельное сообщение от сервера
            else:  # как только все данные получили (то есть новый кусок стал None), начинаем формировать ответ:
                print("данные от клиента получены")
                answer = process_request(message)
                connection.send(answer.encode("utf-8"))
                connection.close()
                print()
                break
    except:  # на всякий случай, чтобы при любых ошибках закрывать соединение
        connection.close()
