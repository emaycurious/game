# 小球用 神经网络 来学习 （调角度、速度）
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
bg_width, bg_height = 500, 300

# fast
hz = 30

# reward
jiao_list = [j for j in range(0, 360, 90)]
v_list = [i for i in range(7, 15)]  # 速度（和角度排列组合）
vj_list = []
for jiao in jiao_list:
    for v in v_list:
        vj_list.append([jiao, v])

move_reward = [0 for _ in range(len(vj_list))]
result_reward = [0, -1, 0, -0.5]  # (没碰上球，碰上球，不碰墙，碰墙)



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
    begin_x, begin_y = 50, bg_height / 2
    ball = Ball(begin_x, begin_y, 10, 0, 1, Blue)

    # ball_enemys_xy = [[50, 250], [90, 250], [100, 50],[170,70], [130, 200], [150, 150], [200, 100], [250, 200], [450, 20]]
    # ball_enemys = []
    # for b_xy in ball_enemys_xy:
    #     ball_enemys.append(Ball(b_xy[0], b_xy[1], 10, 0, 0, Red))

    global flag
    flag = 0

    # target
    target = Target(bg_width - 20, bg_height / 2, 10, Green)

    # mind
    mind = Mind(2, 10, len(vj_list))  # d => x,y

    inputs = numpy.array([[ball.x, ball.y]])
    goals = numpy.array([[0 for _ in range(len(vj_list))]])

    w_ih = numpy.zeros((mind.hidden_node, mind.input_node)) + 0.1
    w_ho = numpy.zeros((mind.output_node, mind.hidden_node)) + 0.1

    step = 0.01

    t = 0

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # input
        inputs = numpy.array([[ball.x, ball.y]])
        old_d = m.sqrt((ball.x - target.x)**2 + (ball.y - target.y)**2)  # 状态：小球离目标的距离

        # output
        hiddens = numpy.tanh(w_ih.dot(inputs.T))
        outputs = numpy.tanh(w_ho.dot(hiddens))

        outputs_list = list(outputs)
        outputs_max_i = outputs_list.index(max(outputs_list))

        # 动一下（ 会有一个新的 d ）
        ball.jiao = vj_list[outputs_max_i][0]  # 角度
        ball.step = vj_list[outputs_max_i][1]  # 速度
        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        new_d = m.sqrt((ball.x - target.x) ** 2 + (ball.y - target.y) ** 2)

        # goals (reward)

        # 结果奖励
        # if ball_many_collide(ball, ball_enemys):
        #     # 碰上球
        #     ball.x, ball.y = begin_x, begin_y  # 回到出发点
        #     result_collide_i = 1
        #     t += 1
        #     print(t)
        # else:
        #     result_collide_i = 0

        if wall_collide(ball):
            # 碰墙
            ball.x, ball.y = begin_x, begin_y  # 回到出发点
            result_wall_i = 3
            t += 1
            print(t)
        else:
            result_wall_i = 2

        # reward = move_reward[outputs_max_i] + result_reward[result_collide_i] + result_reward[result_wall_i]
        reward = result_reward[result_wall_i]

        # 靠近目标
        print(old_d- new_d)
        if old_d - new_d > 0:
            reward += 0.01

        for i in range(len(goals[0])):
            if i == outputs_max_i:
                goals[0][i] = reward
            else:
                goals[0][i] = 0

        # change
        e_ho = outputs - goals.T
        w_ho -= w_ho * e_ho * hiddens.T * step

        e_ih = w_ho.T.dot(e_ho)
        w_ih -= w_ih * e_ih * inputs * step

        # show
        background.fill(White)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)
        # show_enemy_ball(background, ball_enemys)

        # target
        pygame.draw.circle(background, target.color, (target.x, target.y), target.r)

        pygame.display.update()
        hzClock.tick(hz)


def show_enemy_ball(background, ball_enemys):
    for ball in ball_enemys:
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)


def rad(jiao):
    return m.pi / 180 * jiao


# 小球上下移动
def ball_enemy_move(ball, flag):
    if flag == 0:
        # 上移
        j = 6
        if ball.y - ball.r <= bg_height / 2 - 100:
            flag = 1
    else:
        j = 2
        if ball.y + ball.r >= bg_height / 2 + 100:
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


def ball_many_collide(ball_1, ball_enemys):
    for ball_2 in ball_enemys:
        if ball_collide(ball_1, ball_2):
            return 1
    return 0


# 碰上边缘
def wall_collide(ball):
    if (0 + ball.r <= ball.x <= bg_width - ball.r) and (0 + ball.r <= ball.y <= bg_height - ball.r):
        return 0
    else:
        return 1


if __name__ == '__main__':
    play()
