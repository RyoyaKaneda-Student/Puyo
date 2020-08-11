import sys

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import random
import math

import GUI.Colors as Color
from GUI.gamegamen import GameGamen
import pygame
from pygame.locals import *

from Game.game import Game, Operation, M_Operation
from Game.puyo import Puyo, Puyopuyo

from DQN.Action_Reward import ActionRewards
from DQN.Q_net import DQN
from DQN.Memory import ReplayMemory, Transition

BATCH_SIZE = 128
GAMMA = 0.999
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 200
TARGET_UPDATE = 10

device = 'cpu'

g = Game()
ar = ActionRewards(g)

clock = pygame.time.Clock()

policy_net = DQN(g.stage).to(device)
target_net = DQN(g.stage).to(device)

target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.Adam(policy_net.parameters())
memory = ReplayMemory(10000)

steps_done = 0


def select_action(state):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max(1) will return largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return ar.get_action_torch_values(state, policy_net).max(1)[1].view(1, 1)
    else:
        return ar.get_random_action_torch_values(state).max(1)[1].view(1, 1)


episode_durations = []


def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
    # detailed explanation). This converts batch-array of Transitions
    # to Transition of batch-arrays.
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    # (a final state would've been the one after which simulation ended)
    non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=device, dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state
                                       if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch)

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1)[0].
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0].detach()
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    # Compute Huber loss
    loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    for param in policy_net.parameters():
        param.grad.data.clamp_(-1, 1)
    optimizer.step()


game = GameGamen(g)
game.draw('')
isdraw = True
num_episodes = 5000
for i_episode in range(num_episodes):
    # Initialize the environment and state
    all_flame = 0
    ar.reset()
    state = ar.get_state()
    for t in range(50000):
        # Select and perform an action
        action = select_action(state)
        next_state, reward, done, info = ar.step(all_flame, action)
        reward = torch.tensor([reward], device=device)
        all_flame += info['flame']
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
            if event.type == KEYDOWN:  # キーを押したとき
                # ESCキーならスクリプトを終了
                if event.key == K_ESCAPE:
                    sys.exit()
                if event.key == K_s:
                    isdraw = not isdraw
        if isdraw:
            dt = clock.tick(240) / 1000
            game.draw(f'episode {i_episode}, dt = {dt}')
        else:
            # dt = clock.tick(60) / 1000
            g.turn_end = False
            # game.draw(f'episode {i_episode},  dt = {dt}, mode speedy')
        # Store the transition in memory
        memory.push(state, action, next_state, reward)

        # Move to the next state
        state = next_state

        # Perform one step of the optimization (on the target network)
        optimize_model()
        if done:
            episode_durations.append(t + 1)
            print(f"episode {i_episode}\t, final flame {all_flame}\t, final step {t}")
            break
    # Update the target network, copying all weights and biases in DQN
    if i_episode % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())

print('Complete')
game = GameGamen()
game.draw('')
running = True
while running:
    m_operation = ar.get_action_operations(ar.get_state(), target_net)[0]
    print(m_operation)
    running = game.skiploop(m_operation)
