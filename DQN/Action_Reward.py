import random

import torch  # ライブラリ「PyTorch」のtorchパッケージをインポート
import torch.nn as nn  # 「ニューラルネットワーク」モジュールの別名定義

import GUI.Colors as Color
from pygame.locals import *

from Game.game import Game, Operation, M_Operation
from Game.puyo import Puyo, Puyopuyo
from DQN.Q_net import DQN

from Game.game import Game, Operation, M_Operation
from Game.puyo import Puyo, Puyopuyo
from Game.puyo import reset as PuyoReset


class ActionRewards:

    def __init__(self, g: Game):
        self.g = g

    def get_state(self):
        stage_list = self.g.stage.stage_list()
        stage_list_int = [[puyo._puyoid if puyo is not None else 0 for puyo in stage_list[y][1:-1]]
                          for y in range(len(stage_list))][:-1]
        stage_1list_int = [id for _list in stage_list_int for id in _list]

        state_list = stage_1list_int + [puyo._puyoid for puyo in self.g.next_puyo.puyos if not puyo._puyoid == -1]
        state_list = state_list + [puyo._puyoid for puyo in self.g.nxnx_puyo.puyos if not puyo._puyoid == -1]

        return torch.tensor([state_list], dtype=torch.float)

    def get_action_torch_values(self, state, dqn: DQN):
        x = dqn(state)
        return x

    def get_action_operations(self, state, dqn: DQN):
        x = self.get_action_torch_values(state, dqn)
        return self.to_m_operations(x)

    def get_random_action_torch_values(self, state):
        x = torch.rand(len(state), 22)
        return x

    def to_m_operations(self, x):
        m_operations = []
        ops = x.tolist()

        for op in ops:
            op = op[0]
            if op > 2:
                op = op + 1
            side = op // 4 + 1
            turn = op % 4

            m_operations.append(M_Operation(side=side, turn=turn))
        return m_operations

    def reset(self):
        self.g.reset()
        self.g.next()
        PuyoReset()

    def step(self, all_flame: int, action):
        g = self.g
        flame = 0
        point = g.rensa_point
        reward = 0
        done = False
        m_operation = self.to_m_operations(action)[0]
        end_moves = g.skip_loop(m_operation)
        flame += len(end_moves)
        end_moves = g.skip_loop(m_operation)
        flame += len(end_moves)
        get_point = g.rensa_point - point
        if get_point > 0:
            reward = reward + 1
        # reward = get_point

        if g.batankyu:
            done = True
            reward = reward - 1
            return None, reward, done, {'flame': flame}  # 行動後の状態、reward,ゲーム終了フラグ
        else:
            reward = reward + 1

        if all_flame + flame >= 18000:
            done = True
            return None, reward, done, {'flame': flame}  # 行動後の状態、reward,ゲーム終了フラグ

        return self.get_state(), reward, done, {'flame': flame}  # 行動後の状態、reward,ゲーム終了フラグ
