from digibot import Digibot
from nebula.nebula import Nebula
from queue import Queue
import logging

logging.basicConfig(level=logging.DEBUG)

q = Queue()
nebula = Nebula(q, speed=1)

nebula.director()













# import sys
# import os
# import math
# from random import randrange, random, getrandbits
# from time import time, sleep
#
# from serial.tools import list_ports
# from digibot import Digibot
#
# digibot = Digibot(verbose=False)
# digibot.draw_stave()
#
# mode = 1
# if mode == 1:
#     mode_type = "draw"
# else:
#     mode_type = "co-create"
#
# print(f'mode = {mode_type}')
# """
# draw mode uses continuous line like Cardew
# co-create mode, is like Wolff's piece
# """
#
# (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
# print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
# # reset speed
# digibot.speed(velocity=100, acceleration=100)
#
# # print('test wiggle')
# # digibot.move_to(x + 20, y, z, r, wait=True)
# # # device.wait(1000)
# # digibot.move_to(x, y, z, r, wait=True)
#
# # start operating vars
# duration_of_piece = 400  # seconds
# running = True
# old_value = 0
# start_time = time()
# end_time = start_time + duration_of_piece
#
#
# def move_y():
#     # move y along a bit
#     elapsed = time() - start_time
#
#     # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
#     newy = (((elapsed - 0) * (175 - -175)) / (duration_of_piece - 0)) + -175
#
#     # current_y_delta = elapsed * sub_division_of_duration
#     (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
#     print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
#     # lift up pen
#     # digibot.move_to_relative(0, 0, 5, 0)
#     print('elapsed time = ', elapsed)
#     print(f'old y = {y}, move to = {newy}')
#     if x <= 200 or x >= 300:
#         x = 250
#     if mode == 1:
#         digibot.jump_to(x, newy, 0, r, True)
#
#     # digibot.move_to_relative(0, 0, -5, 0)
#     # return (x, y, z)
#
# def rnd(power):
#     pos = 1
#     if getrandbits(1):
#
#         pos = -1
#     result = (randrange(1, 5) + power) * pos
#     print(f'Rnd result = {result}')
#     return result
#
# # todo - move to an emmission system like Fabrizio's score
# while time() < end_time:
#     # 1. clear the alarms
#     digibot.clear_alarms()
#
#     # 2. calculate y-position & outside x range?
#
#
#     power = randrange(1, 10)
#     # print('move y')
#     # move_y()
#
#     (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
#     print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
#     digibot.speed(velocity=randrange(3, 10) * 10, acceleration=randrange(3, 10) * 10)
#
#     # sleep(2)
#
#     # digibot.squiggle([(rnd(power), rnd(power), rnd(power))])
#
#     randchoice = randrange(4)
#     print(f'randchoice == {randchoice}')
#
#     # move y
#     if randchoice == 0:
#         print('move y')
#         move_y()
#
#     # messy squiggle
#     if randchoice <= 1:
#         squiggle_list = []
#         for n in range(randrange(2, 4)):
#             squiggle_list.append((randrange(-5, 5),
#                                   randrange(-5, 5),
#                                   randrange(-5, 5))
#                                    )
#         digibot.squiggle(squiggle_list)
#
#         # digibot.squiggle([(randrange(1, 5), randrange(1, 5), randrange(1, 5))])
#
#     # line to somewhere
#     elif randchoice == 2:
#         digibot.move_to(x + rnd(power), y + rnd(power), 0, 0, True)
#
#     # arc/ circle
#     elif randchoice == 3:
#         digibot.arc(x + rnd(power), y + rnd(power), 0, 0, x + rnd(power), y + rnd(power), 0, 0, True)
#
#     # elif randchoice == 4:
#     #     move_y()
#
#     sleep(random() * power)
#
# digibot.close()
#
