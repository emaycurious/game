# 数字 划龙道
# 在一个面板上，随机出现一组数字，只缺一个空，滑动这些数字，让它们按顺序归位

import pygame, sys, random
from pygame import *

White = (255, 255, 255)
Red = (255, 0, 0)
Green = (0, 200, 100)
Blue = (0, 0, 255)
Black = (0,0,0)

map_row = 4
map_col = 4
random_num = 50     # 30 is great ~

x_margin = 20
y_margin = 20

node_width = 50
node_height = 50
node_space = 3
node_color = Green

node_text_space = 17
node_text_size = 16
node_text_color = White

bg_width = (node_width + node_space * 2) * map_col + x_margin * 2
bg_height = (node_height + node_space * 2) * map_row + y_margin * 2
bg_name = 'number go!'
bg_color = White


ag_x = bg_width - 30
ag_y = bg_height - 15
ag_color = Green
ag_text_size = 10

new_x = node_space
new_mouse_x = new_x * 8
new_y = bg_height - 15
new_color = Green
new_text_size = 10

win_x = bg_width // 2
win_y = node_space * 3
win_color = Red
win_text_size = 15


move_hz = 300


def play():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height) )
    pygame.display.set_caption( bg_name )
    background.fill( bg_color )
    hzClock = pygame.time.Clock()

    # draw map
    map = get_map()
    map_win = get_map_again(map)

    # map random
    while 1:
        [block_i, block_j] = get_map_random( map )
        map_init = get_map_again(map)
        block_init = [block_i, block_j][:]

        # can't be the same as map init
        if map_init != map_win:
            break


    # show
    show_map( background, map )
    again_show(background)
    new_game_show(background)

    while 1:

        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # mouse move
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos

                # touch (x,y) -> node (node_i,node_j)
                [node_i, node_j] = get_node( mousex, mousey )

                if node_i is not None and node_j is not None and map[node_i][node_j] != 0:

                    if (node_i - 1 >= 0 and map[node_i - 1][node_j] == 0) or (
                            node_i + 1 < map_row and map[node_i + 1][node_j] == 0) or (
                            node_j - 1 >= 0 and map[node_i][node_j - 1] == 0) or (
                            node_j + 1 < map_col and map[node_i][node_j + 1] == 0):

                        [block_i, block_j] = map_move( background, map, node_i, node_j, block_i, block_j, hzClock )

                # again
                if mousex > ag_x and mousey > ag_y:
                    map = get_map_again(map_init)
                    [block_i,block_j] = block_init[:]
                    win_show(background,'          ')
                    show_map( background, map )

                # new
                if mousex < new_mouse_x and mousey > new_y:
                    play()

                # win
                if map == map_win:
                    win_show(background,'win !')

        pygame.display.update()


def get_map():
    map = []
    n = 1
    for i in range( map_row ):
        mr = []
        for j in range( map_col ):
            mr.append( n )
            n += 1
        map.append( mr )

    map[map_row - 1][-1] = 0
    return map


def get_map_random(map):
    [block_i, block_j] = [map_row - 1, map_col - 1]
    for i in range( random_num ):
        [block_i, block_j] = map_random( map, block_i, block_j )

    return [block_i, block_j]  # the init block [block_i, block_j]


def map_random(map, i, j):
    # random move
    # '0' move to somewhere ~

    choose = []
    if i - 1 >= 0:
        choose.append( [i - 1, j] )
    if i + 1 <= map_row - 1:
        choose.append( [i + 1, j] )
    if j - 1 >= 0:
        choose.append( [i, j - 1] )
    if j + 1 <= map_col - 1:
        choose.append( [i, j + 1] )

    # random and choose one place to move
    random.shuffle( choose )

    [node_i, node_j] = choose[0]

    # [node_i, node_j] => block [block_i,block_j], and [node_i, node_j] to new block
    map[i][j] = map[node_i][node_j]
    map[node_i][node_j] = 0

    return [node_i, node_j]  # block



def get_xy(i, j):
    # [i,j] -> [x,y]
    x = x_margin + (node_width + node_space * 2) * j + node_space
    y = y_margin + (node_width + node_space * 2) * i + node_space
    return [x, y]

def get_node(mousex, mousey):
    # mouse (x,y) -> node (i,j)
    for i in range( map_row ):
        for j in range( map_col ):
            [node_x, node_y] = get_xy( i, j )
            node_rect = pygame.Rect( node_x, node_y, node_width, node_height )
            if node_rect.collidepoint( mousex, mousey ):
                return [i, j]

    return [None, None]


def show_map(background, map):
    for node_i in range( map_row ):
        for node_j in range( map_col ):
            [node_x, node_y] = get_xy( node_i, node_j )
            if map[node_i][node_j]:
                pygame.draw.rect( background, node_color, (node_x, node_y, node_width, node_height) )
                text_move( background, map, node_i, node_j, node_x, node_y )
            else:
                pygame.draw.rect( background, bg_color, (node_x, node_y, node_width, node_height) )


def map_move(background, map, node_i, node_j, block_i, block_j, hzClock):
    [node_x, node_y] = get_xy( node_i, node_j )  # node
    [block_x, block_y] = get_xy( block_i, block_j )  # block

    # first cover the node, then show new node
    while 1:

        pygame.draw.rect( background, bg_color, (node_x, node_y, node_width, node_height) )

        if [node_i, node_j] == [block_i - 1, block_j]:
            node_y += 1
            if node_y >= block_y:
                break

        if [node_i, node_j] == [block_i + 1, block_j]:
            node_y -= 1
            if node_y <= block_y:
                break

        if [node_i, node_j] == [block_i, block_j - 1]:
            node_x += 1
            if node_x >= block_x:
                break

        if [node_i, node_j] == [block_i, block_j + 1]:
            node_x -= 1
            if node_x <= block_x:
                break

        # pygame.draw.rect( background, bg_color, (node_x, node_y, node_width, node_height) )
        pygame.draw.rect( background, node_color, (node_x, node_y, node_width, node_height) )

        text_move( background, map, node_i, node_j, node_x, node_y )

        pygame.display.update()
        hzClock.tick( move_hz )

    pygame.draw.rect( background, node_color, (node_x, node_y, node_width, node_height) )
    text_move( background, map, node_i, node_j, node_x, node_y )

    # map[][] move too
    map[block_i][block_j] = map[node_i][node_j]
    map[node_i][node_j] = 0

    return [node_i, node_j]


def text_move(background, map, node_i, node_j, node_x, node_y):
    fontObj = pygame.font.Font( 'freesansbold.ttf', node_text_size )
    text = str( map[node_i][node_j] )
    textObj = fontObj.render( text, True, node_text_color )
    background.blit( textObj, (node_x + node_text_space, node_y + node_text_space) )

def get_map_again(map):
    map_again = []
    for i in range(map_row):
        map_again.append(map[i][:])
    return map_again


def again_show(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', ag_text_size )
    textSurfaceObj = fontObj.render( 'again', True, ag_color )
    background.blit( textSurfaceObj, (ag_x, ag_y) )

def new_game_show(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', new_text_size )
    textSurfaceObj = fontObj.render( 'new', True, new_color )
    background.blit( textSurfaceObj, (new_x, new_y) )

def win_show(background,text):
    fontObj = pygame.font.Font( 'freesansbold.ttf', win_text_size )
    textSurfaceObj = fontObj.render( text, True, win_color, bg_color )
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (win_x, win_y)
    background.blit( textSurfaceObj, textRectObj)



if __name__ == '__main__':
    play()
