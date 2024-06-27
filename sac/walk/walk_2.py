import gym
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal
import numpy as np
import collections, random

# Hyperparameters
lr_a = 0.0005
lr_q = 0.001
init_alpha = 0.01
gamma = 0.98
batch_size = 32
buffer_limit = 50000
tau = 0.01  # for target network soft update
target_entropy = -1.0  # for automated alpha update
lr_alpha = 0.001  # for automated alpha update


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


class Actor(nn.Module):
    def __init__(self, s_node, h_node, a_node):
        super().__init__()

        self.layer_s = nn.Linear(s_node, h_node)
        self.layer_a = nn.Linear(h_node, a_node)
        self.layer_o = nn.Linear(h_node, a_node)

        self.optimizer = optim.Adam(self.parameters(), lr=lr_a)

        self.log_alpha = torch.tensor(np.log(init_alpha))
        self.log_alpha.requires_grad = True
        self.log_alpha_optimizer = optim.Adam([self.log_alpha], lr=lr_alpha)

    def forward(self, x):
        x = F.relu(self.layer_s(x))
        x_a = self.layer_a(x)
        x_o = F.softplus(self.layer_o(x))

        dist = Normal(x_a, x_o)
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

        # 更新自己
        loss = -min_q - entropy
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

        # 更新熵（混乱度，往大的走，可以尝试更多不同动作）
        self.log_alpha_optimizer.zero_grad()
        alpha_loss = -(self.log_alpha.exp() * (log_prob + target_entropy).detach()).mean()
        alpha_loss.backward()
        self.log_alpha_optimizer.step()


class Critic(nn.Module):
    def __init__(self, s_node, a_node, s_h1_node, a_h2_node, h3_node):
        super().__init__()

        self.layer_s = nn.Linear(s_node, s_h1_node)
        self.layer_a = nn.Linear(a_node, a_h2_node)
        self.layer_cat = nn.Linear(s_h1_node + a_h2_node, h3_node)
        self.layer_out = nn.Linear(h3_node, a_node)  # out dim == a dim , why ?

        self.optimizer = optim.Adam(self.parameters(), lr=lr_q)

    def forward(self, s, a):
        s = F.relu(self.layer_s(s))
        a = F.relu(self.layer_a(a))
        cat = torch.cat([s, a], dim=1)
        q = F.relu(self.layer_cat(cat))
        q = self.layer_out(q)
        return q

    def train_net(self, target, mini_batch):
        s, a, _, _, _ = mini_batch
        loss = F.smooth_l1_loss(self.forward(s, a), target)
        self.optimizer.zero_grad()
        loss.mean().backward()
        self.optimizer.step()

    def soft_update(self, net_target):
        for param_target, param in zip(net_target.parameters(), self.parameters()):
            param_target.data.copy_(param_target.data * (1.0 - tau) + param.data * tau)


class SAC(nn.Module):
    def __init__(self, s_node, a_node, h_node, h1_node, h2_node, h3_node):
        super().__init__()

        # actor
        self.actor = Actor(s_node, h_node, a_node)

        # critic ( 2 + 2 )
        self.q1, self.q2 = Critic(s_node, a_node, h1_node, h2_node, h3_node), Critic(s_node, a_node, h1_node, h2_node,
                                                                                     h3_node)
        self.q1_target, self.q2_target = Critic(s_node, a_node, h1_node, h2_node, h3_node), Critic(s_node, a_node,
                                                                                                   h1_node,
                                                                                                   h2_node, h3_node)
        self.q1_target.load_state_dict(self.q1.state_dict())
        self.q2_target.load_state_dict(self.q2.state_dict())

        # memory
        self.memory = ReplayBuffer()

    def get_target(self, actor, q1, q2, mini_batch):
        s, a, r, s_next, done = mini_batch

        with torch.no_grad():
            a_next, log_prob = actor(s_next)
            entropy = -actor.log_alpha.exp() * log_prob

            q1_val, q2_val = q1(s_next, a_next), q2(s_next, a_next)
            q1_q2 = torch.cat([q1_val, q2_val], dim=1)
            min_q = torch.min(q1_q2, 1, keepdim=True)[0]

            target = r + gamma * done * (min_q + entropy)

        return target


def play():
    # env
    env = gym.make('BipedalWalker-v3', autoreset=True, render_mode="human")
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]

    # mind
    sac = SAC(state_dim, action_dim, 128, 64, 64, 32)
    sac.actor.load_state_dict(torch.load('actor.pth'))      # 把之前的大脑安上来

    for n_epi in range(10000):
        s, _ = env.reset()
        done = False
        count = 0

        while count < 1000 and not done:  # 每一轮，动 1000 步

            a, log_prob = sac.actor(torch.from_numpy(s).float())
            a = a.detach().numpy()
            s_next, r, done, truncated, info = env.step(2.0 * a)
            sac.memory.put((s, a, r , s_next, done))
            count += 1

        if sac.memory.size() > 2000:

            for i in range(20):
                mini_batch = sac.memory.sample(batch_size)

                # critic target
                q_target = sac.get_target(sac.actor, sac.q1_target, sac.q2_target, mini_batch)

                # critic 更新
                sac.q1.train_net(q_target, mini_batch)
                sac.q2.train_net(q_target, mini_batch)

                # actor 更新
                sac.actor.train_net(sac.q1, sac.q2, mini_batch)
                sac.q1.soft_update(sac.q1_target)
                sac.q2.soft_update(sac.q2_target)

        print('epi:', n_epi)

        save(sac.actor)  # 每结束一轮，保存起来

    env.close()


def save(actor):
    # 保存
    torch.save(actor.state_dict(), 'actor.pth')
    print('saved')




if __name__ == '__main__':
    play()
