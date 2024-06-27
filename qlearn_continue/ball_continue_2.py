# 小球用 神经网络 来学习
# 少了第二个（动作-奖励）神经网络：奖励对动作的影响太直接了 ~

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
    def __init__(self, input_node, hidden_node, output_node):
        self.input_node = input_node
        self.hidden_node = hidden_node
        self.output_node = output_node


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
        print('+0.1')
        reward += 0.1
    if abs(ball.y - target.y) < abs(old_ball_xy[1] - target.y):
        reward += 0.1
        print('+0.1')
    if ball_collide(ball, target):
        reward += 500
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
    ball = Ball(begin_x, begin_y, 10, 0, 5, Blue)

    # target
    target = Ball(bg_width - 20, bg_height - 20, 10, 0, 1, Red)

    # mind
    mind = Mind(2, 6, 1)

    # mind init
    w_ih = numpy.zeros((mind.hidden_node, mind.input_node)) + 0.1
    w_ho = numpy.zeros((mind.output_node, mind.hidden_node)) + 0.1

    step = 0.001

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
        old_ball_xy = [ball.x, ball.y]
        ball.jiao = outputs[0][0] * 180  # (-1,1) * 180 => (-180,180)
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # reward
        reward = get_target_reward(old_ball_xy, ball, target)

        if wall_collide(ball):  # 如果碰到墙，回到出发点
            reward += -100
            ball.x, ball.y = begin_x, begin_y

        # change
        e_ho = outputs + reward
        w_ho += w_ho * e_ho * hiddens.T * step

        e_ih = w_ho.T.dot(e_ho)
        w_ih += w_ih * e_ih * inputs * step

        # print(w_ih)

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


if __name__ == '__main__':
    play()
