# 小球用 神经网络 来学习

import pygame, sys, random, math as m
import numpy
from pygame import *

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 500, 300

# fast
hz = 20

# move
jiao_list = [0, 90, 180, 270]

# reward
move_reward = [0, 0, 0, 0]


# target reward
# d_t = [i for i in range(10, 30)]  # 10,11,12....30
# result_reward = [i for i in range(22, -18, -2)]  #
# result_reward.append(-20)


# ball
class Ball:
    def __init__(self, x, y, r, jiao, step, color):
        self.x = x
        self.y = y
        self.r = r
        self.jiao = jiao
        self.step = step
        self.color = color


# class Line:
#     def __init__(self, begin, end, width, color):
#         self.begin = begin
#         self.end = end
#         self.width = width
#         self.color = color


class Mind:
    def __init__(self, input_node, hidden_node, output_node):
        self.input_node = input_node
        self.hidden_node = hidden_node
        self.output_node = output_node


def rad(jiao):
    return m.pi / 180 * jiao


def wall_collide(ball):
    if (0 + ball.r <= ball.x <= bg_width - ball.r) and (0 + ball.r <= ball.y <= bg_height - ball.r):
        return 0
    else:
        return 1


def get_target_reward(old_ball_xy, ball, target):
    reward = 0
    if abs(ball.x - target.x) < abs(old_ball_xy[0] - target.x):
        reward += 0.2
    if abs(ball.y - target.y) < abs(old_ball_xy[1] - target.y):
        reward += 0.1
    return reward


def ball_mind():
    pass


def play():
    # init
    pygame.init()
    pygame.display.set_caption('ball go')
    hzClock = pygame.time.Clock()

    # bg
    background = pygame.display.set_mode((bg_width, bg_height))

    # ball
    begin_x, begin_y = 30, bg_height / 2
    ball = Ball(begin_x, begin_y, 10, 0, 5, Blue)

    # target
    target = Ball(bg_width/2, bg_height - 20, 10, 0, 1, Red)

    # mind
    mind = Mind(2, 5, 4)

    # mind init
    inputs = numpy.array([[ball.x, ball.y]])
    goals = numpy.array([[0 for _ in range(len(jiao_list))]])

    w_ih = numpy.zeros((mind.hidden_node, mind.input_node)) + 0.1
    w_ho = numpy.zeros((mind.output_node, mind.hidden_node)) + 0.1

    step = 0.01

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # input
        inputs = numpy.array([[ball.x, ball.y]])

        # output
        hiddens = numpy.tanh(w_ih.dot(inputs.T))
        outputs = numpy.tanh(w_ho.dot(hiddens))

        # 动一下（ 会有一个新的 ball.x, ball.y ）
        old_ball_xy = (ball.x, ball.y)
        outputs_list = list(outputs)
        outputs_max_i = outputs_list.index(max(outputs_list))
        ball.jiao = jiao_list[outputs_max_i]
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # reward
        reward = get_target_reward(old_ball_xy, ball, target)

        if wall_collide(ball):  # 如果碰到墙，回到出发点
            reward += -5
            ball.x, ball.y = begin_x, begin_y

        print('reward:', reward)

        for i in range(len(goals[0])):
            if i == outputs_max_i:
                goals[0][i] = reward
            else:
                goals[0][i] = 0

        # change
        # e_ho = outputs - goals.T
        # print(goals)
        e_ho = goals.T
        w_ho += w_ho * e_ho * hiddens.T * step

        e_ih = w_ho.T.dot(e_ho)
        w_ih += w_ih * e_ih * inputs * step

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


if __name__ == '__main__':
    play()
