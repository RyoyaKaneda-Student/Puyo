n = 0


def uid():
    global n
    n = n + 1
    return n

def reset():
    global n
    n = 0


class Puyo():
    def __init__(self, _puyo: int = None):
        self._puyoid: int = _puyo
        self.uid: int = uid()
        self.hasfriend: bool = False

    def set(self, _puyo: int):
        self._puyoid = _puyo

    def get_puyo(self) -> int:
        return self._puyoid

    def get_uid(self):
        return self.uid

    def __eq__(self, other):
        return other is not None and self.get_puyo() == other.get_puyo()

    def __str__(self):
        return str(self._puyoid)

    def __hash__(self):
        return self.uid


class In_position(Puyo):
    def __init__(self):
        super().__init__()
        self._puyoid: int = -1

    def __str__(self):
        return 'I'


class Dummy(Puyo):
    def __init__(self):
        super().__init__()
        self._puyoid: int = -2

    def __str__(self):
        return 'D'


class Ojama(Puyo):
    def __init__(self):
        super().__init__()
        self._puyoid: int = 7

    def __str__(self):
        return 'O'


class Puyopuyo():
    def __init__(self):
        self._puyopuyo = [[]]
        self._turn = 0

    def turn(self, n):
        self._turn = (self._turn + n) % 4
        return self._turn

    def position(self, n):
        return []

    def right(self):
        turn = self.turn(1)
        self._puyopuyo = self.position(self._turn)

    def left(self):
        turn = self.turn(-1)
        self._puyopuyo = self.position(self._turn)

    def __str__(self):
        for puyos in self._puyopuyo:
            print(' '.join([str(puyo) for puyo in puyos]))

    def iteration(self, reverse=False, y_short=0):
        items = []
        _puyopuyo = self._puyopuyo
        ra = range(y_short, len(_puyopuyo))
        if reverse:
            ra = reversed(ra)
        for y in ra:
            for x, item in enumerate(_puyopuyo[y]):
                if item is not None:
                    items.append((x, y, item))
        return items

    @property
    def puyos(self):
        iteration = self.iteration()
        x, y, puyos = zip(*iteration)
        return puyos


class puyo2(Puyopuyo):
    def __init__(self, top: Puyo, under: Puyo):
        super().__init__()
        self.top = top
        self.under = under
        self._puyopuyo = self.position(self._turn)
        self._puyopuyo[2][1] = In_position()

    def turn(self, n):
        super().turn(n)
        self._puyopuyo = self.position(self._turn)
        return n % 2 == 0

    def position(self, n):
        if n > 3 or n < 0:
            pass
        elif n == 0:
            return [[None, self.top, None], [None, self.under, None], [None, None, None]]
        elif n == 1:
            return [[None, None, None], [None, self.under, self.top], [None, None, None]]
        elif n == 2:
            return [[None, None, None], [None, self.under, None], [None, self.top, None]]
        elif n == 3:
            return [[None, None, None], [self.top, self.under, None], [None, None, None]]

    def right(self):
        super().right()

    def left(self):
        super().right()

    def zurashi(self):
        # print(self._turn)
        if self._turn == 0:
            return None
        elif self._turn == 1:
            return {'x': -1, 'y': 0}
        elif self._turn == 2:
            return {'x': 0, 'y': -1}
        elif self._turn == 3:
            return {'x': 1, 'y': 0}
