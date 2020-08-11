import queue
import itertools
import math

from Game.puyo import Puyo, puyo2, Puyopuyo, In_position, Dummy


class Puyobox():
    def __init__(self):
        self._puyo: Puyo = None
        self.left: Puyobox = None
        self.right: Puyobox = None
        self.up: Puyobox = None
        self.down: Puyobox = None
        self.position:Position = None

    def isempty(self):
        return self._puyo is None or isinstance(self._puyo, In_position)

    def set_position(self,position):
        self.position = position

    def set_puyo(self, puyo: Puyo):
        self._puyo = puyo

    def get_puyo(self) -> Puyo:
        return self._puyo

    def pop_puyo(self) -> Puyo:
        puyo = self.get_puyo()
        self.set_puyo(None)
        return puyo

    def reset(self):
        self._puyo = None

    def down_to(self):
        if self.down.isempty():
            down_count, down_box = self.down.down_to()
            return 1 + down_count, down_box
        else:
            return 0, self

    def __str__(self):
        if self._puyo is None:
            return ' '
        else:
            return str(self._puyo)

    @staticmethod
    def move(box_from, box_to):
        if box_to.isempty():
            box_to.set_puyo(box_from.pop_puyo())
            return True
        else:
            False

    @property
    def next_to(self):
        return (self.up, self.right, self.down, self.left)

    def next_to_with_position(self):
        return zip((Position.UP, Position.RIGHT, Position.DOWN, Position.LEFT), self.next_to)

    @staticmethod
    def dummy():
        pb = Puyobox()
        pb.set_puyo(Dummy())
        return pb


def p_add(p1, p2):
    p3 = []
    for i in range(len(p1)):
        p3.append(p1[i] + p2[i])
    return p3


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, x, y):
        self.x += x
        self.y += y
        return self

    def dif(self,x,y):
        self.x -= x
        self.y -= y
        return self

    def xy(self):
        return self.x, self.y

    def xy_rounded_down(self):
        return math.floor(self.x), math.floor(self.y)

    @staticmethod
    def LEFT(n=1):
        return Position(-n, 0)

    @staticmethod
    def RIGHT(n=1):
        return Position(0, n)

    @staticmethod
    def UP(n=1):
        return Position(0, n)

    @staticmethod
    def DOWN(n=1):
        return Position(0, -1)


class PuyoColection():
    def __init__(self, colorlen, del_len=4):
        self.puyo_conections = [None] + [dict() for _ in range(colorlen)]
        self.del_len = del_len
        self.will_del = [None] + [dict() for _ in range(colorlen)]
        self.puyo_to_box = {}

    def input(self, puyobox: Puyobox):
        puyo: Puyo = puyobox.get_puyo()
        self.puyo_to_box[puyo] = puyobox
        conections = self.puyo_conections[puyo.get_puyo()]
        title, values = str(puyo.uid), {puyo}
        conections[title] = values
        for next_to in puyobox.next_to:
            side_puyo: Puyo = next_to.get_puyo()
            if puyo == side_puyo:
                side_title, side_values = self.find_set(side_puyo)

                if side_title is not None and not title == side_title:
                    del conections[title], conections[side_title]

                    l1 = side_title.split(',') + title.split(',')
                    title, values = ','.join(sorted(set(l1), key=l1.index)), side_values | values
                    conections[title] = values

    def find_set(self, puyo: Puyo):
        for title, values in self.puyo_conections[puyo.get_puyo()].items():
            if puyo in values:
                return title, values
        return None, None

    def delete(self, puyo:Puyo):
        if self.puyo_to_box.pop(puyo,None) is not None:
            title, values = self.find_set(puyo)
            conections = self.puyo_conections[puyo.get_puyo()]
            if title is not None:
                del conections[title]
                l = title.split(',')
                l.remove(str(puyo.uid))
                values.remove(puyo)
                title, values = ','.join(l), values
                if len(values) > 0:
                    conections[title] = values
                return True
            else:
                return False
        else:
            return False

    def over_set(self):
        del_puyoset = set()
        del_puyo_conections = [dict() for _ in self.puyo_conections]

        for puyo_id in range(1, len(self.puyo_conections)):
            titles = list(self.puyo_conections[puyo_id].keys())
            for title in titles:
                if len(self.puyo_conections[puyo_id][title]) >= self.del_len:
                    del_set = self.puyo_conections[puyo_id][title]
                    del_puyoset = del_puyoset | del_set
                    del_puyo_conections[puyo_id][title] = del_set
        return del_puyoset,del_puyo_conections

    def delete_set(self):
        del_puyoset = set()
        del_puyo_conections = [dict() for _ in self.puyo_conections]

        for puyo_id in range(1, len(self.puyo_conections)):
            titles = list(self.puyo_conections[puyo_id].keys())
            for title in titles:
                if len(self.puyo_conections[puyo_id][title]) >= self.del_len:
                    del_set = self.puyo_conections[puyo_id].pop(title)
                    del_puyoset = del_puyoset | del_set
                    del_puyo_conections[puyo_id][title] = del_set
        return del_puyoset,del_puyo_conections

    def titles(self, color_index):
        return self.puyo_conections[color_index].keys()


class stage:
    def __init__(self, weight: int, height: int, in_position: int, color_len=4):
        self.width = weight + 2
        self.height = height + 1


        self._stage: list[list[Puyobox]] = [[Puyobox.dummy()] + [Puyobox() for _ in range(weight)] + [Puyobox.dummy()]
                                            for j in range(height)]
        self._stage.append([Puyobox.dummy() for _ in self._stage[0]])
        for j in range(0, len(self._stage) - 1):
            for i in range(1, len(self._stage[0]) - 1):
                self._stage[j][i].left = self._stage[j][i - 1]
                self._stage[j][i].right = self._stage[j][i + 1]
                self._stage[j][i].up = self._stage[j - 1][i]
                self._stage[j][i].down = self._stage[j + 1][i]
        self.in_position = in_position
        self._stage[1][in_position].set_puyo(In_position())

        self._puyopuyo = None
        self.sechi = False
        self.sechicount = 0
        self.puyoColection: PuyoColection = PuyoColection(color_len)

    def stage_iteration(self, x_reverse=False, y_reverse=False, Dummy_in=True, only_exist=False):
        stage_iter = []
        Dummy_in = int(not Dummy_in)
        x_range = range(Dummy_in, len(self._stage[0]) - 1)
        y_range = range(0, len(self._stage) - Dummy_in)

        if x_reverse:
            x_range = reversed(x_range)
        if y_reverse:
            y_range = reversed(y_range)
        for x, y in itertools.product(x_range, y_range):
            puyo_box: Puyobox = self._stage[y][x]
            if only_exist and puyo_box.isempty():
                pass
            else:
                stage_iter.append((x, y, puyo_box))
        return stage_iter

    def set_in(self, puyopuyo: Puyopuyo):
        self._puyopuyo:Puyopuyo = puyopuyo
        self._puyo_position:Position = Position(self.in_position, 1)
        for x, y, puyo in puyopuyo.iteration():
            if isinstance(puyo, In_position):
                self._puyo_position.add(-x, -y+0.5)
                puyopuyo._puyopuyo[y][x] = None

        self.sechicount = 0
        self.sechi = False
        self.time_reset()
        return self._stage[1][self.in_position].isempty()

    def time_reset(self):
        self.fly_flame = 0
        self.set_flame = 0

    def right(self):
        rightable = self.is_rightable()
        if rightable:
            self._puyo_position.x += 1
        return rightable

    def left(self):
        leftable = self.is_leftable()
        if leftable:
            self._puyo_position.x += -1
        return leftable

    def turn(self, n):
        puyopuyo: Puyopuyo = self._puyopuyo
        p = self._puyo_position
        if puyopuyo.turn(n):
            p.add(**puyopuyo.superzurash(n))
        elif self.is_conflict(middle_down=True):
            zurashi = puyopuyo.zurashi()
            p.add(**zurashi)
            if self.is_conflict(middle_down=True):
                # print('conflict')
                puyopuyo.turn(-n)
                p.dif(**zurashi)

    def down(self, half = True):
        if half:
            self._puyo_position.y += 0.5
            return True
        else:
            self._puyo_position.y += 1
            return True

    def is_moveable(self, _x: int, _y: int, middle_down=False):
        if not _x * _y == 0:
            return None
        _puyopuyo: Puyopuyo = self._puyopuyo
        px, py = self._puyo_position.xy()
        py = math.ceil(py) if middle_down else math.floor(py)
        for i, j, puyo in _puyopuyo.iteration(reverse=True, y_short=_y):
            x = px + i
            y = py + j
            if not self._stage[y + _y][x + _x].isempty():
                return False
        return True

    def is_downable(self,middle_down=False):
        return self.is_moveable(0, 1, middle_down)

    def is_leftable(self):
        return self.is_moveable(-1, 0, True)

    def is_rightable(self):
        return self.is_moveable(1, 0, True)

    def is_conflict(self, middle_down=False):
        return not self.is_moveable(0, 0, middle_down)

    def set_puyopuyo(self):
        _poyopuyo: Puyopuyo = self._puyopuyo
        px, py = self._puyo_position.xy_rounded_down()
        max_high = 0
        for i, j, puyo in _poyopuyo.iteration(reverse=True):
            x = px + i
            y = py + j
            for k in range(y + 1, len(self._stage)):
                if not self._stage[k][x].isempty():
                    puyobox = self._stage[k - 1][x]
                    puyobox.set_puyo(puyo)
                    max_high = max(max_high, k - 1 - y)
                    if not k == 1: # 最上行じゃないとき
                        self.puyoColection.input(puyobox)
                    break
        return max_high

    def width(self):
        return self.width

    def height(self):
        return self.height

    def stage_list(self, move_puyo=False):
        stage = [[self._stage[i][j].get_puyo() for j in range(self.width)] for i in range(self.height)]
        if not move_puyo:
            return stage
        else:
            _puyopuyo: Puyopuyo = self._puyopuyo
            if _puyopuyo is None:
                return stage, []
            px, py = self._puyo_position.xy()
            puyolist = []
            for i, j, puyo in _puyopuyo.iteration():
                x = px + i
                y = py + j
                puyolist.append([x, y, puyo])
            return stage, puyolist

    def stage_list_str(self, move_puyo=False):
        stage = [[str(_puyo) for _puyo in li] for li in self.stage_list(move_puyo)]
        return stage
