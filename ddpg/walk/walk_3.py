# 两条腿，学走路

import gym
import random
import collections
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

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


class Actor(nn.Module):
    def __init__(self, s_node, h1_node, h2_node, a_node):
        super().__init__()
        self.layer_s = nn.Linear(s_node, h1_node)
        self.layer_h = nn.Linear(h1_node, h2_node)
        self.layer_a = nn.Linear(h2_node, a_node)

        self.optimizer = optim.Adam(self.parameters(), lr=lr_a)  # w

    def forward(self, x):
        x = F.relu(self.layer_s(x))
        x = F.relu(self.layer_h(x))
        x = torch.tanh(self.layer_a(x))
        return x


class Critic(nn.Module):
    def __init__(self, s_node, a_node, s_h1_node, a_h1_node, h2_node, q_node):
        super().__init__()
        self.layer_s = nn.Linear(s_node, s_h1_node)
        self.layer_a = nn.Linear(a_node, a_h1_node)
        self.layer_q = nn.Linear(s_h1_node + a_h1_node, h2_node)
        self.layer_out = nn.Linear(h2_node, q_node)  # q

        self.optimizer = optim.Adam(self.parameters(), lr=lr_c)  # w

    def forward(self, s, a):
        s = F.relu(self.layer_s(s))
        a = F.relu(self.layer_a(a))
        cat = torch.cat([s, a], dim=1)
        q = F.relu(self.layer_q(cat))
        out = self.layer_out(q)
        return out


class DDPG:
    def __init__(self, s_node, a_node, h1_node, h2_node, h3_node, q_node):
        self.actor = Actor(s_node, h1_node, h2_node, a_node)
        self.actor_target = Actor(s_node, h1_node, h2_node, a_node)
        self.critic = Critic(s_node, a_node, h2_node, h2_node, h3_node, q_node)
        self.critic_target = Critic(s_node, a_node, h2_node, h2_node, h3_node, q_node)

        self.memory = ReplayBuffer()
        self.noise = Noise(actor=np.zeros(s_node))

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
    # env
    env = gym.make('BipedalWalker-v3', autoreset=True, render_mode="human")
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]

    # mind
    ddpg = DDPG(state_dim, action_dim, 64, 32, 16, 1)

    for n_epi in range(10000):
        s, _ = env.reset()
        done = False

        count = 0
        while count < 200 and not done:
            a = ddpg.actor(torch.from_numpy(s + ddpg.noise()[0]).float()).detach().numpy()
            s_next, r, done, truncated, info = env.step(a)

            ddpg.memory.put((s, a, r / 100.0, s_next, done))

            s = s_next
            count += 1

        if ddpg.memory.size() > 2000:
            for i in range(10):
                ddpg.train()
                ddpg.soft_update(ddpg.actor, ddpg.actor_target)
                ddpg.soft_update(ddpg.critic, ddpg.critic_target)

        print('epi:',n_epi)

    env.close()


if __name__ == '__main__':
    play()
