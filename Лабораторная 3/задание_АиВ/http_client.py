import socket
import sys

if len(sys.argv) != 4:
    HOST, PORT, file = "127.0.0.1", 32000, "temp1.html"
    print("Некорректный ввод параметров!")
    print(f'...спользуется дефолтный набор параметров: хост сервера={HOST}, '
          f'порт сервера={PORT}, имя файла={file}')
    print()
else:
    program_name, HOST, PORT, file = sys.argv
    PORT = int(PORT)

request = f"GET /{file} HTTP/1.1\r\nHost: {HOST}:{PORT}\r\n\r\n"
response = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(request.encode("utf-8"))
    while True:
        try:
            sock.settimeout(3)
            data = sock.recv(1024)
        except TimeoutError:
            data = None
        if data:
            response += data.decode("utf-8")
        else:
            print("Ответ от сервера:")
            print(response)
            break
