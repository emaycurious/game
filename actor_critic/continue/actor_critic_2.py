# 小球用 神经网络 来学习
#  (actor - critic）神经网络

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
        # self.step_x = step_x
        # self.step_y = step_y
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
    if ((ball.x - target.x) ** 2 + (ball.y - target.y) ** 2) < ((old_ball_xy[0] - target.x) ** 2 + (
            old_ball_xy[1] - target.y) ** 2):
        print('close')
        reward += 0.1
    else:
        print('far')
        reward -= 0.2

    # ball 如果碰到了目标
    if ball_collide(ball, target):
        reward += 10
        print('touch target !!!')
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
    target = Ball(bg_width / 2 + 100, 20, 10, 0, 0, Red)

    # mind

    # actor
    step_1 = 0.01
    actor = Mind(2, 5, 1, step_1)
    actor.w_ih = numpy.zeros((actor.hidden_node, actor.input_node)) + 0.1
    actor.w_ho = numpy.zeros((actor.output_node, actor.hidden_node)) + 0.1

    # critic_1
    step_2 = 0.01

    # t:
    critic_1 = Mind(actor.input_node, 10, actor.output_node, step_2)
    critic_1.w_ih = numpy.zeros((critic_1.hidden_node, critic_1.input_node)) + 0.1
    critic_1.w_ho = numpy.zeros((critic_1.output_node, critic_1.hidden_node)) + 0.1

    # t+1:
    critic_2 = Mind(critic_1.input_node, critic_1.hidden_node, critic_1.output_node, step_2)
    critic_2.w_ih = numpy.zeros((critic_2.hidden_node, critic_2.input_node)) + 0.1
    critic_2.w_ho = numpy.zeros((critic_2.output_node, critic_2.hidden_node)) + 0.1

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # actor
        actor.inputs = numpy.array([[ball.x, ball.y]])
        actor.hiddens = numpy.tanh(actor.w_ih.dot(actor.inputs.T))
        actor.outputs = numpy.tanh(actor.w_ho.dot(actor.hiddens))
        print()

        # 动一下（ 会有一个新的 ball.x, ball.y ）
        ball.jiao = (actor.outputs[0][0] * 180) + 180
        old_ball_xy = [ball.x, ball.y]
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # reward
        reward = get_target_reward(old_ball_xy, ball, target)
        if wall_collide(ball):  # 如果碰到墙，回到出发点
            reward -= 5
            ball.x, ball.y = begin_x, begin_y

        # critic_1
        # t:
        critic_1.inputs = actor.inputs
        print('t:',critic_1.inputs)
        critic_1.hiddens = numpy.tanh(critic_1.w_ih.dot(critic_1.inputs.T))
        critic_1.outputs = numpy.tanh(critic_1.w_ho.dot(critic_1.hiddens))

        # t+1:
        critic_2.inputs = numpy.array([[ball.x, ball.y]])
        print('t+1:',critic_2.inputs)
        critic_2.hiddens = numpy.tanh(critic_2.w_ih.dot(critic_2.inputs.T))
        critic_2.outputs = numpy.tanh(critic_2.w_ho.dot(critic_2.hiddens))

        # back
        # change critic:
        e_ho = (critic_1.outputs) - (critic_2.outputs + reward)
        critic_1.w_ho -= critic_1.w_ho * e_ho * critic_1.hiddens.T * critic_1.step
        e_ih = critic_1.w_ho.T.dot(e_ho)
        critic_1.w_ih -= critic_1.w_ih * e_ih * critic_1.inputs * critic_1.step

        # change actor:
        actor.w_ho -= actor.w_ho * e_ho * actor.hiddens.T * actor.step
        e_ih = actor.w_ho.T.dot(e_ho)
        actor.w_ih -= actor.w_ih * e_ih * actor.inputs * actor.step

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


if __name__ == '__main__':
    play()
