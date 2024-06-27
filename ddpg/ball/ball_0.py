# 小球走到目标点

import gym
import random
import collections
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import pygame, sys, random, math as m
from pygame import *
import matplotlib.pyplot as plt

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 500, 700

# fast
hz = 20

# param
lr_a = 0.0005
lr_c = 0.001
gamma = 0.99  # train
batch_size = 32
buffer_limit = 50000
tau = 0.005  # soft update target


class ReplayBuffer():
    def __init__(self):
        self.buffer = collections.deque(maxlen=buffer_limit)

    def put(self, transition):
        self.buffer.append(transition)

    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_next_lst, done_mask_lst = [], [], [], [], []

        for transition in mini_batch:
            s, a, r, s_next, done = transition
            s_lst.append(s)
            a_lst.append(a)
            r_lst.append([r])
            s_next_lst.append(s_next)
            done_mask = 0.0 if done else 1.0
            done_mask_lst.append([done_mask])

        return torch.tensor(s_lst, dtype=torch.float), torch.tensor(a_lst, dtype=torch.float), \
            torch.tensor(r_lst, dtype=torch.float), torch.tensor(s_next_lst, dtype=torch.float), \
            torch.tensor(done_mask_lst, dtype=torch.float)

    def size(self):
        return len(self.buffer)


class Noise:
    def __init__(self, actor):
        self.theta, self.dt, self.sigma = 0.1, 0.01, 0.1
        self.actor = actor
        self.x_prev = np.zeros_like(self.actor)

    def __call__(self):
        x = self.x_prev + self.theta * (self.actor - self.x_prev) * self.dt + \
            self.sigma * np.sqrt(self.dt) * np.random.normal(size=self.actor.shape)
        self.x_prev = x
        return x


class Ball:
    def __init__(self, x, y, r, step_x, step_y, color):
        self.x = x
        self.y = y
        self.r = r
        self.step_x = step_x
        self.step_y = step_y
        self.color = color


class Actor(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer_s = nn.Linear(2, 50)
        self.layer_h = nn.Linear(50, 25)
        self.layer_a = nn.Linear(25, 2)

        self.optimizer = optim.Adam(self.parameters(), lr=lr_a)  # w

    def forward(self, x):
        x = F.relu(self.layer_s(x))
        x = F.relu(self.layer_h(x))
        x = torch.tanh(self.layer_a(x))
        return x


class Critic(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer_s = nn.Linear(2, 25)
        self.layer_a = nn.Linear(2, 25)
        self.layer_q = nn.Linear(50, 12)
        self.layer_out = nn.Linear(12, 1)  # q

        self.optimizer = optim.Adam(self.parameters(), lr=lr_c)  # w

    def forward(self, s, a):
        s = F.relu(self.layer_s(s))
        a = F.relu(self.layer_a(a))
        cat = torch.cat([s, a], dim=1)
        q = F.relu(self.layer_q(cat))
        out = self.layer_out(q)
        return out


class DDPG:
    def __init__(self):
        self.actor, self.actor_target = Actor(), Actor()
        self.critic, self.critic_target = Critic(), Critic()

        self.memory = ReplayBuffer()
        self.noise = Noise(actor=np.zeros(2))  # 输入的 states 有 2 个节点

    def train(self):
        s, a, r, s_next, done = self.memory.sample(batch_size)

        target = r + gamma * self.critic_target(s_next, self.actor_target(s_next))

        c_loss = F.smooth_l1_loss(self.critic(s, a), target.detach())
        self.critic.optimizer.zero_grad()
        c_loss.backward()
        self.critic.optimizer.step()

        a_loss = -self.critic(s, self.actor(s)).mean()
        self.actor.optimizer.zero_grad()
        a_loss.backward()
        self.actor.optimizer.step()

    def soft_update(self, net, net_target):
        for param_target, param in zip(net_target.parameters(), net.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - tau) + param.data * tau)


def play():
    # init
    pygame.init()
    pygame.display.set_caption('ball go')
    hzClock = pygame.time.Clock()
    background = pygame.display.set_mode((bg_width, bg_height))

    # player ball
    begin_x, begin_y = 30, bg_height / 2
    ball = Ball(begin_x, begin_y, 10, 1, 1, Blue)

    # target ball
    target = Ball(10, bg_height- 10, 10, 0, 0, Red)

    # mind
    ddpg = DDPG()

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        done = 0  # 开始一轮

        count = 0
        while count < 200 and not done:

            # 动一下
            s = np.array([ball.x / 100.0, ball.y / 100.0])
            a = ddpg.actor(torch.from_numpy(s + ddpg.noise()[0]).float()).detach().numpy()

            # move
            old_ball_xy = [ball.x, ball.y]

            ball.step_x = a[0].item()
            ball.step_y = a[1].item()
            ball.x += ball.step_x / 10
            ball.y += ball.step_y / 10
            s_next = np.array([ball.x / 100.0, ball.y / 100.0])

            # reward
            r = get_target_reward(old_ball_xy, ball, target)
            if wall_collide(ball):  # 如果碰到墙，回到出发点
                r -= 1
                ball.x, ball.y = begin_x, begin_y
                done = 1  # 结束一轮

            # 存进去
            ddpg.memory.put((s, a, r, s_next, done))
            count += 1

        if ddpg.memory.size() > 2000:
            for i in range(10):
                ddpg.train()
                ddpg.soft_update(ddpg.actor, ddpg.actor_target)
                ddpg.soft_update(ddpg.critic, ddpg.critic_target)

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


# 碰上墙
def wall_collide(ball):
    if (0 + ball.r <= ball.x <= bg_width - ball.r) and (0 + ball.r <= ball.y <= bg_height - ball.r):
        return 0
    else:
        return 1


# 两个小球碰上
def ball_collide(ball_1, ball_2):
    if (ball_1.x - ball_2.x) ** 2 + (ball_1.y - ball_2.y) ** 2 <= (ball_1.r + ball_2.r + 10) ** 2:
        # collide !!!
        return 1
    else:
        return 0


# 靠近目标（奖励）
def get_target_reward(old_ball_xy, ball, target):
    reward = 0
    if ((ball.x - target.x) ** 2 + (ball.y - target.y) ** 2) < ((old_ball_xy[0] - target.x) ** 2 + (
            old_ball_xy[1] - target.y) ** 2):
        # print('close')
        reward += 0.01  # 和目标加分，相差大一些（球儿会向目标走，而不是不停累计路程上的分数）
    else:
        # print('far')
        reward -= 0.5

    # ball 如果碰到了目标
    if ball_collide(ball, target):
        reward += 1000
        print('touch target !!!')
    return reward


if __name__ == '__main__':
    play()
