# класс для описания маршрутизатора
class Host:
    def __init__(self, num):
        self.number = num  # номер маршрутизатора
        self.neighbours = []  # список элементов типа Host - других маршрутизаторов - соседей для данного
        self.dist_neigh = dict()  # по номеру соседа храним расстояние до него (не кратчайшй путь, а прмяое расстояние)
        self.data_for_update = []  # здесь копятся данные от соседних маршрутизаторах об обновлении в их таблицах
        self.table_router = dict()  # таблица маршрутизации - словарь: по номеру маршрутизатора N храним пару
        # вида (D, R), где N - номер маршрутизатора, которому предназначаются пакеты; D - номер соседнего
        # маршрутизатора (соседнего для того, у которого table_router рассматриваем), на который будем отправлять
        # пакеты, предназначенные для N (а далее уже D передаст их дальше к N или не передат, если D=N); R - вес
        # пути от текущего маршрутизатора к N через D  (после окончания алгоритма, R - миинимально возодный вес пути)

    # функция получает список пар из соседних маршрутизаторов и расстояний до них -> заполняет:
    def set_neighbours(self, list_):
        new_path = dict()
        for neigh, dist in list_:
            self.neighbours.append(neigh)
            self.dist_neigh[neigh.number] = dist
            self.table_router[neigh.number] = (neigh.number, dist)
            new_path[neigh.number] = (self.number, dist)
        return new_path  # новые пути возвращаем

    # отправить сообщение msg (об обновлени своих путей) всем соседним маршрутизаторам
    def send_update(self, msg):
        # msg - словарь, где по номеру маршрутизатора B хранится номер другого маршрутизатора A
        # и текущее известное минимальное расстояние от A до B
        # (A - это номер текщего маршрутизатора (который отправляет сообщение соседям), B - это номер какого-то другого
        # маршрутизатора, до которого был найден болле короткий маршрут)
        for host in self.neighbours:
            host.data_for_update.append(msg)

    # из известной таблицы перенаправлений (маршрутизации) получаем сообщение msg для соседей
    def get_msg(self):
        return {dest: (self.number, dist) for dest, (_, dist) in self.table_router.items()}

    # функция улучшение таблицы маршрутизации на основе данных от других (соседних!) маршрутизаторов
    def improve(self):
        improve_path = dict()
        for msg in self.data_for_update:  # перебираем то, что соседи прислали

            # length - новая длина пути от num_host (сосед для данного) до destination:
            for destination, (num_host, length) in msg.items():
                if destination == self.number:  # интересуют только пути до других хостов
                    continue
                to_num_host = self.dist_neigh[num_host]  # прмяое (без промежуточных) расстояние до соседа num_host

                # если в таблице маршрутизации ещё нет пути до destination или текущая длина пути больше, чем
                # через num_host, то добавляем в таблицу маршрутизации путь до destination через соседа - num_host
                # Обновление вносим в improve_path ( - содержит то же, что и msg)
                if destination not in self.table_router:
                    self.table_router[destination] = (num_host, length + to_num_host)
                    improve_path[destination] = (self.number, length + to_num_host)
                elif self.table_router[destination][1] > length + to_num_host:
                    self.table_router[destination] = (num_host, length + to_num_host)
                    improve_path[destination] = (self.number, length + to_num_host)

        if len(improve_path) > 0:  # если есть обновления путей
            return self.get_msg()  # возвращаем всю информацию об ВСЕХ известных маршрутах
        else:
            return {}  # иначе пустой словарь

    # функция обновления расстояние до соседа:
    # num - номер соседа для данного маршрутизатора, new_dist - расстояние до него напрямую
    def change_dist(self, num, new_dist):
        upd = 0
        if num in self.dist_neigh:  # если такой сосед уже был
            delta = new_dist - self.dist_neigh[num]  # считаем изменение расстояния
            self.dist_neigh[num] = new_dist

            for N, (D, R) in self.table_router.items():
                if D == num:  # все пути, которые проходили через этого соседа изменяем на delta
                    self.table_router[N] = (D, R + delta)
                    if delta != 0:
                        upd = 1  # помечаем, что есть измение

            if self.table_router[num][1] > new_dist:  # если можно укоротить путь до соседа, меняем его:
                self.table_router[num] = (num, new_dist)
                upd = 1
        else:
            self.dist_neigh[num] = new_dist  # если это новый сосед, добавляем его
            self.table_router[num] = (num, new_dist)
            upd = 1

        if upd == 1:  # если что-то изменилось, возвращаем все маршруты
            return self.get_msg()
        else:
            return {}


"""вносим информацию о текущей конфигурации сети"""
m0 = Host(0)  # согласно схеме в условии, у нас 4 маршрутизатора с номероами от 0 до 3
m1 = Host(1)
m2 = Host(2)
m3 = Host(3)
hosts = [m0, m1, m2, m3]
num_hosts = 4

msg0 = m0.set_neighbours([(m3, 7), (m2, 3), (m1, 1)])  # перечисляем соседей для каждого маршрутизатора и расстояния
msg1 = m1.set_neighbours([(m0, 1), (m2, 1)])
msg2 = m2.set_neighbours([(m3, 2), (m0, 3), (m1, 1)])
msg3 = m3.set_neighbours([(m0, 7), (m2, 2)])
msgs = [msg0, msg1, msg2, msg3]

"""работает алгоритм:"""
while True:
    for i in range(num_hosts):  # рассылаем обовления
        hosts[i].send_update(msgs[i])
    for i in range(num_hosts):  # улучшаем маршруты
        msgs[i] = hosts[i].improve()

    count = 0
    for msg in msgs:  # если ни один маршрутизатор ничего не улучшил (msg - пустой словарь)
        if len(msg) == 0:
            count += 1
    if count == num_hosts:
        break  # выходим

"""результаты"""
for i in range(num_hosts):
    print("Таблица для {}".format(i))
    for d, (n, l) in hosts[i].table_router.items():
        print("Пакеты для {} отправляются на {}, полный путь = {}".format(d, n, l))
    print()

"""--------------------------------------------"""
msg0 = m0.change_dist(3, 3)  # расстояние между 0 и 3 стало 3
msg3 = m3.change_dist(0, 3)
msgs = [msg0, {}, {}, msg3]

"""работает алгоритм:"""
while True:
    for i in range(num_hosts):  # рассылаем обовления
        hosts[i].send_update(msgs[i])
    for i in range(num_hosts):  # улучшаем маршруты
        msgs[i] = hosts[i].improve()

    count = 0
    for msg in msgs:  # если ни один маршрутизатор ничего не улучшил (msg - пустой словарь)
        if len(msg) == 0:
            count += 1
    if count == num_hosts:
        break  # выходим

"""результаты"""
print()
print("---------------------------------------------")
print()
print("Результаты после изменения пути между 0 и 3 -> теперь длина пути = 3")
for i in range(num_hosts):
    print("Таблица для {}".format(i))
    for d, (n, l) in hosts[i].table_router.items():
        print("Пакеты для {} отправляются на {}, полный путь = {}".format(d, n, l))
    print()
