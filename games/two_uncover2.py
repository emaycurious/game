# 游戏 1 ：
# 一次翻开两块，颜色相同就留着，不同又盖上，直到翻开所以格子

import random
import pygame
from pygame import *
import sys

Red = (255, 0, 0)
Blue = (0, 0, 255)
Blue_Grey = (0, 200, 255)
Yellow = (255, 255, 0)
Green = (0, 255, 0)
Green_Qing = (100, 250, 200)
Green_Black = (10, 100, 10)
Brown = (200, 100, 0)
Orange = (250, 160, 0)
Purple = (255, 0, 255)
White = (255, 255, 255)
Black = (0, 0, 0)
Grey = (200, 200, 200)

Circle = 'circle'
Circle_fat = 'circle_fat'
Triangle = 'triangle'
Rectangle = 'rectangle'
Lintangle = 'lintangle'

colors = [Red, Blue, Blue_Grey, Yellow, Green, Green_Qing, Green_Black, Brown, Orange, Purple, Black]
shapes = [Circle, Circle_fat, Triangle, Rectangle, Lintangle]

map_row = 6
map_col = 6
assert map_row * map_col <= len( colors ) * len(
    shapes ) * 2, 'colors and shapes are too little for the map, check the len of colors and shapes'
assert map_row * map_col % 2 == 0, "the nodes of the map can't divide a half out, check the row and col"

x_margin = 20
y_margin = 20

node_width = 20
node_height = 20
node_space = 10

bg_width = (node_width + node_space * 2) * map_col + x_margin * 2
bg_height = (node_height + node_space * 2) * map_row + y_margin * 2

ag = 0
ag_x = bg_width - 30
ag_y = bg_height - 15

time_x, time_y = node_space // 2, node_space // 2
time_width, time_height = bg_width, node_space

move_hz = 20
time_hz = 60

mouse_touch = 0  # every time is 0 , then touch 2 twice
nodes_touch = []

win = 0  # how many 1 in the map2 ?


def play():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height), 0, 8 )
    background.fill( Grey )
    pygame.display.set_caption( '10 x 10' )
    clock = pygame.time.Clock()
    start_clock_sec_tick = pygame.time.get_ticks()

    map = get_map()
    map2 = get_map2()

    show_map( background )
    show_again( background )

    global mouse_touch, win
    win = 0

    while 1:

        # mouse touch
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONUP:  # mouse touch (x,y)

                mousex, mousey = event.pos
                # print( mousex, mousey )

                # touch (x,y) -> node (i,j)
                [i, j] = get_node( mousex, mousey )

                # uncover the node of map2
                if i is not None and j is not None and map2[i][j] == 0:

                    mouse_touch += 1

                    node = map[i][j]
                    map2[i][j] = 1
                    win += 1

                    if mouse_touch <= 2:
                        uncover_node( background, node, i, j )
                        nodes_touch.append( [i, j, node] )

                    # check
                    if mouse_touch == 2:

                        pygame.time.wait( 500 )

                        if nodes_touch[0][2] != nodes_touch[1][2]:  # not equal then cover
                            cover_node( map2, nodes_touch, background )

                        nodes_touch.clear()
                        mouse_touch = 0

                # again
                if mousex > ag_x and mousey > ag_y:
                    nodes_touch.clear()
                    mouse_touch = 0
                    play()

        # show time second
        end_clock_sec_tick = pygame.time.get_ticks()
        show_time( background, start_clock_sec_tick, end_clock_sec_tick )
        clock.tick( time_hz )

        # win
        if win < len( map ) * len( map[0] ):
            # if win, time stop
            pygame.display.update()


# get map
def get_map():
    # create diff colors and shapes nodes
    nodes = []

    for c in colors:
        for s in shapes:
            nodes.append( [c, s] )
    random.shuffle( nodes )

    # need how many nodes in the map ?
    map_len = map_row * map_col
    nodes_len = map_len // 2
    nodes_need = nodes[:nodes_len] * 2

    random.shuffle( nodes_need )

    # create map
    # insert nodes into the map
    map = []
    for i in range( map_row ):
        mr = []
        for j in range( map_col ):
            mr.append( nodes_need.pop( 0 ) )
        map.append( mr )

    # print( map )
    return map


def get_map2():
    # 0 cover all
    map2 = []
    for i in range( map_row ):
        mr = []
        for j in range( map_col ):
            mr.append( 0 )
        map2.append( mr )

    # print( map2 )
    return map2


def show_map(background):
    # show map2
    # get node (x,y)
    for i in range( map_row ):
        for j in range( map_col ):
            x = x_margin + (node_width + node_space * 2) * j + node_space
            y = y_margin + (node_width + node_space * 2) * i + node_space

            pygame.draw.rect( background, White, (x, y, node_width, node_height) )


def get_node(mousex, mousey):
    # mouse (x,y) -> node (i,j)
    for i in range( map_row ):
        for j in range( map_col ):
            x = x_margin + (node_width + node_space * 2) * j + node_space
            y = y_margin + (node_width + node_space * 2) * i + node_space

            node_rect = pygame.Rect( x, y, node_width, node_height )
            if node_rect.collidepoint( mousex, mousey ):        # this mouse is in this rect
                return [i, j]

    return [None, None]


def uncover_node(background, node, i, j):
    x = x_margin + (node_width + node_space * 2) * j + node_space
    y = y_margin + (node_width + node_space * 2) * i + node_space

    # first clear the origin rect node
    pygame.draw.rect( background, Grey, (x, y, node_width, node_height) )
    pygame.display.update()

    color, shape = node[0], node[1]
    if shape == Circle:
        pygame.draw.circle( background, color, (x + node_width // 2, y + node_height // 2), node_width // 2 )
    if shape == Circle_fat:
        pygame.draw.ellipse( background, color, (x, y + 3, node_width, node_height - 5) )  # fat cicle
    if shape == Triangle:
        pygame.draw.polygon( background, color,
                             ((x + node_width // 2, y), (x + node_width - 1, y + node_height - 5),
                              (x + 1, y + node_height - 5)) )
    if shape == Rectangle:
        pygame.draw.rect( background, color, (x, y, node_width, node_height) )
    if shape == Lintangle:
        pygame.draw.polygon( background, color,
                             ((x + node_width // 2, y + 1), (x + node_width - 1, y + node_height // 2),
                              (x + node_width // 2, y + node_height - 1), (x + 1, y + node_height // 2)) )

    pygame.display.update()


def cover_node(map2, nodes_touch, background):
    global win
    for node in nodes_touch:
        i, j = node[0], node[1]
        map2[i][j] = 0  # again can mouse touch ~
        win -= 1
        x = x_margin + (node_width + node_space * 2) * j + node_space
        y = y_margin + (node_width + node_space * 2) * i + node_space

        pygame.draw.rect( background, White, (x, y, node_width, node_height) )

    pygame.display.update()


def show_again(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', 10 )
    textSurfaceObj = fontObj.render( 'again', True, White )
    background.blit( textSurfaceObj, (ag_x, ag_y) )


def show_time(background, start_sec, end_sec):
    sec = (end_sec - start_sec) // 1000

    fontObj = pygame.font.Font( 'freesansbold.ttf', 10 )
    textSurfaceObj = fontObj.render( str( sec ) + " ' ", True, White )

    # first clear the origin rect node
    pygame.draw.rect( background, Grey, (time_x, time_y, time_width, time_height) )
    background.blit( textSurfaceObj, (time_x, time_y) )


if __name__ == '__main__':
    play()
