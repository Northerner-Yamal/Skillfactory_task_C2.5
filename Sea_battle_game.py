# Практическое задание - проект "Морской бой".
# Выполнил: студент группы FPW-60 Ильин Максим.
# Дата: 03.03.2022
from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "   Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "   Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
       return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=9):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["o"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "    | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |"
        for i, row in enumerate(self.field):
            res += f"\n  {i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "o")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0 , 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "*"
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("    Корабль уничтожен!")
                    return False
                else:
                    print("    Корабль подбит!")
                    return True

        self.field[d.x][d.y] = "*"
        print("    Мимо!")
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 8), randint(0, 8))
        print(f"    Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("    Ваш ход: ").split()

            if len(cords) != 2:
                print("    Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("    Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=9):
        self.lens = [4, 3, 2, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):

        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet_and_rules(self):
        print("* " * 22)
        print("          Добро пожаловать в игру\n"
              "                МОРСКОЙ БОЙ")

        print("* " * 22)
        print("  Игроку необходимо потопить все корабли\n"
              " противника, расположенные на игровом поле.\n"
              "  Чтобы сделать ход, введите через пробел\n"
              "     координату ячейки на игровом поле\n"
              "          (например 0 1 или 1 1).")
        print("* " * 22)
        print(" Игра завершается победой игрока, если он\n"
              "  сможет первым потопить флот противника.\n"
              "               ЖЕЛАЕМ УДАЧИ!")
        print("* " * 22)

    def print_boards(self):
        print()
        print("    Доска пользователя:")
        print(self.us.board)
        print("* " * 22)
        print()
        print("    Доска компьютера:")
        print(self.ai.board)
        print("* " * 22)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("    Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("    Ходит компьютер!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("* " * 22)
                print("    Игрок выиграл!")
                break

            if self.us.board.defeat():
                print("* " * 22)
                print("    Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet_and_rules()
        self.loop()

g = Game()
g.start()