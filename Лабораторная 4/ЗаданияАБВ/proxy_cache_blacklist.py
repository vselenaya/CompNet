import socket
import os

hostname = "127.0.0.1"
port = 23456
dir_cache = "caches_pages"
blacklist_file = "config.txt"

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.bind((hostname, port))
proxy_socket.listen(1)


def add_blacklist(func_server_get):
    ban_page = "".join(["HTTP/1.1 200 OK\r\n",
                        "Server: proxy\r\n",
                        "Content-Type: text/html; charset=utf-8\r\n",
                        "\r\n",
                        "<!DOCTYPE html>\n",
                        '<html lang="ru"\n',
                        '<head>\n',
                        '    СТРАНИЦА ЗАБЛОКИРОВАНА!\n',
                        '</head>\n',
                        '</html>'])

    def server_get_with_blacklist(server_name, req):
        url = server_name + req.split("\r\n")[0].split()[1]
        if os.path.isfile(blacklist_file):
            with open(blacklist_file, "r") as f:
                blacklist = f.readlines()
        else:
            blacklist = []
        for line in blacklist:
            if url.startswith(line.strip()):
                return ban_page
        return func_server_get(server_name, req)
    return server_get_with_blacklist


def add_cache(func_server_get):
    def server_get_with_cache(server_name, req):
        page_name = req.split("\r\n")[0].split()[1][1:]
        dir_with_cache_page = os.path.join(dir_cache, server_name, page_name)
        file_cache_page = None

        if os.path.exists(dir_with_cache_page):
            for elem in os.listdir(dir_with_cache_page):
                if elem == "cache":
                    file_cache_page = os.path.join(dir_with_cache_page, elem)
                    break
        else:
            os.makedirs(dir_with_cache_page)

        if file_cache_page is None:
            response = func_server_get(server_name, req)
            with open(os.path.join(dir_with_cache_page, "cache"), "w") as f:
                f.write(response.replace("\r\n", "\n"))
            return response

        else:
            with open(os.path.join(file_cache_page), "r") as f:
                cache_page = f.read().replace("\n", "\r\n")
            etag = None
            last_modified = None
            for line in cache_page.split("\r\n"):
                if "Last-Modified:" in line:
                    last_modified = line.split(" ", 1)[1]
                if "ETag:" in line:
                    etag = line.split(" ", 1)[1]

            clean_req = [l for l in req.split("\r\n") if not
                         (l.startswith("If-Modified-Since:") or l.startswith("If-None-Match:"))]
            new_req = "\r\n".join(clean_req[:2] + ["If-Modified-Since: {}".format(last_modified),
                                                   "If-None-Match: {}".format(etag)] + clean_req[2:])
            response = func_server_get(server_name, new_req)
            print("Ответ когда кеш есть:\n", response)
            if "304 Not Modified" in response:
                print("Используем данные из кеша")
                return cache_page
            else:
                with open(os.path.join(file_cache_page), "w") as f:
                    f.write(response.replace("\r\n", "\n"))
                    print("Обновляем кеш")
                return response
    return server_get_with_cache


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


def process_request(req):
    try:
        req_url = req.split("\r\n")[0].split()[1][1:]

        if "/" in req_url:
            server_name, page_name = req_url.split("/", 1)
            new_req = "\r\n".join(["GET /{} HTTP/1.1".format(page_name),
                                   "Host: {}".format(server_name),
                                   *req.split("\r\n")[2:]])
        elif len(req_url) > 0:
            server_name = req_url
            new_req = "\r\n".join(["GET / HTTP/1.1",
                                   "Host: {}".format(server_name),
                                   *req.split("\r\n")[2:]])
        else:
            return "", ""
        return new_req, server_name
    except IndexError:
        return None, None


@add_blacklist
@add_cache
def get_from_server(server_name, req):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.connect((server_name, 80))
            server_socket.sendall(req.encode("utf-8"))
            response = get_data(server_socket)

        except socket.gaierror:
            response = "".join(["HTTP/1.1 404 Not Found\r\n",
                                "Server: None\r\n",
                                "\r\n"])
    return response


while True:
    print("Ожидается запрос...")
    connection, client_address = proxy_socket.accept()
    print("... подключено, получаем запрос")

    try:
        request = get_data(connection)
        new_request, server = process_request(request)
        if new_request is None:
            continue
        elif new_request == "":
            server_response = "".join(["HTTP/1.1 400 Bad Request\r\n",
                                       "Server: None\r\n",
                                       "\r\n"])
        else:
            server_response = get_from_server(server, new_request)

        connection.sendall(server_response.encode("utf-8"))

    finally:
        connection.close()
