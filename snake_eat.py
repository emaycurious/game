# 贪吃蛇
# 吃红苹果，吃一个长长一点，吃到自己的尾巴 game over
import pygame, sys, random
from pygame import *

White = (255, 255, 255)
Red = (255, 0, 0)
Yellow = (255, 220, 0)
Orange = (250, 100, 0)
Blue = (0, 120, 200)
Green = (0, 180, 100)
Blue_Light = (0, 150, 220)

# background
bg_width = 400
bg_height = 400
bg_space = 40
bg_width_len = bg_width // bg_space
bg_height_len = bg_height // bg_space
bg_color = White

map = [
    [0 for _ in range( bg_height_len )] for _ in range( bg_width_len )
]

# dead
dead_x, dead_y = bg_width // 2, bg_height // 2
dead_color = Red

# snake
snake = []  # tail .... head
snake_head = []
snake_width = bg_space
snake_height = bg_space
snake_color = Blue_Light
snake_head_color = Blue
snake_walk = bg_space

# apple
apple_color = Yellow
apple_num = 0
apple_num_xy = [bg_space // 2, bg_space // 2]
apple_num_color = Orange

# eat
# if eat a apple, the tail no need to pop

hz = 20
wait_time = 3000


def move():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height), 0, 8 )
    background.fill( bg_color )
    pygame.display.set_caption( 'eat apple' )
    hzClock = pygame.time.Clock()

    snake.clear()
    snake.append( [bg_height_len // 2, bg_width_len // 2] )
    [apple_i, apple_j] = apple_random()
    global apple_num
    apple_num = 0
    touch_ok = 0

    while 1:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:

                [snake_head_i, snake_head_j] = snake_get_head()

                if event.key == K_UP:
                    touch_ok = check_dead( snake_head_i - 1, snake_head_j, background )
                    snake.append( [snake_head_i - 1, snake_head_j] )

                if event.key == K_DOWN:
                    touch_ok = check_dead( snake_head_i + 1, snake_head_j, background )
                    snake.append( [snake_head_i + 1, snake_head_j] )

                if event.key == K_LEFT:
                    touch_ok = check_dead( snake_head_i, snake_head_j - 1, background )
                    snake.append( [snake_head_i, snake_head_j - 1] )

                if event.key == K_RIGHT:
                    touch_ok = check_dead( snake_head_i, snake_head_j + 1, background )
                    snake.append( [snake_head_i, snake_head_j + 1] )

                if event.key == K_UP or event.key == K_DOWN or event.key == K_LEFT or event.key == K_RIGHT:

                    [snake_head_i, snake_head_j] = snake_get_head()

                    if [snake_head_i, snake_head_j] == [apple_i, apple_j]:
                        # eat
                        eat_apple( [apple_i, apple_j], background )
                        [apple_i, apple_j] = apple_random()
                    else:
                        # not eat
                        if snake_head_i < 0 or snake_head_i + 1 > bg_height_len or snake_head_j < 0 or snake_head_j + 1 > bg_width_len \
                                or touch_ok:
                            snake.pop()
                            touch_ok = 0
                        else:
                            snake.pop( 0 )

        background.fill( bg_color )     # refresh all things to white

        snake_show( snake, background )
        apple_show( background, apple_i, apple_j )
        apple_show_num( background )

        pygame.display.update()
        hzClock.tick( hz )  # give service to all of the fresh


def get_xy(i, j):
    # [i,j] -> [x,y]
    x = j * bg_space
    y = i * bg_space

    return [x, y]


def snake_show(snake, background):
    for s in snake:
        [s_x, s_y] = get_xy( s[0], s[1] )
        pygame.draw.rect( background, snake_color, (s_x, s_y, snake_width, snake_height) )

    [s_head_x, s_head_y] = get_xy( snake[-1][0], snake[-1][1] )
    pygame.draw.rect( background, snake_head_color, (s_head_x, s_head_y, snake_width, snake_height) )


def snake_get_head():
    snake_head = snake[-1]
    snake_head_i, snake_head_j = snake_head[0], snake_head[1]
    return [snake_head_i, snake_head_j]


def apple_random():
    # random a apple [i,j]
    # go around the map, get the left node, then random and chose first
    left = []
    for i in range( len( map ) ):
        for j in range( len( map[0] ) ):
            if [i, j] not in snake:
                left.append( [i, j] )
    random.shuffle( left )
    return left[0]


def apple_show(background, apple_i, apple_j):
    [apple_x, apple_y] = get_xy( apple_i, apple_j )
    pygame.draw.rect( background, apple_color, (apple_x, apple_y, bg_space, bg_space) )
    pygame.display.update()


def eat_apple(apple_ij, background):
    # when snack head [i,j] == apple [i,j], then apple delete
    global apple_num
    apple_num += 1
    pygame.draw.rect( background, bg_color, (apple_ij[0], apple_ij[1], bg_space, bg_space) )
    pygame.display.update()


def apple_show_num(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', 15 )
    textSurfaceObj = fontObj.render( 'apple : ' + str( apple_num ), True, apple_num_color )
    background.blit( textSurfaceObj, (apple_num_xy[0], apple_num_xy[1]) )


def check_dead(snake_head_i, snake_head_j, background):
    if len( snake ) > 1:
        for s in range( len( snake ) ):
            if [snake_head_i, snake_head_j] == snake[s]:
                if s == len( snake ) - 2:
                    return 1
                else:
                    snake_dead( background )
                    return 0
    return 0


def snake_dead(background):
    background.fill( bg_color )
    dead_show( background )
    apple_show_num( background )
    pygame.display.update()
    pygame.time.wait( wait_time )
    move()  # game again


def dead_show(background):
    fontObj = pygame.font.Font( 'freesansbold.ttf', 20 )
    textSurfaceObj = fontObj.render( 'Game Over !!!', False, dead_color, bg_color )
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (dead_x, dead_y)

    background.blit( textSurfaceObj, textRectObj )
    pygame.display.update()


if __name__ == '__main__':
    move()
