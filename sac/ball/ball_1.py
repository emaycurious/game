import gym
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal
import numpy as np
import collections, random

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
hz = 10

# Hyperparameters
lr_pi = 0.0005
lr_q = 0.001
init_alpha = 0.01
gamma = 0.98
batch_size = 32
buffer_limit = 50000
tau = 0.01  # for target network soft update
target_entropy = -1.0  # for automated alpha update
lr_alpha = 0.001  # for automated alpha update

class Ball:
    def __init__(self, x, y, r, step_x, step_y, color):
        self.x = x
        self.y = y
        self.r = r
        self.step_x = step_x
        self.step_y = step_y
        self.color = color


class ReplayBuffer():
    def __init__(self):
        self.buffer = collections.deque(maxlen=buffer_limit)

    def put(self, transition):
        self.buffer.append(transition)

    def sample(self, n):
        mini_batch = random.sample(self.buffer, n)
        s_lst, a_lst, r_lst, s_prime_lst, done_mask_lst = [], [], [], [], []

        for transition in mini_batch:
            s, a, r, s_prime, done = transition
            s_lst.append(s)
            a_lst.append(a)
            r_lst.append([r])
            s_prime_lst.append(s_prime)
            done_mask = 0.0 if done else 1.0
            done_mask_lst.append([done_mask])

        return torch.tensor(s_lst, dtype=torch.float), torch.tensor(a_lst, dtype=torch.float), \
            torch.tensor(r_lst, dtype=torch.float), torch.tensor(s_prime_lst, dtype=torch.float), \
            torch.tensor(done_mask_lst, dtype=torch.float)

    def size(self):
        return len(self.buffer)


class PolicyNet(nn.Module):
    def __init__(self, learning_rate):
        super(PolicyNet, self).__init__()
        self.fc1 = nn.Linear(2, 50)
        self.fc_mu = nn.Linear(50, 2)
        self.fc_std = nn.Linear(50, 2)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

        self.log_alpha = torch.tensor(np.log(init_alpha))
        self.log_alpha.requires_grad = True
        self.log_alpha_optimizer = optim.Adam([self.log_alpha], lr=lr_alpha)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        mu = self.fc_mu(x)
        std = F.softplus(self.fc_std(x))
        dist = Normal(mu, std)
        action = dist.rsample()
        log_prob = dist.log_prob(action)
        real_action = torch.tanh(action)
        real_log_prob = log_prob - torch.log(1 - torch.tanh(action).pow(2) + 1e-7)
        return real_action, real_log_prob

    def train_net(self, q1, q2, mini_batch):
        s, _, _, _, _ = mini_batch
        a, log_prob = self.forward(s)
        entropy = -self.log_alpha.exp() * log_prob

        q1_val, q2_val = q1(s, a), q2(s, a)
        q1_q2 = torch.cat([q1_val, q2_val], dim=1)
        min_q = torch.min(q1_q2, 1, keepdim=True)[0]

        loss = -min_q - entropy  # for gradient ascent
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

        self.log_alpha_optimizer.zero_grad()
        alpha_loss = -(self.log_alpha.exp() * (log_prob + target_entropy).detach()).mean()
        alpha_loss.backward()
        self.log_alpha_optimizer.step()


class QNet(nn.Module):
    def __init__(self, learning_rate):
        super(QNet, self).__init__()
        self.fc_s = nn.Linear(2, 25)
        self.fc_a = nn.Linear(2, 25)
        self.fc_cat = nn.Linear(50, 12)
        self.fc_out = nn.Linear(12, 1)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

    def forward(self, x, a):
        h1 = F.relu(self.fc_s(x))
        h2 = F.relu(self.fc_a(a))
        cat = torch.cat([h1, h2], dim=1)
        q = F.relu(self.fc_cat(cat))
        q = self.fc_out(q)
        return q

    def train_net(self, target, mini_batch):
        s, a, r, s_prime, done = mini_batch
        loss = F.smooth_l1_loss(self.forward(s, a), target)
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

    def soft_update(self, net_target):
        for param_target, param in zip(net_target.parameters(), self.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - tau) + param.data * tau)


def calc_target(pi, q1, q2, mini_batch):
    s, a, r, s_prime, done = mini_batch

    with torch.no_grad():
        a_prime, log_prob = pi(s_prime)
        entropy = -pi.log_alpha.exp() * log_prob
        q1_val, q2_val = q1(s_prime, a_prime), q2(s_prime, a_prime)
        q1_q2 = torch.cat([q1_val, q2_val], dim=1)
        min_q = torch.min(q1_q2, 1, keepdim=True)[0]
        target = r + gamma * done * (min_q + entropy)

    return target


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
    target = Ball(bg_width - 10, bg_height // 2, 10, 0, 0, Red)

    # mind
    memory = ReplayBuffer()
    q1, q2, q1_target, q2_target = QNet(lr_q), QNet(lr_q), QNet(lr_q), QNet(lr_q)
    pi = PolicyNet(lr_pi)

    q1_target.load_state_dict(q1.state_dict())
    q2_target.load_state_dict(q2.state_dict())

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                save(pi)
                sys.exit()

        done = 0  # 开始一轮

        count = 0
        while count < 200 and not done:  # 每一轮动 200 下

            # 动一下
            s = np.array([ball.x / 100.0, ball.y / 100.0])
            a, log_prob = pi(torch.from_numpy(s).float())
            a = 2.0 * a.detach().numpy()

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

            # 存进去 (for train)
            memory.put((s, a, r, s_next, done))
            count += 1

        if memory.size() > 1000:

            # 每轮训练 20 次
            for i in range(20):
                mini_batch = memory.sample(batch_size)
                td_target = calc_target(pi, q1_target, q2_target, mini_batch)
                q1.train_net(td_target, mini_batch)
                q2.train_net(td_target, mini_batch)
                pi.train_net(q1, q2, mini_batch)
                q1.soft_update(q1_target)
                q2.soft_update(q2_target)

        # show
        background.fill(Black)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


# 把大脑拿下来，试一试

def save(pi):
    # 保存
    torch.save(pi.state_dict(), 'pi.pth')
    print('saved')



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
