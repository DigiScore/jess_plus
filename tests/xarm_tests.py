####################################################
# Running the tests with pytest (pip install pytest)
####################################################
# Run the tests in the cmd from the root folder:
# - running all the tests: $ tests/pytest xArm_test.py
# - running a specific test: $ pytest tests/xArm_test.py::test_function

from modules.drawXarm import DrawXarm
import config
from random import randrange, uniform
import logging


logging.basicConfig(level=logging.INFO)


port = config.xarm1_port
drawbot = DrawXarm(port)

middle = [
    sum(config.xarm_x_extents)/2,
    sum(config.xarm_y_extents)/2,
    sum(config.xarm_z_extents)/2
]
offlimit = [
    sum(config.xarm_x_extents)/2,
    sum(config.xarm_y_extents)/2,
    config.xarm_z_extents[1] + 70
]
pose1 = [drawbot.draw_position[0]+50, drawbot.draw_position[1], drawbot.z,
         drawbot.roll, drawbot.pitch, drawbot.yaw]
pose2 = [drawbot.draw_position[0], drawbot.draw_position[1]+50, drawbot.z,
         drawbot.roll, drawbot.pitch, drawbot.yaw]
pose3 = [drawbot.draw_position[0], drawbot.draw_position[1]+100, drawbot.z,
         drawbot.roll, drawbot.pitch, drawbot.yaw]


################
# Base functions
################
def test_arc():
    drawbot.go_position_draw()
    drawbot.arc(pose1, pose2)
    drawbot.go_position_draw()
    drawbot.arc(pose1, pose3)


def test_move_to():
    for _ in range(3):
        drawbot.bot_move_to(*middle)
        drawbot.go_position_draw()


def test_move_to_offlimit():
    drawbot.go_position_draw()
    drawbot.bot_move_to(*offlimit)


def test_tool_move():
    drawbot.go_position_draw()
    drawbot.tool_move('black')
    drawbot.tool_move('blue')
    drawbot.tool_move('red')
    drawbot.tool_move('green')
    drawbot.tool_move('undefined_colour')


#####################
# Ancillary functions
#####################
def test_move_y():
    drawbot.go_position_draw()
    drawbot.move_y()


def test_go_positions_ready_draw():
    drawbot.go_position_ready()
    drawbot.go_position_draw()
    drawbot.go_position_ready()


def test_home():
    drawbot.go_position_draw()
    drawbot.home()


def test_go_draw():
    drawbot.go_position_draw()
    drawbot.go_draw(drawbot.draw_position[0] + 50,
                    drawbot.draw_position[1] + 50)


def test_go_draw_up():
    drawbot.go_position_draw()
    drawbot.go_draw_up(drawbot.draw_position[0] + 50,
                       drawbot.draw_position[1] + 50)


def test_go_random_draw():
    drawbot.go_position_draw()
    drawbot.go_random_draw()


def test_go_random_3d():
    drawbot.go_position_draw()
    drawbot.go_random_3d()


def test_go_random_jump():
    drawbot.go_position_draw()
    drawbot.go_random_jump()
    drawbot.go_position_draw()
    drawbot.go_random_jump()


def test_position_move_by():
    drawbot.go_position_draw()
    drawbot.position_move_by(50, 50, 20)


####################
# Notation functions
####################
def test_squiggle():
    drawbot.go_position_draw()
    squiggle_list = [
        (uniform(-5, 5), uniform(-5, 5), uniform(-5, 5))
        for _ in range(randrange(3, 9))
    ]
    drawbot.squiggle(squiggle_list)


def test_dot():
    drawbot.go_position_draw()
    drawbot.dot()


def test_note_head():
    drawbot.go_position_draw()
    drawbot.note_head(5)
    drawbot.note_head(1)
    drawbot.note_head(10)


def test_arc2D():
    drawbot.go_position_draw()
    drawbot.arc2D(*pose1[:2], *pose2[:2])
    drawbot.go_position_draw()
    drawbot.arc2D(*pose1[:2], *pose3[:2])
    drawbot.go_position_draw()


def test_draw_square():
    drawbot.go_position_draw()
    drawbot.draw_square(5)
    drawbot.draw_square(25)
    drawbot.draw_square(10)


def test_draw_triangle():
    drawbot.go_position_draw()
    drawbot.draw_triangle(5)
    drawbot.draw_triangle(25)
    drawbot.draw_triangle(10)


def test_draw_sunburst():
    drawbot.go_position_draw()
    drawbot.draw_sunburst(5)
    drawbot.draw_sunburst(25)
    drawbot.draw_sunburst(10)


def test_draw_irregular_shape():
    drawbot.go_position_draw()
    drawbot.draw_irregular_shape(3)
    drawbot.draw_irregular_shape(0)
    drawbot.draw_irregular_shape(10)


def test_draw_circle():
    drawbot.go_position_draw()
    drawbot.draw_circle(5)
    drawbot.draw_circle(25)
    drawbot.draw_circle(10)


def test_draw_char():
    drawbot.go_position_draw()
    drawbot.draw_char('A', size=5)
    drawbot.draw_char('B', size=5)
    drawbot.draw_char('C', size=5)
    drawbot.draw_char('D', size=5)
    drawbot.draw_char('E', size=5)
    drawbot.draw_char('F', size=5)
    drawbot.draw_char('G', size=5)
    drawbot.draw_char('P', size=5)
    drawbot.draw_char('Z', size=5)


def test_create_shape_group():
    drawbot.go_random_jump()
    drawbot.create_shape_group()
