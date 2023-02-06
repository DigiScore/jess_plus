from random import getrandbits, randrange
from time import time, sleep
import logging
import struct

# install dobot modules
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs


######################
# DRAWBOT CONTROLS
######################

class Drawbot(Dobot):

    def __init__(self,
                 port,
                 verbose,
                 duration_of_piece,
                 continuous_line):

        super().__init__(port, verbose)

        self.continuous_line = continuous_line

        # make a shared list/ dict
        self.ready_position = [250, -175, 20, 0]
        self.draw_position = [250, -175, 0, 0]
        self.end_position = (250, 175, 20, 0)
        self.duration_of_piece = duration_of_piece
        self.start_time = time()

    def rnd(self, power_of_command: int) -> int:
        """Returns a randomly generated + or - integer,
        influenced by the incoming power factor"""
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result

    def move_y(self):
        """When called moves the pen across the y-axis
        aligned to the delta change in time across the duration of the piece"""
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # move z (pen head) a little
        if getrandbits(1):
            z = 0
        else:
            z = randrange(-2, 2)

        # which mode
        if self.continuous_line:
            self.move_to(x, newy, z, r, True)
        else:
            self.jump_to(x, newy, z, r, True)

        logging.info(f'Move Y to x:{round(x)} y:{round(newy)} z:{round(z)}')


    def move_y_random(self):
        """Moves x and y pen position to nearly the true Y point."""
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # which mode
        if self.continuous_line:
            self.move_to(x + self.rnd(10), newy + self.rnd(10), 0, r, True)
        else:
            self.jump_to(x + self.rnd(10), newy + self.rnd(10), 0, r, True)


    # def move_y(self):
    #         """When called moves the pen across the y-axis
    #         aligned to the delta change in time across the duration of the piece"""
    #         # How far into the piece
    #         elapsed = time() - self.local_start_time
    #
    #         # get current y-value
    #         (x, y, z, r, j1, j2, j3, j4) = self.pose()
    #         # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    #         newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
    #         logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
    #
    #         # check x-axis is in range
    #         if x <= 200 or x >= 300:
    #             x = 250
    #
    #         # move z (pen head) a little
    #         if self.pen:
    #             if getrandbits(1):
    #                 z = 0
    #             else:
    #                 z = randrange(-1, 1)
    #
    #         # which mode
    #         if self.continuous_line:
    #             self.move_to(x, newy, z, r, True)
    #         else:
    #             self.jump_to(x, newy, z, r, True)
    #
    #         logging.info(f'Move Y to x:{round(x)} y:{round(newy)} z:{round(z)}')

    # def move_y_random(self):
    #     """Moves x and y pen position to nearly the true Y point."""
    #     # How far into the piece
    #     elapsed = time() - self.local_start_time
    #
    #     # get current y-value
    #     (x, y, z, r, j1, j2, j3, j4) = self.pose()
    #     # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    #     newy = ((((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175) + self.rnd(100)
    #     logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
    #
    #     # check x-axis is in range
    #     newx = x + self.rnd(100)
    #     if newx <= 200 or newx >= 300:
    #         newx = 250
    #
    #     # # which mode
    #     # if self.continuous_line:
    #     #     self.move_to(newx, newy, 0, r, True)
    #     # else:
    #     self.jump_to(newx, newy, 0, r, True)


    ######################
    # DIGIBOT CONTROLS
    ######################
    """Low level functions for communicating direct to the Dobot"""
    def draw_stave(self, staves: int = 1):
        """Draws a  line across the middle of an A3 paper, symbolising a stave.
        Has optional function to draw multiple staves.
        Starts at right hand edge centre, and moves directly left.
        Args:
            staves: number of lines to draw. Default = 1"""

        stave_gap = 2
        x = 250 - ((staves * stave_gap) / 2)
        y_start = 175
        y_end = -175
        z = 0
        r = 0

        # goto start position for line draw, without pen
        self.move_to(x, y_start, z, r)
        input('insert pen, then press enter')

        if staves >= 1:
            # draw a line/ stave
            for stave in range(staves):
                print(f'drawing stave {stave + 1} out of {staves}')
                self.move_to(x, y_end, z, r)

                if staves > 1:
                    # reset to RH and draw the rest
                    x += stave_gap

                    if (stave + 1) < staves:
                        self.jump_to(x, y_start, z, r)
        else:
            self.jump_to(x, y_end, z, r)

    def squiggle(self, arc_list: list):
        """accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
             """
        [x, y, z, r] = self.pose()[0:4]
        for arc in arc_list:
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy
            sleep(0.2)

    def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
        """Draws an arc defined by a) circumference of arc (x, y, z, r),
        with b) a finishing coordinates (cirx, ciry, cirz, cirr.
        """
        msg = Message()
        msg.id = 101
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', r)))
        msg.params.extend(bytearray(struct.pack('f', cir_x)))
        msg.params.extend(bytearray(struct.pack('f', cir_y)))
        msg.params.extend(bytearray(struct.pack('f', cir_z)))
        msg.params.extend(bytearray(struct.pack('f', cir_r)))
        return self._send_command(msg, wait)

    def follow_path(self, path):
        for point in path:
            queue_index = self.move_to(point[0], point[1], point[2], 0)

    def continuous_trajectory(self, x, y, z, velocity = 50, wait = True):
        msg = Message()
        msg.id = 91
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', x)))
        msg.params.extend(bytearray(struct.pack('f', y)))
        msg.params.extend(bytearray(struct.pack('f', z)))
        msg.params.extend(bytearray(struct.pack('f', velocity)))

        return self._send_command(msg, wait)

    # todo - continuous trajectory - test circle
    def go_position_ready(self):
        """moves directly to pre-defined position 'Ready Position'"""
        x, y, z, r = self.ready_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def go_position_draw(self):
        """moves directly to pre-defined position 'Ready Position'"""
        x, y, z, r = self.draw_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def go_position_end(self):
        """moves directly to pre-defined position 'end position'"""
        x, y, z, r = self.end_position[:4]
        self.move_to(x, y, z, r, wait=True)

    def jump_to(self, x, y, z, r, wait=True):
        """Lifts pen up, and moves directly to defined coordinates (x, y, z, r)"""
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=wait)

    def move_to_relative(self, x, y, z, r, wait=True):
        """moves to new position defined in relatives coordinates to current position.
        Delta/ relative movement is x, y, z, r from current position"""
        self._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)

    def joint_move_to(self, j1, j2, j3, j4, wait=True):
        """moves specific joints direct to new angles."""
        self.joint_move_to(j1, j2, j3, j4, wait)

    def home(self):
        """Go directly to the home position 0, 0, 0, 0"""
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        return self._send_command(msg, wait=True)

    def clear_alarms(self) -> None:
        """clear the alarms log and LED"""
        msg = Message()
        msg.id = 20 # this should be 21, but that doesnt work!!
        msg.ctrl = 0x01
        self._send_command(msg)  # empty response

    def dot(self):
        """draws a small dot at current position"""
        self.note_head(1)

    def note_head(self, size: float = 5):
        """draws a circle at the current position.
        Default is 5 pixels diameter.
        Args:
            size: radius in pixels
            drawing: True = pen on paper
            wait: True = wait till sequence finished"""

        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        self.arc(x + size, y, z, r, x + 0.01, y + 0.01, z, r)



#
# def dobot_control(self):
#     """Loop thread that controls the robot arm
#     responses to the data generated by Nebula."""
#
#     print("Started dobot control thread")
#
#     while self.running:
#         while not self.dobot_commands_queue.empty():
#             print('================')
#             # check end of duration
#             if time() > self.end_time:
#                 self.terminate()
#                 self.running = False
#                 break
#
#             # get current nebula emission value
#             # live_emission_data = self.nebula.user_live_emission_data()
#             live_emission_data = self.dobot_commands_queue.get()
#
#             # if the value has changed then ...
#             if live_emission_data != self.old_value:
#                 self.old_value = live_emission_data
#
#                 # multiply by 10 for local logic (power value)
#                 incoming_command = int(live_emission_data * 10) + 1
#                 logging.info(f"MAIN: emission value = {live_emission_data} == {incoming_command}")
#
#                 # 1. clear the alarms
#                 self.digibot.clear_alarms()
#
#                 # 2. move Y
#                 # self.move_y()
#
#                 # 3. get speed based on power of incoming value * global speed setting * 2
#                 if getrandbits(1):
#                     self.digibot.speed(velocity=((incoming_command * 10) * self.global_speed) * 2,
#                                        acceleration=((incoming_command * 10) * self.global_speed) * 2
#                                        )
#                 else:
#                     self.digibot.speed(velocity=randrange(30, 200),
#                                        acceleration=randrange(30, 200)
#                                        )
#
#                 (x, y, z, r, j1, j2, j3, j4) = self.digibot.pose()
#                 logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')
#
#                 #
#                 # LOW power response from AI Factory
#                 #
#                 if incoming_command < 3:
#                     # self.move_y()
#                     # self.digibot.dot()
#
#                     logging.info('Emission < 3: PASS')
#
#                 #
#                 # HIGH power response from AI Factory
#                 #
#                 elif incoming_command >= 8:
#                     # self.move_y_random()
#
#                     # does this or that
#                     if getrandbits(1):
#                         self.move_y_random()
#                         logging.info('Emission >= 8: move Y random')
#                     else:
#                         # self.move_y()
#                         self.digibot.arc(x + self.rnd(incoming_command),
#                                          y + self.rnd(incoming_command),
#                                          z, 0,
#                                          x + self.rnd(incoming_command),
#                                          y + self.rnd(incoming_command),
#                                          z, 0,
#                                          False)
#                         logging.info('Emission >= 8: arc')
#
#                 #
#                 # MID power response
#                 #
#                 else:
#                     # randomly choose from the following c hoices
#                     randchoice = randrange(6)
#                     logging.debug(f'randchoice == {randchoice}')
#
#                     # 0= line to somewhere
#                     if randchoice == 0:
#                         self.digibot.move_to(x + self.rnd(incoming_command),
#                                              y + self.rnd(incoming_command),
#                                              z, 0,
#                                              False)
#                         logging.info('Emission 3-8: draw line')
#
#                     # 1 = messy squiggles
#                     if randchoice == 1:
#                         squiggle_list = []
#                         for n in range(randrange(2, 4)):
#                             squiggle_list.append((randrange(-5, 5) / 10,
#                                                   randrange(-5, 5) / 10,
#                                                   randrange(-5, 5) / 10)
#                                                  )
#                         self.digibot.squiggle(squiggle_list)
#                         logging.info('Emission 3-8: small squiggle')
#
#                     # 2 = dot
#                     elif randchoice == 2:
#                         self.digibot.dot()
#                         logging.info('Emission 3-8: dot')
#
#                     # 3 = note head
#                     elif randchoice == 3:
#                         note_size = randrange(5)
#                         note_shape = randrange(20)
#                         self.digibot.note_head(size=note_size,
#                                                steps=note_shape)
#                         logging.info('Emission 3-8: note head')
#
#                     # 4 = note head and line
#                     elif randchoice == 4:
#                         note_size = randrange(5)
#                         note_shape = randrange(20)
#                         self.digibot.note_head(size=note_size,
#                                                steps=note_shape)
#                         self.digibot.move_to(x + self.rnd(incoming_command),
#                                              y + self.rnd(incoming_command),
#                                              z, 0,
#                                              False)
#                         logging.info('Emission 3-8: note head and line')
#
#                     # 5 = dot and random Y
#                     elif randchoice == 5:
#                         self.digibot.dot()
#                         self.move_y_random()
#                         logging.info('Emission 3-8: dot and line')
#
#                 # take a breath
#                 sleep(self.global_speed)
#
#             # wait a bit until the new emission is different from current
#             self.move_y()
#             sleep(self.global_speed)
#
#     logging.info('quitting dobot director thread')
