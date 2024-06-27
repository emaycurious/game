# 小球用 神经网络 来学习
# 加上（动作-奖励）神经网络

import pygame, sys, random, math as m
import numpy
from pygame import *

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 500, 700

# fast
hz = 20


# ball
class Ball:
    def __init__(self, x, y, r, jiao, step, color):
        self.x = x
        self.y = y
        self.r = r
        self.jiao = jiao
        self.step = step
        self.color = color


class Mind:
    def __init__(self, input_node, hidden_node, output_node, step, inputs=None, hiddens=None, outputs=None, w_ih=None,
                 w_ho=None):
        self.input_node = input_node
        self.hidden_node = hidden_node
        self.output_node = output_node

        self.inputs = inputs
        self.hiddens = hiddens
        self.outputs = outputs

        self.step = step
        self.w_ih = w_ih
        self.w_ho = w_ho


def rad(jiao):
    return m.pi / 180 * jiao


# 碰上墙
def wall_collide(ball):
    if (0 + ball.r <= ball.x <= bg_width - ball.r) and (0 + ball.r <= ball.y <= bg_height - ball.r):
        return 0
    else:
        return 1


# 两个小球碰上
def ball_collide(ball_1, ball_2):
    if (ball_1.x - ball_2.x) ** 2 + (ball_1.y - ball_2.y) ** 2 <= (ball_1.r + ball_2.r + 100) ** 2:
        # collide !!!
        return 1
    else:
        return 0


def get_target_reward(old_ball_xy, ball, target):
    reward = 0
    if abs(ball.x - target.x) < abs(old_ball_xy[0] - target.x):
        reward += 0.01
    else:
        reward -= 0.02
    if abs(ball.y - target.y) < abs(old_ball_xy[1] - target.y):
        reward += 0.01
    else:
        reward -= 0.02

    if ball_collide(ball, target):
        reward += 2000
        print('yeah!!!!!!!!!! + 500 ')
    return reward


def play():
    # init
    pygame.init()
    pygame.display.set_caption('ball go')
    hzClock = pygame.time.Clock()

    # bg
    background = pygame.display.set_mode((bg_width, bg_height))

    # ball
    begin_x, begin_y = 30, bg_height / 2
    ball = Ball(begin_x, begin_y, 10, 0, 10, Blue)

    # target
    target = Ball(bg_width - 20, bg_height - 20, 10, 0, 1, Red)

    # mind

    # mind_1
    step_1 = 0.01
    mind_1 = Mind(2, 10, 1, step_1)
    mind_1.w_ih = numpy.zeros((mind_1.hidden_node, mind_1.input_node)) + 0.1
    mind_1.w_ho = numpy.zeros((mind_1.output_node, mind_1.hidden_node)) + 0.1

    # mind_2
    step_2 = 0.01
    mind_2 = Mind(1, 10, 1, step_2)
    mind_2.w_ih = numpy.zeros((mind_2.hidden_node, mind_2.input_node)) + 0.1
    mind_2.w_ho = numpy.zeros((mind_2.output_node, mind_2.hidden_node)) + 0.1

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # go

        # mind_1
        mind_1.inputs = numpy.array([[ball.x, ball.y]])
        mind_1.hiddens = numpy.tanh(mind_1.w_ih.dot(mind_1.inputs.T))
        mind_1.outputs = numpy.tanh(mind_1.w_ho.dot(mind_1.hiddens))

        # mind_2
        mind_2.inputs = mind_1.outputs.T
        mind_2.hiddens = numpy.tanh(mind_2.w_ih.dot(mind_2.inputs.T))
        mind_2.outputs = numpy.tanh(mind_2.w_ho.dot(mind_2.hiddens))

        print(mind_2.outputs)

        # 动一下（ 会有一个新的 ball.x, ball.y ）
        old_ball_xy = [ball.x, ball.y]
        ball.jiao = mind_1.outputs[0][0] * 180 + 180 # (-1,1) * 180 => (-180,180) + 180 => (0,360)
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # reward
        reward = get_target_reward(old_ball_xy, ball, target)
        if wall_collide(ball):  # 如果碰到墙，回到出发点
            reward += -100
            ball.x, ball.y = begin_x, begin_y

        # back

        # mind_2
        e_ho = mind_2.outputs + 1
        mind_2.w_ho -= mind_2.w_ho * e_ho * mind_2.hiddens.T * mind_2.step

        e_ih = mind_2.w_ho.T.dot(e_ho)
        mind_2.w_ih -= mind_2.w_ih * e_ih * mind_2.inputs * mind_2.step

        # mind_1
        e_ho = mind_2.w_ih.T.dot(e_ih)
        mind_1.w_ho -= mind_1.w_ho * e_ho * mind_1.hiddens.T * mind_1.step

        e_ih = mind_1.w_ho.T.dot(e_ho)
        mind_1.w_ih -= mind_1.w_ih * e_ih * mind_1.inputs * mind_1.step

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


if __name__ == '__main__':
    play()
