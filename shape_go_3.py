# 俄罗斯方块
# 几种方块一个一个掉下来，上-转动方向，下左右-移动，掉到地面停下，
# 如果一排没有空隙，就消掉这一排，叠在上面的方块自动往下挤一排，
# 叠着叠着，有一个方块摸到顶了，就 gome over, 记下消掉多少行-得分

import pygame, sys, random
# import msvcrt
from pygame import *

Red = (255, 0, 0)
Blue = (0, 0, 255)
Yellow = (255, 255, 0)
Green = (0, 255, 0)
Purple = (255, 0, 255)
White = (255, 255, 255)
Black = (0, 0, 0)

colors = [Red, Blue, Yellow, Green, Purple]

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

map_row = 24
map_col = 16

node_space = 20
node_color = Red

bg_width = map_col * node_space
bg_height = map_row * node_space
bg_color = Black
bg_name = 'shape go!'

move_still_time = 100
down_time = 500

time_x, time_y = node_space // 2, node_space // 2
time_width, time_height = bg_width, node_space

dead_x, dead_y = bg_width // 2, bg_height // 2
dead_color = Red
wait_time = 5000

shape_space = node_space - 1

hz = 25


def play():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height) )
    background.fill( bg_color )
    pygame.display.set_caption( bg_name )
    hzClock = pygame.time.Clock()

    start_clock_sec_tick = pygame.time.get_ticks()

    map = map_get()

    # a shape out
    [shape_choose, shape_one, shape_color, round_index, node_i, node_j] = shape_out()

    # pygame.mixer.music.load( '../music/tetrisb.mid' )
    # pygame.mixer.music.play( -1 )

    move_left, move_right, move_down = 0, 0, 0
    last_move_time = pygame.time.get_ticks()
    last_down_time = pygame.time.get_ticks()

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                if event.key == K_UP and not shape_touch( map, node_i, node_j, shape_one ):
                    # turn around
                    round_index = (round_index + 1) % len( shape_choose )
                    if not shape_touch( map, node_i, node_j, shape_choose[round_index] ):
                        shape_one = shape_choose[round_index]

                if event.key == K_LEFT and not shape_touch( map, node_i, node_j - 1, shape_one ):
                    if node_j - 1 >= 0:
                        node_j -= 1
                        move_left = 1

                if event.key == K_RIGHT and not shape_touch( map, node_i, node_j + 1, shape_one ):
                    if node_j + 1 <= map_col - len( shape_one[0] ):
                        node_j += 1
                        move_right = 1

                if event.key == K_DOWN and not shape_touch( map, node_i + 1, node_j, shape_one ):
                    if node_i + 1 <= map_row - len( shape_one ):
                        node_i += 1
                        move_down = 1

                last_move_time = pygame.time.get_ticks()

            elif event.type == KEYUP:
                move_left, move_right, move_down = 0, 0, 0
                last_move_time = pygame.time.get_ticks()

        # if move still
        if pygame.time.get_ticks() - last_move_time > move_still_time:

            if move_left:
                if node_j - 1 >= 0 and not shape_touch( map, node_i, node_j - 1, shape_one ):
                    node_j -= 1
            if move_right:
                if node_j + 1 <= map_col - len( shape_one[0] ) and not shape_touch( map, node_i, node_j + 1,
                                                                                    shape_one ):
                    node_j += 1
            if move_down:
                if node_i + 1 <= map_row - len( shape_one ) and not shape_touch( map, node_i + 1, node_j, shape_one ):
                    node_i += 1

            last_move_time = pygame.time.get_ticks()

        # draw background
        background.fill( bg_color )

        # show this shape
        bg_draw_shapes( background, map )
        shape_show( background, shape_one, shape_color, node_i, node_j )

        # get end time
        end_clock_sec_tick = pygame.time.get_ticks()

        # go down ( if it's time to down )
        if pygame.time.get_ticks() - last_down_time > down_time:

            if node_i + 1 <= map_row - len( shape_one ) and not shape_touch( map, node_i + 1, node_j, shape_one ):
                node_i += 1
                # show this shape
                bg_draw_shapes( background, map )
                shape_show( background, shape_one, shape_color, node_i, node_j )
            else:
                # draw map [1,color]
                map_draw_shapes( map, shape_one, shape_color, node_i, node_j )

                # if touch up, game over !
                if touch_up( map ):
                    pygame.mixer.music.stop()
                    show_time( background, start_clock_sec_tick, end_clock_sec_tick )
                    game_over_show( background )
                else:
                    # a shape out
                    [shape_choose, shape_one, shape_color, round_index, node_i, node_j] = shape_out()

            last_down_time = pygame.time.get_ticks()

        # show time sec
        show_time( background, start_clock_sec_tick, end_clock_sec_tick )

        # refresh
        pygame.display.update()
        hzClock.tick( hz )



def map_get():
    map = []  # [ [0,bg_color],[1,Red],[1,Yellow],... ]
    for i in range( map_row ):
        m = []
        for j in range( map_col ):
            m.append( [0, bg_color] )
        map.append( m )

    return map


def map_draw_shapes(map, shape_one, shape_color, node_i, node_j):
    for s_i in range( len( shape_one ) ):
        for s_j in range( len( shape_one[0] ) ):
            if shape_one[s_i][s_j] == 1:
                node_real_i = s_i + node_i
                node_real_j = s_j + node_j
                map[node_real_i][node_real_j] = [1, shape_color]


def bg_draw_shapes(background, map):
    for i in range( map_row ):

        if one_line_full( i, map ):
            map.pop( i )
            # then insert one line on the top
            m = []
            for j in range( map_col ):
                m.append( [0, bg_color] )
            map.insert( 0, m )

        for j in range( map_col ):
            # [1,color] - every node
            [x, y] = get_xy( i, j )
            pygame.draw.rect( background, map[i][j][1], (x, y, shape_space, shape_space) )


def color_random():
    random.shuffle( colors )
    return colors[0]


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


def shape_out():
    shape_choose = shape_random()
    round_index = shape_round_index( shape_choose )
    shape_one = shape_choose[round_index]
    shape_color = color_random()

    node_i = 0
    node_j = first_out_random( shape_one )

    return [shape_choose, shape_one, shape_color, round_index, node_i, node_j]


def shape_show(background, shape_one, shape_color, node_i, node_j):
    for s_i in range( len( shape_one ) ):
        for s_j in range( len( shape_one[0] ) ):
            if shape_one[s_i][s_j] == 1:
                node_real_i = s_i + node_i
                node_real_j = s_j + node_j
                if 0 <= node_real_i < map_row and 0 <= node_real_j < map_col:
                    [node_x, node_y] = get_xy( node_real_i, node_real_j )
                    pygame.draw.rect( background, shape_color, (node_x, node_y, shape_space, shape_space) )


def shape_touch(map, node_i, node_j, shape_one):
    for s_i in range( len( shape_one ) ):
        for s_j in range( len( shape_one[0] ) ):
            if shape_one[s_i][s_j] == 1:
                node_real_i = s_i + node_i
                node_real_j = s_j + node_j

                if 0 <= node_real_i < map_row and 0 <= node_real_j < map_col:
                    if map[node_real_i][node_real_j][0] == 1:
                        return True  # touched !
                else:
                    return True
    return False


def one_line_full(i, map):
    # if one line is full, then delete this line  ( i - this line index )
    for j in range( len( map[0] ) ):
        if map[i][j][0] == 0:
            return False

    return True  # this line all are 1


def touch_up(map):
    # game over !
    for j in range( map_col ):
        # if first line have a color node, then game over !
        if map[0][j][0] == 1:
            return True
    return False


def show_time(background, start_sec, end_sec):
    sec = (end_sec - start_sec) // 1000

    fontObj = pygame.font.Font( 'freesansbold.ttf', 15 )
    textSurfaceObj = fontObj.render( str( sec ) + " ' ", True, White )

    background.blit( textSurfaceObj, (time_x, time_y) )


def game_over_show(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', 20 )
    textSurfaceObj = fontObj.render( 'Game Over !!!', False, dead_color, bg_color )
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (dead_x, dead_y)
    background.blit( textSurfaceObj, textRectObj )

    pygame.display.update()
    pygame.time.wait( wait_time )
    play()  # game again


if __name__ == '__main__':
    play()
