# a traveler go every node
import pygame, sys, random
from pygame import *

# background init
White = (255, 255, 255)
Red = (255, 0, 0)
Blue = (0, 0, 255)
Green = (0, 255, 0)
Yellow = (255, 255, 0)
Black = (0, 0, 0)

bg_width = 600
bg_height = 500
hz = 30

# robot
begin_x, begin_y = 0, 0
robot_width, robot_height = 20, 20
robot_space = 40
move_step = 1


class Robot:
    def __init__(self, color, x, y, width, height):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_move = False
        self.offset_x = 0
        self.offset_y = 0


def play(nodes, ways, pass_nodes):
    # init
    background, hzClock = bg_init()

    # robot init
    robot_list = robot_create( nodes )

    # begin
    is_begin = False

    # create a new robot
    robot_1 = Robot( Blue, bg_width - robot_width, bg_height - robot_height, robot_width, robot_height )
    robot_2 = robot_list[pass_nodes.pop( 0 )]

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # mouse move
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 鼠标按下事件
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # old robots
                for robot in robot_list:
                    if robot.x <= mouse_x <= robot.x + robot.width and robot.y <= mouse_y <= robot.y + robot.height:
                        robot.is_move = True
                        robot.offset_x = mouse_x - robot.x
                        robot.offset_y = mouse_y - robot.y

                # new robot
                if robot_1.x <= mouse_x <= robot_1.x + robot_1.width and robot_1.y <= mouse_y <= robot_1.y + robot_1.height:
                    robot_1.is_move = True
                    robot_1.offset_x = mouse_x - robot_1.x
                    robot_1.offset_y = mouse_y - robot_1.y

            elif event.type == pygame.MOUSEBUTTONUP:
                # 鼠标释放事件
                # old robots
                for robot in robot_list:
                    robot.is_move = False
                # new robot
                robot_1.is_move = False

            elif event.type == pygame.MOUSEMOTION:
                # 鼠标移动事件
                # old robots
                for robot in robot_list:
                    if robot.is_move:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        robot.x = mouse_x - robot.offset_x
                        robot.y = mouse_y - robot.offset_y
                # new robots
                if robot_1.is_move:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    robot_1.x = mouse_x - robot_1.offset_x
                    robot_1.y = mouse_y - robot_1.offset_y

            elif event.type == pygame.KEYDOWN:
                if event.key == K_RIGHT:
                    is_begin = True

        # a robot move to another robot

        # show bg
        background.fill( White )

        # show robots
        show_robots( background, robot_list )
        pygame.draw.rect( background, robot_1.color,
                          (robot_1.x, robot_1.y, robot_1.width, robot_1.height) )

        # show line
        show_line( background, robot_list, ways )

        # move robots
        if is_begin:

            # show robot move
            robot_rect_1 = pygame.Rect( robot_1.x, robot_1.y, robot_1.width, robot_1.height )
            robot_rect_2 = pygame.Rect( robot_2.x, robot_2.y, robot_2.width, robot_2.height )

            if robot_rect_1.colliderect( robot_rect_2 ):
                robot_1 = Robot( Blue, robot_2.x, robot_2.y, robot_2.width, robot_2.height )
                if len( pass_nodes ) > 0:
                    robot_2 = robot_list[pass_nodes.pop( 0 )]
            else:
                if robot_2.x == robot_1.x:
                    if robot_2.y - robot_1.y > 0:
                        robot_1.y += move_step
                    else:
                        robot_1.y -= move_step
                else:

                    x_y = abs( (robot_2.y - robot_1.y) / (robot_2.x - robot_1.x) )

                    # x 每移动一步，y 移动 x 的比例步

                    if robot_2.x - robot_1.x > 0:
                        robot_1.x += move_step
                    else:
                        robot_1.x -= move_step

                    if robot_2.y - robot_1.y > 0:
                        robot_1.y += x_y * move_step
                    else:
                        robot_1.y -= x_y * move_step

        pygame.display.update()
        hzClock.tick( hz )


# background init
def bg_init():
    pygame.init()
    background = pygame.display.set_mode( (bg_width, bg_height) )
    pygame.display.set_caption( 'travel' )
    hzClock = pygame.time.Clock()

    return background, hzClock


# robot create
def robot_create(nodes):
    global begin_x, begin_y
    robot_list = []  # 0 - robot_0 , 1 - robot_1, 2 - robot_2 ...

    for _ in nodes:
        robot = Robot( Green, begin_x, begin_y, robot_width, robot_height )
        robot_list.append( robot )
        begin_x, begin_y = begin_x + robot_space, begin_y + robot_space

    return robot_list


# draw robots
def show_robots(background, robot_list):
    for i in range( len( robot_list ) ):
        pygame.draw.rect( background, robot_list[i].color,
                          (robot_list[i].x, robot_list[i].y, robot_list[i].width, robot_list[i].height) )
        # number
        fontObj = pygame.font.Font( 'freesansbold.ttf', 15 )
        text_show = fontObj.render( str( i ), True, Red )
        background.blit( text_show, (robot_list[i].x, robot_list[i].y) )


# draw line
def show_line(background, robot_list, ways):
    for i in range( len( ways ) ):
        for j in range( i + 1, len( ways[0] ) ):
            if ways[i][j] > 0:
                pygame.draw.line( background, Black, (
                    robot_list[i].x + robot_list[i].width / 2, robot_list[i].y + robot_list[i].height / 2),
                                  (robot_list[j].x + robot_list[j].width / 2,
                                   robot_list[j].y + robot_list[j].height / 2), 2 )
                # long
                center_x = (robot_list[i].x + robot_list[j].x) / 2
                center_y = (robot_list[i].y + robot_list[j].y) / 2

                fontObj = pygame.font.Font( 'freesansbold.ttf', 15 )
                text_show = fontObj.render( str( ways[i][j] ), True, Red )
                background.blit( text_show, (center_x, center_y) )


# travel
def travel_better(nodes, ways):
    random.shuffle( nodes )

    min_node = nodes[0]
    pass_nodes = []

    while len( pass_nodes ) < len( nodes ):

        line = ways[min_node]

        for i in range( len( line ) ):
            if i in pass_nodes:
                line[i] = 100

        way_min = min( line )
        min_node = line.index( way_min )
        pass_nodes.append( min_node )

    print( pass_nodes)
    return pass_nodes

def sum_way_len(pass_nodes,ways):
    sum = 0

    if len( pass_nodes ) >= 2:
        begin = 0
        end = begin + 1
        while end <= len( pass_nodes ) - 1:
            sum += ways[pass_nodes[begin]][pass_nodes[end]]
            begin += 1
            end += 1
    return sum


if __name__ == '__main__':
    nodes = [0, 1, 2, 3]
    # ways = [
    #     [100, 2, 6, 5],
    #     [2, 100, 4, 4],
    #     [6, 4, 100, 1],
    #     [5, 4, 1, 100]
    # ]

    ways = [
        [100, 10, 5, 9],
        [10, 100, 6, 9],
        [5, 6, 100, 3],
        [9, 9, 3, 100]
    ]

    old_nodes = [0, 1, 2, 3]
    # old_ways = [
    #     [100, 2, 6, 5],
    #     [2, 100, 4, 4],
    #     [6, 4, 100, 1],
    #     [5, 4, 1, 100]
    # ]

    old_ways = [
        [100, 10, 5, 9],
        [10, 100, 6, 9],
        [5, 6, 100, 3],
        [9, 9, 3, 100]
    ]

    pass_nodes = travel_better( old_nodes, old_ways )
    print(sum_way_len(pass_nodes,ways))

    play( nodes, ways, pass_nodes )
