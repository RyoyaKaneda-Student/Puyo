import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from Game.stage import stage
from Game.game import Game, Operation, M_Operation
from Game.puyo import Puyo, Puyopuyo

from GUI.gamegamen import GameGamen

from DQN.Action_Reward import *


class DQN(nn.Module):

    def __init__(self, stage: stage):
        super(DQN, self).__init__()
        stage_len = (stage.width - 2) * (stage.height - 1)
        self.L1 = nn.Linear(stage_len + 4, stage_len + 4)
        self.L2 = nn.Linear(stage_len + 4, 22)

    def forward(self, x):
        x = F.relu(self.L1(x))
        x = F.relu(self.L2(x))
        return x

    def to_m_operations(self, x):
        m_operations = []
        ops = x.argmax(1).tolist()

        for op in ops:
            if op > 2:
                op = op + 1
            side = op // 4 + 1
            turn = op % 4

            m_operations.append(M_Operation(side=side, turn=turn))
        return m_operations


if __name__ == '__main__':
    g = Game()
    dqn = DQN(g.stage)
    ar = ActionRewards(g)
    game = GameGamen()

    game.draw('')
    running = True
    while running:
        m_operation = ar.get_action_operations(ar.get_state(), dqn)[0]
        print(m_operation)
        running = game.skiploop(m_operation)
