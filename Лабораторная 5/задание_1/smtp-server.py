import smtplib

from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.text import MIMEText  # Текст/HTML
from email.mime.image import MIMEImage  # Изображения


# данные нашего почтового ящика, через который будем письмо отправлять:
my_mail = "st***@student.spbu.ru"  # имя почты (для нашей студ почты спбгу сервисом является gmail)
my_pass = "***"
mail_server = ('smtp.gmail.com', 587)  # адрес и порт почтового сервера
need_TLS = True  # указываем, нужно ли почтовому серверу безопасное поключение SSL/TLS или нет...

print("Введте адрес получателя:")
destination = input()
print()
if destination == "":
    destination = "default dest"  # если не ввели адрес получателя, используем какой-нибудь по умолчанию

print("Введите тему письма:")
theme = input()
if theme == "":
    theme = "Без темы"

txt = ""
print("Введите текст письма (txt-формат), а на последней строке - один символ точка:")
while True:
    line = input()
    if line != ".":
        txt += line + "\n"
    else:
        txt = txt[:-1]  # берём весь текст (кроче последнего добавленного нами перевода строки)
        break

html = ""
print("Введите html-фрагимент письма, а на послндней строке точку:")
while True:
    line = input()
    if line != ".":
        html += line + "\n"
    else:
        html = html[:-1]
        break

print("Начинаем отправлять...")

msg = MIMEMultipart()  # Создаем сообщение
msg['From'] = my_mail  # Адресат
msg['To'] = destination  # Получатель
msg['Subject'] = theme  # Тема сообщения

if txt != "":
    msg.attach(MIMEText(txt, 'plain', 'utf-8'))  # Добавляем в сообщение текст
if html != "":
    msg.attach(MIMEText(html, 'html', 'utf-8'))  # Добавляем html

server = smtplib.SMTP(mail_server)
if need_TLS:
    server.starttls()  # используем защищённое соединение TLS (такое же в https)
server.login(my_mail, my_pass)
server.send_message(msg)
server.quit()
