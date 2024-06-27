# 一个 net visual ~

import pygame, sys
from pygame import *


class Node:
    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.is_move = False
        self.offset_x = 0
        self.offset_y = 0
        self.color = color


# background init
White = (255, 255, 255)
Red = (255, 0, 0)
Blue = (0, 0, 255)
Green = (0, 255, 0)

bg_width = 600
bg_height = 500

hz = 30


def bg_init():
    pygame.init()
    background = pygame.display.set_mode((bg_width, bg_height))
    pygame.display.set_caption('draw_mind')
    hzClock = pygame.time.Clock()

    return background, hzClock


def play():
    # init
    background, hzClock = bg_init()

    layers = [2, 3, 4]
    begin_xy = [100, bg_height / 2]

    node_list, node_show_list = get_nodes(layers, begin_xy)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # mouse move
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标按下事件
                mouse_x, mouse_y = pygame.mouse.get_pos()

                for node in node_list:
                    if (mouse_x - node.x) ** 2 + (mouse_y - node.y) ** 2 <= node.r ** 2:
                        node.is_move = True
                        node.offset_x = mouse_x - node.x
                        node.offset_y = mouse_y - node.y

            elif event.type == pygame.MOUSEBUTTONUP:
                # 鼠标释放事件
                for node in node_list:
                    node.is_move = False
            elif event.type == pygame.MOUSEMOTION:
                # 鼠标移动事件
                for node in node_list:
                    if node.is_move:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        node.x = mouse_x - node.offset_x
                        node.y = mouse_y - node.offset_y

        background.fill(White)

        show_nodes_lines(background, node_show_list)

        pygame.display.update()
        hzClock.tick(hz)


def get_nodes(layers, begin_xy):
    node_list = []
    node_show_list = []
    x = begin_xy[0]

    for layer in layers:

        y = begin_xy[1]
        node_layer = []
        for _ in range(layer):
            # 画几个节点
            node = Node(x, y, 8, Blue)
            node_layer.append(node)
            node_list.append(node)
            y += 50  # 每一层 layer 节点之间，竖着画
        node_show_list.append(node_layer)
        x += 100  # 相邻两层 layer，横着画

    return node_list, node_show_list


def draw_a_line(background, node_1, node_2, width):
    pygame.draw.line(background, Red, (node_1.x, node_1.y), (node_2.x, node_2.y), width)


def show_nodes_lines(background, node_list):
    for i in range(len(node_list) - 1):
        layer_1 = node_list[i]
        layer_2 = node_list[i + 1]

        for j in range(len(layer_1)):
            node_1 = layer_1[j]  # layer_1 的一个节点 向 layer_2 的每个节点连线
            pygame.draw.circle(background, node_1.color, (node_1.x, node_1.y), node_1.r)

            for k in range(len(layer_2)):
                node_2 = layer_2[k]
                pygame.draw.circle(background, node_2.color, (node_2.x, node_2.y), node_2.r)
                draw_a_line(background, node_1, node_2, 2)


if __name__ == '__main__':
    play()
