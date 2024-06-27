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
bg_width, bg_height = 700, 500

# fast
hz = 20

# reward
jiao_list = [0, 90, 180, 270]
move_reward = [1, 0, 0, 0]

result_reward = [3, 1, -1, -5]  # 5, 10, 15, 20   可能有一个区间的奖励值


# ball
class Ball:
    def __init__(self, x, y, r, jiao, step, d, color):
        self.x = x
        self.y = y
        self.r = r
        self.jiao = jiao
        self.step = step
        self.d = d
        self.color = color


class Line:
    def __init__(self, begin, end, width, color):
        self.begin = begin
        self.end = end
        self.width = width
        self.color = color


class Mind:
    def __init__(self, input_node, hidden_node, output_node):
        self.input_node = input_node
        self.hidden_node = hidden_node
        self.output_node = output_node



def play():
    # init
    pygame.init()
    pygame.display.set_caption('ball go')
    hzClock = pygame.time.Clock()

    # bg
    background = pygame.display.set_mode((bg_width, bg_height))

    # ball
    ball = Ball(25, bg_height / 2 + 30, 10, 0, 1, 0, Blue)

    # line
    line = Line((50, bg_height / 2), (bg_width - 50, bg_height / 2), 1, Black)

    # mind

    # d = abs(ball.y - line.begin[1])
    #
    # inputs = numpy.array([[d]])
    # goals = numpy.array([[0 for _ in range(len(jiao_list))]])
    # weights = numpy.zeros((len(goal[0]), len(inputs[0]))) + 0.1

    # mind
    mind = Mind(1, 5, 4)

    d = abs(ball.y - line.begin[1])

    inputs = numpy.array([[d]])
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
        d = abs(ball.y - line.begin[1])
        print(d)

        # inputs[0][0] = d
        #
        # # output
        # outputs = numpy.tanh(weights.dot(inputs.T))
        # outputs_list = list(outputs)
        # outputs_max_i = outputs_list.index(max(outputs_list))

        inputs[0][0] = d

        # output
        hiddens = w_ih.dot(inputs.T)
        outputs = w_ho.dot(hiddens)

        outputs_list = list(outputs)
        outputs_max_i = outputs_list.index(max(outputs_list))

        # 动一下（ 会有一个新的 d ）
        ball.jiao = jiao_list[outputs_max_i]
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # goal (reward)
        result_i = 0  # 结果奖励
        if d < 10:
            result_i = 0
        elif d < 20:
            result_i = 1
        elif d < 30:
            result_i = 2
        else:
            result_i = 3
        reward = move_reward[outputs_max_i] + result_reward[result_i]

        for i in range(len(goals[0])):
            if i == outputs_max_i:
                goals[0][i] = reward
            else:
                goals[0][i] = 0

        # # error
        # errors = outputs - goal.T
        #
        # # change
        # weights -= weights * errors * inputs * step

        # change
        e_ho = outputs - goals.T
        w_ho -= w_ho * e_ho * hiddens.T * step

        e_ih = w_ho.T.dot(e_ho)
        w_ih -= w_ih * e_ih * inputs * step

        # show
        background.fill(White)
        pygame.draw.line(background, line.color, line.begin, line.end, line.width)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)

        pygame.display.update()
        hzClock.tick(hz)


def rad(jiao):
    return m.pi / 180 * jiao


# def sig(x):
#     return 1 / (1 + numpy.exp(-x))

# def relu(x):
#     if x.any() >= 0:
#         return x
#     else:
#         return 0


if __name__ == '__main__':
    play()
