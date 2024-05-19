# Создание игры "Морской бой"

# Определяем собственное исключение
from random import randint


class CustomError(Exception):
    pass


class BoardOutException(CustomError):
    def __str__(self):
        return 'Вы стреляете вне диапазона игрового поля!'


class BoardUseException(CustomError):
    def __str__(self):
        return 'Вы уже стреляли сюда!'


# Исключение для правильной расстановки кораблей
class RightShips(CustomError):
    pass


# Класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y  # Сравнивает 2 объекта 1 класса


# Класс корабли
class Ship:
    def __init__(self, nose, length, pos):
        self.nose = nose
        self.length = length
        self.pos = pos
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.nose.x  # Нос корабля разбиваем на х
            cur_y = self.nose.y  # и y
            if self.pos == 0:  # Если положение корабля горизонтальное
                cur_x += i  # то к x прибавляем координату следуещей палубы
            elif self.pos == 1:  # Если положение корабля вертикальное
                cur_y += i  # то к y прибавляем координату следуещей палубы

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:

    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid  # информация о том, нужно ли скрывать корабли(булево значение)
        self.count = 0
        self.field = [['O'] * size for _ in range(size)]  # _ не используется счетчик
        self.busy = []  # список для хранения занятых точек, выстрел, контуры и корабли
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:  # Проходит по точкам корабля
            if self.out(d) or d in self.busy:  # Проверяет что она не выходит за поле
                raise RightShips()  # Если выходит то выбрасывает ошибку
        for d in ship.dots:  # Проходит по списку точек корабля
            self.field[d.x][d.y] = "■"  # И ставит корабль на поле
            self.busy.append(d)  # Добавляет в список занятых точек

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, 1), (0, 1), (1, 1),
            (-1, 0), (0, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)]  # Список чтобы обводить контур
        for d in ship.dots:  # Проходимся циклом по кораблю
            for dx, dy in near:  # Проходимся по списку контура
                cur = Dot(d.x + dx, d.y + dy)  # Каждой точке корабля прибавляем значения из списка контурв
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):  # i индекс
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' | '

        if self.hid:  # Меняем корабли на пустую ячейку
            res = res.replace('■', 'O')
        return res

    # для точки(объекта класса Dot) возвращает True, если точка выходит за игровое поле, и False, если не выходит
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Обводит корабль по контуру. Помечает соседние клетки где кораблей быть не должно

    def shot(self, d):
        if self.out(d):  # Стреляет по полю если оно выходит за поле
            raise RightShips()  # Выдает исключения

        if d in self.busy:  # Если точка уже занята(выстрел уже был туда)
            raise BoardUseException()

        self.busy.append(d)  # Добавляет выстрел в список busy

        for ship in self.ships:  # Проходится по списку кораблей
            if d in ship.dots:  # Если попал
                ship.lives -= 1  # то отнимает жизнь
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:  # Если жизней нет токорабль уничтожен
                    self.count += 1  #
                    self.contour(ship, verb=True)  # Если корабль уничтожен, обводит по контуру
                    print("Убит!")
                    return False
                else:
                    print("Ранен!")
                    return True

        self.field[d.x][d.y] = "."  # Ставит точку в место выстрела
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:  # Передается 2 доски врага и своя
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:  # пока истина
            try:
                target = self.ask()  # Просим сделать выстрел
                repeat = self.enemy.shot(target)  # Если попал
                return repeat  # то повтаряем просьбу
            except CustomError as e:
                print(e)


class AI(Player):
    # Компьютер рандомно делает выстрелы
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # компьютер выбирает рандомное значение
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  # Запрашиваем у пользователя координаты хода

            if len(cords) != 2:  # Если ввел больше или меньше 2 координат
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):  # Проверяем что введены числа
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # Вычетаем по 1 потому что поле начинается не с 0


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()  # Создается поле
        co = self.random_board()  # Создается  поле
        co.hid = True  # Поле игрока скрывается для компьютера
        pl.hid = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # Список допустимых длин кораблей
        board = Board(6)  # Создаем доску
        attempts = 0  # Колличество попыток создать доску
        for l in lens:  # Проходим по спску длин кораблей
            while True:
                attempts += 1
                if attempts > 2000:  # Если больше 2000 попыток
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)  # Добавляем корабль
                    break  # Если все нормально то обрываем
                except RightShips:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:  # Пока доска пуста
            board = self.try_board()  # Создаем доску
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # Список длин кораблей
        board = Board(size=self.size)  # Задаем размер доски и создаем
        attempts = 0  # Колличество попыток создания доски
        for l in lens:  # Проходим по спску длин кораблей
            while True:
                attempts += 1  # Увеличиваем колличество попыток на одну
                if attempts > 2000:  # Если больше 2000 вывести None
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except RightShips:
                    pass
        board.begin()
        return board

    def greet(self):
        # Метод приветствия
        print('''
        ----------------------
        ___Добро_пожаловать___
        ________в игру________
        _____морской бой______
        ----------------------''')
        print("Введите координаты: x y ")
        print("Где x - номер строки  ")
        print("И y - номер столбца ")

    def loop(self):
        num = 0  # Номер хода
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:  # Если номер хода четный
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:  # Если вызываем повтор хода(кто-то попал) то номер хода уменьшаем на 1
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
