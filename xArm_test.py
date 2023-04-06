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
middle_down = [sum(config.xarm_x_extents)/2,
               sum(config.xarm_y_extents)/2,
               drawbot.z]


# Test move to
def test_move_to():
    middle = [sum(config.xarm_x_extents)/2,
              sum(config.xarm_y_extents)/2,
              sum(config.xarm_z_extents)/2]
    middle_too_high = [sum(config.xarm_x_extents)/2,
                       sum(config.xarm_y_extents)/2,
                       config.xarm_z_extents[1] + 50]
    for _ in range(N_REPEAT):
        drawbot.move_to(*middle)
        drawbot.move_to(*middle_too_high)
        drawbot.move_to(*middle_down)


# Test arc
def test_arc():
    pose1 = [300, 0, drawbot.z, drawbot.roll, drawbot.pitch, drawbot.yaw]
    pose2 = [400, 200, drawbot.z, drawbot.roll, drawbot.pitch, drawbot.yaw]
    pose_off_limit = [400, config.xarm_y_extents[1] + 50, drawbot.z,
                      drawbot.roll, drawbot.pitch, drawbot.yaw]
    drawbot.move_to(*middle_down)
    drawbot.arc(pose1, pose2)
    drawbot.move_to(*middle_down)
    drawbot.arc(pose1, pose_off_limit)


# Test squiggle
def test_squiggle():
    squiggle_list = []
    for _ in range(randrange(3, 9)):
        squiggle_list.append((uniform(-5, 5), uniform(-5, 5), uniform(-5, 5)))
    for _ in range(N_REPEAT):
        drawbot.squiggle(squiggle_list)


if __name__ == "__main__":
    # test_move_to()
    test_arc()
    # test_squiggle()
