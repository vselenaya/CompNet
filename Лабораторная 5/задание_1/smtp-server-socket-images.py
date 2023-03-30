import socket
import ssl
import base64

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


my_mail = "***"
my_pass = "***"
mail_server = ('smtp.gmail.com', 587)
need_TLS = True
path_to_image = "./image_for_mail.jpg"  # путь к изображению, которое хотим прикрепить


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


print("Введите адрес получателя:")
destination = input()
print()
if destination == "":
    destination = "default dest"

txt = ""  # вводим текст письма
print("Введите текст письма (txt-формат), а на последней строке - один символ точка:")
while True:
    line = input()
    if line != ".":
        txt += line + "\r\n"
    else:
        txt = txt[:-2]
        break
print()

message = MIMEMultipart()  # создаём итоговое сообщение, которое полетит получателю
message.attach(MIMEText(txt, 'plain', 'utf-8'))  # добавляем в него сам текст
with open(path_to_image, "rb") as file_image:
    image = MIMEImage(file_image.read(), _subtype='jpeg')  # считываем изображение, которое будем отправлять
    image.add_header('Content-ID', '<' + 'image_123' + '>')  # добавляем id этому изображению
    image.add_header("Content-Disposition", "inline", filename="image.jpg")
    message.attach(MIMEText('<img src="cid:image_123">', 'html'))  # добавляем html-кусок, в котором изображение
    # (к нему мы обращаемся по задданому id - по image_123) встраивается в текст письма (без этой строки изображение
    # придёт как вложение к письму)
    message.attach(image)  # добавляем в сообщение изображение
message = message.as_string() + "\r\n.\r\n"  # переводим в строку и добавляем символ окончания сообщения

print("Начинаем установку соединения...")
print()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect(mail_server)
    print(get_data(sock, timelimit=2))

    if need_TLS:
        command = "HELO smtp-server\r\n"
        print("   " + command)
        sock.sendall(command.encode("utf-8"))
        print(get_data(sock))

        command = "STARTTLS\r\n"
        print("   " + command)
        sock.sendall(command.encode("utf-8"))
        print(get_data(sock))
        sock = ssl.wrap_socket(sock)

    for command in ["HELO smtp-server\r\n",
                    "AUTH LOGIN\r\n",
                    base64.b64encode(my_mail.encode("utf-8")).decode("utf-8") + "\r\n",
                    base64.b64encode(my_pass.encode("utf-8")).decode("utf-8") + "\r\n",
                    "MAIL FROM: <{}>\r\n".format(my_mail),
                    "RCPT TO: <{}>\r\n".format(destination),
                    "DATA\r\n",
                    message,
                    "QUIT\r\n"]:

        print("   " + command)
        sock.sendall(command.encode("utf-8"))
        print(get_data(sock))
finally:
    sock.close()
