# 俄罗斯方块
# 几种方块一个一个掉下来，上-转动方向，下左右-移动，掉到地面停下，
# 如果一排没有空隙，就消掉这一排，叠在上面的方块自动往下挤一排，
# 叠着叠着，有一个方块摸到顶了，就 gome over, 记下消掉多少行-得分

import pygame, sys, random
from pygame import *

White = (255, 255, 255)
Red = (255, 0, 0)
Black = (0, 0, 0)

map_row = 30
map_col = 20

node_space = 20
node_color = Red

bg_width = map_col * node_space
bg_height = map_row * node_space
bg_color = Black
bg_name = 'shape go!'

shape_space = node_space - 1

T = [
    [
        [0, 1, 0],
        [1, 1, 1],
    ],

    [
        [1, 0],
        [1, 1],
        [1, 0],
    ],
    [
        [1, 1, 1],
        [0, 1, 0],
    ],
    [
        [0, 1],
        [1, 1],
        [0, 1]
    ]
]

Z = [

    [
        [1, 1, 0],
        [0, 1, 1]
    ],

    [
        [0, 1],
        [1, 1],
        [1, 0]
    ],

]

S = [

    [
        [0, 1, 1],
        [1, 1, 0]
    ],

    [
        [1, 0],
        [1, 1],
        [0, 1]
    ],

]

J = [

    [
        [0, 1],
        [0, 1],
        [1, 1]
    ],

    [
        [1, 0, 0],
        [1, 1, 1]
    ],
    [
        [1, 1],
        [1, 0],
        [1, 0]
    ],

    [
        [1, 1, 1],
        [0, 0, 1]
    ],
]

L = [

    [
        [1, 0],
        [1, 0],
        [1, 1]
    ],

    [
        [1, 1, 1],
        [1, 0, 0]
    ],
    [
        [1, 1],
        [0, 1],
        [0, 1]
    ],

    [
        [0, 0, 1],
        [1, 1, 1]
    ],

]

I = [
    [
        [1],
        [1],
        [1],
        [1]
    ],

    [
        [1, 1, 1, 1],
    ],
]

O = [
    [
        [1, 1],
        [1, 1]
    ]
]

shapes = [T, Z, S, J, L, I, O]

hz_move_other = 5
hz_move_down = 5


def play():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height) )
    background.fill( bg_color )
    pygame.display.set_caption( bg_name )
    hzClock = pygame.time.Clock()

    # a rect jump down
    # show every shapes
    # collide other nodes

    # time to down, until draw on the bottom and stop
    # up to game over

    map = map_get()

    shape_choose = shape_random()
    round_index = shape_round_index( shape_choose )
    shape_one = shape_choose[round_index]

    old_node_i = 0
    old_node_j = first_out_random( shape_one )
    new_node_i = old_node_i
    new_node_j = old_node_j

    shape_choose_show( hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i, new_node_j )

    move_up = False
    move_down = False
    move_left = False
    move_right = False

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[K_UP]:
            # turn around
            pass

        if keys[K_DOWN]:

            # only down will not move
            if old_node_i + 1 <= map_row - len( shape_one ):  # check if is collide others or touch the bottom
                new_node_i = old_node_i + 1

                shape_choose_show( hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i,
                                   new_node_j )
                old_node_i = new_node_i

        if keys[K_LEFT]:

            if old_node_j - 1 >= 0:
                new_node_j = old_node_j - 1
                shape_choose_show( hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i,
                                   new_node_j )
                old_node_j = new_node_j

        if keys[K_RIGHT]:

            if old_node_j + 1 <= map_col - len( shape_one[0] ):
                new_node_j = old_node_j + 1
                new_map_j = new_node_j + len( shape_one[0] ) - 1

                if map[new_node_i][new_map_j] == 0:

                    shape_choose_show( hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i,
                                       new_node_j )
                    old_node_j = new_node_j


        [new_node_i,old_node_i] = shape_down_time(hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i,
                                                   new_node_j)
        pygame.display.update()
        hzClock.tick( hz_move_down )


def map_get():
    map = []
    for i in range( map_row ):
        m = []
        for j in range( map_col ):
            m.append( 0 )
        map.append( m )

    return map


def shape_random():
    random.shuffle( shapes )
    return shapes[0]


def shape_round_index(shape_choose):
    index = random.randint( 0, len( shape_choose ) - 1 )
    return index


def first_out_random(shape_one):
    j = random.randint( 0, map_col - len( shape_one[0] ) - 1 )
    return j


def get_xy(node_i, node_j):
    node_x = node_j * node_space
    node_y = node_i * node_space
    return [node_x, node_y]


def shape_delete(background, old_node_i, old_node_j):
    [old_node_x, old_node_y] = get_xy( old_node_i, old_node_j )
    pygame.draw.rect( background, bg_color, (old_node_x, old_node_y, shape_space, shape_space) )


def shape_new(background, new_node_i, new_node_j):
    [new_node_x, new_node_y] = get_xy( new_node_i, new_node_j )
    pygame.draw.rect( background, node_color, (new_node_x, new_node_y, shape_space, shape_space) )


def shape_choose_show(hzClock,background,map, shape_one, old_node_i, old_node_j, new_node_i, new_node_j):
    # background,T, i
    # shape[round_index]:
    # [
    #         [0, 1, 0],
    #         [1, 1, 1],
    #         [0, 0, 0],
    #         [0, 0, 0]
    # ],

    # delete old
    delete_flag = 0
    for s_i in range( len( shape_one ) ):
        for s_j in range( len( shape_one[0] ) ):

            # if touch map == 1 ,then don't need to delete
            shape_real_new_i = s_i + new_node_i
            shape_real_new_j = s_j + new_node_j

            if map[shape_real_new_i][shape_real_new_j] == 0:

                if shape_one[s_i][s_j]==1:
                    shape_real_old_i = s_i + old_node_i
                    shape_real_old_j = s_j + old_node_j

                    shape_delete( background, shape_real_old_i, shape_real_old_j )
                    map[s_i][s_j] = 0
                    delete_flag = 1

    # show new
    if delete_flag:     # if delete, then new
        for s_i in range( len( shape_one ) ):
            for s_j in range( len( shape_one[0] ) ):
                if shape_one[s_i][s_j]:
                    shape_real_new_i = s_i + new_node_i
                    shape_real_new_j = s_j + new_node_j

                    shape_new( background, shape_real_new_i, shape_real_new_j )
                    map[s_i][s_j] = 1

    pygame.display.update()
    hzClock.tick(hz_move_other)

# def shape_touch_others(map,s_i, s_j, shape_one):
#     # touch the bottom then the shape of map[i][j] = 1
#     # shape_one:
#     # [
#     #         [0, 1, 0],
#     #         [1, 1, 1],
#     # ]
#





def shape_down_time(hzClock,background, map, shape_one, old_node_i, old_node_j, new_node_i,new_node_j):

    # pygame.time.wait(500)
    # if touch left or right, then wait for a sec, then fall down

    if old_node_i + 1 <= map_row - len( shape_one ):  # check if is collide others or touch the bottom
        new_node_i = old_node_i + 1

        shape_choose_show( hzClock,background, map, shape_one, old_node_i, old_node_j, new_node_i,
                           new_node_j )
        old_node_i = new_node_i

    # pygame.time.wait(100)


    return [new_node_i,old_node_i]





if __name__ == '__main__':
    play()
