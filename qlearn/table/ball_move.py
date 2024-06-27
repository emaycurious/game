# 球球学习：走直线

import pygame, sys, math as m
from pygame import *

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 500, 300

# fast
hz = 30

# reward
jiao_list = [270, 180, 90, 0]
move_reward = [0, -1, 0, 1]  # 0, 90, 180, 270
result_reward = [5, -1, -2, -3, -4, -5, -6, -7, -8, -9,-10]  # 0,2,4,6,8,10,12,14,16,18,20


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


def play():
    # init
    pygame.init()
    pygame.display.set_caption('ball to line')
    hzClock = pygame.time.Clock()

    # bg
    background = pygame.display.set_mode((bg_width, bg_height))

    # ball
    ball = Ball(25, bg_height / 2 + 10, 6, 0, 3, 0, Blue)

    # line
    line = Line((50, bg_height / 2), (bg_width - 50, bg_height / 2), 1, Black)

    # table
    table = [[0 for _ in range(len(move_reward))] for _ in range(len(result_reward))]

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # move

        # t
        d_0 = abs(ball.y - line.begin[1])
        i = get_d_i(d_0)
        print('i',i)


        j = table[i].index(max(table[i]))  # choose a move
        ball.jiao = jiao_list[j]

        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # t + 1
        d_1 = abs(ball.y - line.begin[1])

        reward = move_reward[j]  # reward

        result_i = get_d_i(d_1)
        reward += result_reward[result_i]

        new_i = get_d_i(d_1)
        table[i][j] = max(table[new_i]) + reward  # 更新

        print(table)

        # show
        background.fill(White)
        pygame.draw.line(background, line.color, line.begin, line.end, line.width)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)

        pygame.display.update()
        hzClock.tick(hz)


def rad(jiao):
    return m.pi / 180 * jiao


def get_d_i(d):
    i = int((d+1)/2)
    return i


if __name__ == '__main__':
    play()