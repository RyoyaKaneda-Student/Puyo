from Game.stage import stage, Puyobox
from Game.puyo import Puyo, Puyopuyo, puyo2

from collections import deque
import queue
import random
import threading
from dataclasses import dataclass

chigiri_flame = (0, 19, 24, 28, 31, 34, 37, 40, 44, 46, 48, 50, 52, 54, 56, 58, 60)
kesi_flame = (55, 80, 82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110)


class Task():
    def __init__(self, flame, task_name, description=""):
        self.flame = flame
        self.task_name = task_name
        self.description = description
        self.mode = 'weit'

        self.start_func = None
        self.running_func = None
        self.end_func = None

    def start(self):
        self.mode = 'running'
        self.start_func() if self.start_func is not None else None
        return self

    def do(self):
        self.flame -= 1
        self.running_func() if self.running_func is not None else None
        if self.flame == 0:
            self.done()
        return self.mode

    def done(self):
        self.mode = 'finish'
        self.end_func() if self.end_func is not None else None
        return self

    @staticmethod
    def sechi_task():
        task = Task(flame=1, task_name='sechi')
        return task

    @staticmethod
    def side_move_task():
        task = Task(flame=1, task_name='side_move')
        return task

    @staticmethod
    def chigiri_task(max_high):
        task = Task(flame=chigiri_flame[max_high], task_name='chigiri')
        return task

    @staticmethod
    def next_task():
        task = Task(flame=25, task_name='next')
        return task

    @staticmethod
    def kesi_task(kesi, rensa):
        task = Task(flame=0, task_name=f'rensa{rensa}')

        def func():
            max_rensa_high, _ = kesi()
            task.flame = kesi_flame[max_rensa_high]

        task.start_func = func
        return task


@dataclass
class Operation:
    right: bool = False
    left: bool = False
    down: bool = False
    turn_right: bool = False
    turn_left: bool = False

    def copy(self):
        return Operation(self.right, self.left, self.down, self.turn_right, self.turn_left)

@dataclass
class M_Operation:
    side: int = 3  # 1~6
    down: int = -1
    turn: int = 0


Rensa_Bounus = (0, 0, 8, 16, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, 480, 512, 544, 576,)
Renketu_Bounus = (0, 0, 0, 0, 0, 2, 3, 4, 5, 6, 7, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11,)
Color_Bounus = (0, 0, 3, 6, 12, 24, 48,)


class Game:
    def __init__(self):
        self._queue: deque = deque([])
        self.color_len = 4
        self.next_count = 2
        [self.put() for _ in range(self.next_count)]
        # self.interval = 1
        self.move_to = None
        self.tasks = deque([])
        self.operation: Operation = None
        self.turn_end = False
        self.batankyu = False

        self.rensa_point  = 0
        self.rakka_point = 0
        self.zenkesi_point = 0

        self.stage = stage(weight=6, height=13, in_position=3, color_len=self.color_len)

    def reset(self):
        self.__init__()

    def queue_get(self):
        return self._queue.popleft()

    def queue_put(self, puyopuyo: Puyopuyo):
        self._queue.append(puyopuyo)

    def put(self):
        puyos = [Puyo(random.randint(1, self.color_len)) for _ in range(2)]
        p2 = puyo2(puyos[0], puyos[1])
        self.queue_put(p2)

    def turn_start(self):
        self.turn_end = False

    def next(self):
        if not self.stage._stage[1][self.stage.in_position].isempty():
            self.batankyu = True
            self.turn_end = True
            return False
        task = Task.next_task()

        def func():
            self.put()
            puyopuyo = self.queue_get()
            self.stage.set_in(puyopuyo)
            self.set_flame = 0
            self.downable = True
            self.puyo_in = True

        task.end_func = func
        self.tasks.append(task.start())
        self.turn_end = True
        self.puyo_in = False
        return True

    def point_cal(self, rensa, del_puyo_conections):
        bounus = 0
        color_count = 0
        renketsu_bounus = 0
        puyo_count = 0

        bounus += Rensa_Bounus[rensa]
        for puyo_id in range(1, len(del_puyo_conections)):
            if len(del_puyo_conections[puyo_id]) > 0:
                color_count += 1
                for title, puyo_set in del_puyo_conections[puyo_id].items():
                    _count = len(puyo_set)
                    puyo_count += _count
                    renketsu_bounus += Renketu_Bounus[_count]

        bounus += renketsu_bounus
        bounus += Color_Bounus[color_count]
        bounus = max(1, bounus)
        return puyo_count * bounus

    def has_kesi(self):
        # つながってるのをけす
        del_puyoset, del_puyo_conections = stage.puyoColection.delete_set()
        return

    def kesi(self, rensa=1):
        stage = self.stage
        # つながってるのをけす
        del_puyoset, del_puyo_conections = stage.puyoColection.delete_set()

        if len(del_puyoset) > 0:
            def func():
                # 下に移動
                max_rensa_high = 0
                for del_puyo in del_puyoset:
                    del_box = stage.puyoColection.puyo_to_box[del_puyo]
                    del_box.reset()
                for x, y, puyo_box in stage.stage_iteration(y_reverse=True, Dummy_in=False, only_exist=True):
                    down_count, down_puyobox = puyo_box.down_to()
                    if down_count > 0:
                        stage.puyoColection.delete(puyo_box.get_puyo())
                        max_rensa_high = max(max_rensa_high, down_count)
                        Puyobox.move(box_from=puyo_box, box_to=down_puyobox)
                        stage.puyoColection.input(down_puyobox)

                self.rensa_point += self.point_cal(rensa, del_puyo_conections)
                return max_rensa_high, del_puyo_conections

            def finish_func():
                self.kesi(rensa=rensa + 1)

            kesi_task = Task.kesi_task(func, rensa)
            kesi_task.end_func = finish_func
            self.tasks.append(kesi_task.start())
            return True
        else:
            return self.next()

    def loop(self):
        stage = self.stage
        move = ''
        if len(self.tasks) > 0:
            state = self.tasks[0].do()
            move = self.tasks[0].task_name + ' ' + state
            if state == 'finish':
                self.tasks.popleft()

            return stage, move

        downable = stage.is_downable()
        if downable:
            stage.sechi = False
            move = move + 'downable, '
            stage.fly_flame += 1
        else:
            stage.fly_flame = 7
            if not stage.sechi:
                stage.sechi = True
                # self.tasks.append(Task.sechi_task().start())
            stage.set_flame += 1
            move = move + f'not downable {stage.set_flame}, '

        if stage.fly_flame >= 12:
            stage.down()
            stage.fly_flame = 0
            return stage, move + 'down'
        elif stage.set_flame >= 45:
            max_chigiri_high = stage.set_puyopuyo()
            self.stage._puyopuyo = None

            if max_chigiri_high > 0:
                task = Task.chigiri_task(max_chigiri_high).start()
                move = move + f"chigiri {max_chigiri_high}, "
                task.end_func = self.kesi
                self.tasks.append(task)

            else:
                if not self.kesi():
                    return stage, 'batankyu'

            return stage, move + ', next'

        if self.operation.turn_right and not self.operation.turn_left:
            turnable = stage.turn(1)
        elif self.operation.turn_left and not self.operation.turn_right:
            turnable = stage.turn(-1)

        moveable = False
        if self.operation.right:
            moveable = stage.right()
        elif self.operation.left:
            moveable = stage.left()

        if moveable:
            self.tasks.append(Task.side_move_task().start())
            self.operation.right = False
            self.operation.left = False
        elif self.operation.down:
            self.rakka_point += 1
            if downable:
                moveable = downable
                stage.down()
                downable2 = stage.is_downable()
                if downable2:
                    stage.down()
                    self.tasks.append(Task.side_move_task().start())
                stage.fly_flame = 0
            else:
                stage.set_flame += 60

        return stage, move

    def skip_loop(self, m_operation: M_Operation):
        operations = deque([Operation() for _ in range(30)])
        end_moves = []

        if len(self.tasks) == 1 and self.tasks[0].task_name == 'next':
            is_end = lambda: not self.puyo_in

        else:
            is_end = lambda: not self.turn_end

            downmove = Operation()
            if m_operation.down == -1:
                downmove.down = True
                for operation in operations:
                    operation.down = True

            while m_operation.side > 3:
                operations[m_operation.side-4].right = True
                m_operation.side = m_operation.side - 1
            while m_operation.side < 3:
                operations[2-m_operation.side].left = True
                m_operation.side = m_operation.side + 1

            if m_operation.turn == 1:
                operations[0].turn_right = True
            elif m_operation.turn == 2:
                operations[0].turn_right = True
                operations[1].turn_right = True
            elif m_operation.turn == 3:
                operations[0].turn_left = True

        while is_end():
            if len(self.tasks) > 0:
                self.operation = Operation()
            else:
                self.operation = operations.popleft()

            stage, move = self.loop()
            end_moves.append((self.operation, stage.stage_list(move_puyo=True), move))
        return end_moves

    @property
    def next_puyo(self):
        return self._queue[0]

    @property
    def nxnx_puyo(self):
        return self._queue[1]

    @property
    def point(self):
        return self.rensa_point + self.rakka_point + self.zenkesi_point
