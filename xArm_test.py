# from xarm.wrapper.xarm_api import XArmAPI
from operator import pos
from conducter_test import main
from modules.drawXarm import DrawXarm
import config
from random import randrange, uniform
import logging


logging.basicConfig(level=logging.INFO)
N_REPEAT = 3


port = config.xarm1_port
drawbot = DrawXarm(port)

middle = [
    sum(config.xarm_x_extents)/2,
    sum(config.xarm_y_extents)/2,
    sum(config.xarm_z_extents)/2
]
middle_too_high = [
    sum(config.xarm_x_extents)/2,
    sum(config.xarm_y_extents)/2,
    config.xarm_z_extents[1] + 50
]
middle_down = [
    sum(config.xarm_x_extents)/2,
    sum(config.xarm_y_extents)/2,
    drawbot.z
]

pose1 = [300, 0, drawbot.z, drawbot.roll, drawbot.pitch, drawbot.yaw]
pose2 = [400, 200, drawbot.z, drawbot.roll, drawbot.pitch, drawbot.yaw]
pose_off_limit = [
    400, config.xarm_y_extents[1] + 50, drawbot.z,
    drawbot.roll, drawbot.pitch, drawbot.yaw
]


################
# Base functions
################
def test_arc():
    drawbot.move_to(*middle_down)
    drawbot.arc(pose1, pose2)
    drawbot.move_to(*middle_down)
    drawbot.arc(pose1, pose_off_limit)


def test_move_to():
    for _ in range(N_REPEAT):
        drawbot.move_to(*middle)
        drawbot.move_to(*middle_too_high)
        drawbot.move_to(*middle_down)


def test_tool_move():
    drawbot.tool_move('black')
    drawbot.tool_move('blue')
    drawbot.tool_move('red')
    drawbot.tool_move('green')
    drawbot.tool_move('undefined_colour')


#####################
# Ancillary functions
#####################
def test_move_y():
    drawbot.move_y()


def test_go_position_ready():
    drawbot.go_position_ready()


def test_go_position_ready():
    drawbot.go_position_draw()


def test_home():
    drawbot.home()


def test_go_draw():
    drawbot.move_to(*middle_down)
    drawbot.go_draw(middle_down[0] + 50, middle_down[1] + 50)


def test_go_draw_up():
    drawbot.move_to(*middle_down)
    drawbot.go_draw_up(50, 50, jump=30)



def test_go_random_draw():
    drawbot.go_random_draw()


def test_go_random_jump():
    drawbot.go_random_jump()


def test_position_move_by():
    drawbot.move_to(*middle_down)
    drawbot.position_move_by(50, 50, 20)


####################
# Notation functions
####################
def test_squiggle():
    squiggle_list = [
        (uniform(-5, 5), uniform(-5, 5), uniform(-5, 5))
        for _ in range(randrange(3, 9))
    ]
    for _ in range(N_REPEAT):
        drawbot.squiggle(squiggle_list)


def test_dot():
    drawbot.move_to(*middle_down)
    drawbot.dot()


def test_note_head():
    drawbot.move_to(*middle_down)
    drawbot.note_head(5)
    drawbot.note_head(1)
    drawbot.note_head(10)


def test_arc2D():
    drawbot.move_to(*middle_down)
    drawbot.arc2D(pose1, pose2)
    drawbot.move_to(*middle_down)
    drawbot.arc2D(pose1, pose_off_limit)


def test_draw_square():
    pass


if __name__ == "__main__":
    # test_move_to()
    # test_arc()
    # test_squiggle()
    test_home()
