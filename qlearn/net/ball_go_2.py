# 小球用 神经网络 来学习
# 避开飞过来的敌人

import pygame, sys, random, math as m
import numpy
from pygame import *

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 255, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 700, 500

# fast
hz = 20

# reward
jiao_list = [0, 90, 180, 270]
move_reward = [1, 0, 0, 0]

result_reward = [0, -6, 0, -3]  # (没碰上球，碰上球，不碰墙，碰墙)

target_reward = [5, 3, 2, -1, -2]


# ball
class Ball:
    def __init__(self, x, y, r, jiao, step, color):
        self.x = x
        self.y = y
        self.r = r
        self.jiao = jiao
        self.step = step
        self.color = color


class Target:
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color




def play():
    # init

    pygame.init()
    pygame.display.set_caption('ball go')
    hzClock = pygame.time.Clock()

    # bg
    background = pygame.display.set_mode((bg_width, bg_height))

    # ball
    begin_x, begin_y = 50, bg_height / 2 - 30
    ball = Ball(begin_x, begin_y, 10, 0, 3, Blue)
    ball_2 = Ball(bg_width / 2, bg_height / 2, 10, 0, 5, Red)
    global flag
    flag = 0

    # target
    target = Target(bg_width - 20, 20, 5, Green)

    # mind
    d = m.sqrt(abs(ball.x - target.x) + abs(ball.y - target.y))

    inputs = numpy.array([[d]])
    goal = numpy.array([[0 for _ in range(len(jiao_list))]])
    weights = numpy.zeros((len(goal[0]), len(inputs[0]))) + 0.1

    step = 0.01

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # input
        d = m.sqrt(abs(ball.x - target.x) + abs(ball.y - target.y))  # 状态：小球离目标的距离
        print(d)

        inputs[0][0] = d

        # output
        outputs = weights.dot(inputs.T)
        # outputs = numpy.tanh(weights.dot(inputs.T))
        print(outputs)

        outputs_list = list(outputs)
        outputs_max_i = outputs_list.index(max(outputs_list))

        # 动一下（ 会有一个新的 d ）
        ball.jiao = jiao_list[outputs_max_i]
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # goal (reward)

        # 结果奖励

        if ball_collide(ball, ball_2):
            # 碰上球
            ball.x, ball.y = begin_x, begin_y   # 回到出发点
            result_collide_i = 1
        else:
            result_collide_i = 0

        if wall_collide(ball):
            # 碰墙
            ball.x, ball.y = begin_x, begin_y   # 回到出发点
            result_wall_i = 3
        else:
            result_wall_i = 2

        if d < 5:
            result_target_i = 0  # +5
        elif d < 10:
            result_target_i = 1  # +3
        elif d < 20:
            result_target_i = 2  # +2
        elif d < 30:
            result_target_i = 3  # -1
        else:
            result_target_i = 4  # -2

        reward = move_reward[outputs_max_i] \
                 + result_reward[result_collide_i]\
                 + result_reward[result_wall_i] \
                 + result_reward[result_target_i]

        for i in range(len(goal[0])):
            if i == outputs_max_i:
                goal[0][i] = reward
            else:
                goal[0][i] = 0

        # error
        errors = outputs - goal.T

        # change
        weights -= weights * errors * inputs * step

        # move
        flag = ball_enemy_move(ball_2, flag)

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, ball_2.color, (ball_2.x, ball_2.y), ball_2.r)

        # target
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


def rad(jiao):
    return m.pi / 180 * jiao


# 小球上下移动
def ball_enemy_move(ball, flag):
    if flag == 0:
        # 上移
        j = 3
        if ball.y - ball.r <= bg_height / 2 - 50:
            flag = 1
    else:
        j = 1
        if ball.y + ball.r >= bg_height / 2 + 50:
            flag = 0

    ball.jiao = jiao_list[j]
    step_y = m.sin(rad(ball.jiao)) * ball.step
    ball.y += step_y

    return flag


# 两个小球碰上
def ball_collide(ball_1, ball_2):
    if (ball_1.x - ball_2.x) ** 2 + (ball_1.y - ball_2.y) ** 2 <= (ball_1.r + ball_2.r) ** 2:
        # collide !!!
        return 1
    else:
        return 0


# 碰上边缘
def wall_collide(ball):
    if (0 + ball.r <= ball.x <= bg_width - ball.r) and (0 + ball.r <= ball.y <= bg_height - ball.r):
        return 0
    else:
        return 1


# def sig(x):
#     return 1 / (1 + numpy.exp(-x))

# def relu(x):
#     if x.any() >= 0:
#         return x
#     else:
#         return 0


if __name__ == '__main__':
    play()
