# 球球学习：走直线
# 改进：动一下，加一行（一个状态行）

import pygame, sys, random, math as m
from pygame import *

# color
White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)
Blue = (0, 0, 255)

# bg
bg_width, bg_height = 700, 500

# fast
hz = 30

# reward
jiao_list = [0, 90, 180, 270]
move_reward = [2, 0, 0, 1]

result_reward = [3, -2, -3, -5]  # 5, 10, 15, 20


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
    ball = Ball(25, bg_height / 2 + 30, 10, 0, 1, 0, Blue)

    # line
    line = Line((50, bg_height / 2), (bg_width - 50, bg_height / 2), 1, Black)

    # table
    table = [[0 for _ in range(len(jiao_list))]]  # 开始就一行
    d_i_dict = {0: 0}

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # learn

        # move

        # t : 先动一下
        d_0 = abs(ball.y - line.begin[1])
        i, j = 0, 0

        print(d_0)

        if d_0 in d_i_dict.keys():
            # 找到了相同的状态
            i = d_i_dict[d_0]

            # 如果是刚才新增加的
            if table[i] == [0, 0, 0, 0]:
                j = random.randint(0, 3)  # 随机动一下
            else:
                j = table[i].index(max(table[i]))  # 选一个最大值动作
        else:
            j = random.randint(0, 3)  # 随机动一下

        ball.jiao = jiao_list[j]

        step_x = m.cos(rad(ball.jiao)) * ball.step
        step_y = m.sin(rad(ball.jiao)) * ball.step
        ball.x += step_x
        ball.y += step_y

        # t + 1 : 动完了，到下一个状态
        d_1 = abs(ball.y - line.begin[1])   # 下一个状态的距离

        # reward（ 动 到这个状态时的奖励）
        reward = move_reward[j]  # 动作奖励

        result_i = 0  # 结果奖励
        if d_1 < 5:
            result_i = 0
        elif d_1 < 10:
            result_i = 1
        elif d_1 < 15:
            result_i = 2
        else:
            result_i = 3
        reward += result_reward[result_i]

        # 更新
        if d_1 in d_i_dict.keys():
            # 找到（有下一个状态行）
            new_i = d_i_dict[d_1]
        else:
            # 找不到（没有，那就 table = max(0) + reward(move、result)  ）
            table.append([0 for _ in range(len(jiao_list))])  # 加一行
            new_i = len(table) - 1
            d_i_dict[d_1] = new_i

        table[i][j] = max(table[new_i]) + reward

        # print(d_i_dict)
        # print(table)

        # show
        background.fill(White)
        pygame.draw.line(background, line.color, line.begin, line.end, line.width)

        # ball
        pygame.draw.circle(background, ball.color, (ball.x, ball.y), ball.r)

        pygame.display.update()
        hzClock.tick(hz)


def rad(jiao):
    return m.pi / 180 * jiao


if __name__ == '__main__':
    play()