from random import getrandbits, randrange, uniform
from time import time, sleep
from enum import Enum
import logging
import struct
import math
import numpy as np
from threading import Thread

# install dobot modules
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs

# install project modules
import config
from nebula.hivemind import DataBorg


class Shapes(Enum):
    Square = 0
    Triangle = 1
    Sunburst = 2
    Irregular = 3
    Circle = 4
    Line = 5

######################
# DRAWBOT CONTROLS
######################

class Drawbot(Dobot):
    """
    Translation class for digibot arm control
    and primitive commands of robot arm.
    If using a different robot arm, this class will need to
    be updated. All others classes should remain the same
    """

    def __init__(self,
                 port,
                 verbose,
                 continuous_line
                 ):

        # own a hive mind
        self.hivemind = DataBorg()

        # init and inherit the Dobot library
        super().__init__(port, verbose)

        self.continuous_line = continuous_line

        # make a shared list/ dict
        self.ready_position = [250, 0, 20, 0]
        self.draw_position = [250, 0, 0, 0]
        self.end_position = (250, 0, 50, 0)

        self.x_extents = config.x_extents
        self.y_extents = config.y_extents
        self.z_extents = config.z_extents
        self.irregular_shape_extents = config.irregular_shape_extents

        self.squares = []
        self.sunbursts = []
        self.irregulars = []
        self.circles = []
        self.triangles = []
        self.chars = []

        self.shape_groups = []  # list of shape groups [shape type, size, pos]
        self.coords = []        # list of coordinates drawn

        # create a command loist and start process thread
        self.command_list = []
        list_thread = Thread(target=self.process_command_list)
        list_thread.start()

        self.last_shape_group = None

        self.duration_of_piece = config.duration_of_piece
        self.start_time = time()

    ######################
    # Command Q control & safety checks
    ######################
    def add_to_list_set_ptp_cmd(self, x, y, z, r, mode, wait):
        msg_item = (x, y, z, r, mode, wait)
        self.command_list.append(msg_item)
        # print(len(self.command_list))

    def process_command_list(self):
        while self.hivemind.running:
            if not self.hivemind.interrupt_bang:
                self.command_list.clear()
                sleep(0.1)
            elif self.command_list:
                msg = self.command_list.pop()
                x, y, z, r, mode, wait = msg[:]
                self._set_ptp_cmd(x, y, z, r, mode, wait)
            else:
                sleep(0.01)

    def get_normalised_position(self):
        original_pose = self.get_pose()[:3]

        # do a safety position check
        pose = self.safety_position_check(original_pose)

        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        # new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

        norm_x = ((pose[0] - config.x_extents[0]) / (config.x_extents[1] - config.x_extents[0])) * (1 - 0) + 0
        norm_y = ((pose[1] - config.y_extents[0]) / (config.y_extents[1] - config.y_extents[0])) * (1 - 0) + 0
        norm_z = ((pose[2] - config.z_extents[0]) / (config.z_extents[1] - config.z_extents[0])) * (1 - 0) + 0

        norm_xyz = (norm_x, norm_y, norm_z)
        norm_xyz = tuple(np.clip(norm_xyz, 0.0, 1.0))
        norm_xy_2d = np.array(norm_xyz[:2])[:, np.newaxis]

        self.hivemind.current_robot_x_y_z = norm_xyz
        self.hivemind.current_robot_x_y = np.append(self.hivemind.current_robot_x_y, norm_xy_2d, axis=1)
        self.hivemind.current_robot_x_y = np.delete(self.hivemind.current_robot_x_y, 0, axis=1)

        logging.info(f'current x,y,z normalised  = {norm_xyz}')

    def safety_position_check(self, pose):
        if pose[0] < self.x_extents[0]:     # check x posiion
            x = self.x_extents[0]
        elif pose[0] > self.x_extents[1]:
            x = self.x_extents[1]
        else:
            x = pose[0]

        if pose[1] < self.y_extents[0]:  # check y posiion
            y = self.y_extents[0]
        elif pose[1] > self.y_extents[1]:
            y = self.y_extents[1]
        else:
            y = pose[1]

        if pose[2] < self.z_extents[0]:  # check x posiion
            z = self.z_extents[0]
        elif pose[2] > self.z_extents[1]:
            z = self.z_extents[1]
        else:
            z = pose[2]

        self.move_to(x, y, z, 0, False)

        return_pose = (x, y, z)
        return return_pose

    def rnd(self, power_of_command: int) -> int:
        """
        Returns a randomly generated + or - integer,
        influenced by the incoming power factor
        """
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result

    def clear_alarms(self) -> None:
        """
        clear the alarms log and LED
        """
        msg = Message()
        msg.id = 20 # this should be 21, but that doesnt work!!
        msg.ctrl = 0x01
        self._send_command(msg)  # empty response

    def clear_commands(self):
        # self.force_queued_stop()
        # self._set_queued_cmd_stop_exec()
        self._set_queued_cmd_clear()
        # self._set_queued_cmd_start_exec()

    def force_queued_stop(self):
        """
        Uses the 242 code to force stop a command
        :return: stop command via message send
        """
        msg = Message()
        msg.id = 242
        msg.ctrl = ControlValues.ONE
        return self._send_command(msg)

    def get_pose(self):
        return self.pose()

    # def _send_message(self, msg):
    #     sleep(0.1)
    #     if self.verbose:
    #         print('pydobot: >>', msg)
    #     if self.hivemind.interrupt_bang:
    #         self.ser.write(msg.bytes())
    #     else:
    #         self.clear_commands()

    def _send_command(self, msg, wait=False):
        self.lock.acquire()
        self._send_message(msg)
        response = self._read_message()
        self.lock.release()
        #
        # if not wait:
        #     return response
        #
        # # if self.hivemind.interrupt_bang:
        # try:
        #     expected_idx = struct.unpack_from('L', response.params, 0)[0]
        #     if self.verbose:
        #         print('pydobot: waiting for command', expected_idx)
        #
        #     while True:
        #         current_idx = self._get_queued_cmd_current_index()
        #
        #         if current_idx != expected_idx:
        #             sleep(0.1)
        #             continue
        #
        #         if self.verbose:
        #             print('pydobot: command %d executed' % current_idx)
        #         break
        # except:
        #     print('pydobot -- command error')

        return response

    ######################
    # DIGIBOT CORE FUNCTIONS
    ######################
    """
    Low level functions for communicating direct to Dobot primitives.
    All of the notation functions ()below) need to call these here.
    """

    def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
        """
        Draws an arc defined by a) circumference of arc (x, y, z, r),
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

    def arc2D(self, apex_x, apex_y, target_x, target_y, wait=True):
        """
        Simplified arc function for drawing 2D arcs on the xy axis.
        apex_x and y determine
        the coordinates of the apex of the curve.
        target_x and y determine the end point of the curve
        """
        pos = self.get_pose()
        self.coords.append(pos[:2])
        msg = Message()
        msg.id = 101
        msg.ctrl = 0x03
        msg.params = bytearray([])
        msg.params.extend(bytearray(struct.pack('f', apex_x)))
        msg.params.extend(bytearray(struct.pack('f', apex_y)))
        msg.params.extend(bytearray(struct.pack('f', pos[2])))
        msg.params.extend(bytearray(struct.pack('f', pos[3])))
        msg.params.extend(bytearray(struct.pack('f', target_x)))
        msg.params.extend(bytearray(struct.pack('f', target_y)))
        msg.params.extend(bytearray(struct.pack('f', pos[2])))
        msg.params.extend(bytearray(struct.pack('f', pos[3])))
        return self._send_command(msg, wait)

    def move_y(self):
        """
        When called moves the pen across the y-axis
        aligned to the delta change in time across the duration of the piece
        """
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # move z (pen head) a little
        # if getrandbits(1):
        #     z = 0
        # else:
        #     z = randrange(-2, 2)

        # which mode
        # if self.continuous_line:
        self.bot_move_to(x, newy, z, r, True)
        # else:
        #     self.jump_to(x, newy, z, r, True)

        logging.info(f'Move Y to x:{round(x)} y:{round(newy)} z:{round(z)}')

    def move_y_random(self):
        """
        Moves x and y pen position to nearly the true Y point.
        """
        # How far into the piece
        elapsed = time() - self.start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # which mode
        if self.continuous_line:
            self.bot_move_to(x + self.rnd(10), newy + self.rnd(10), 0, r, True)
        else:
            self.jump_to(x + self.rnd(10), newy + self.rnd(10), 0, r, True)

    def go_position_ready(self):
        """
        moves directly to pre-defined position 'Ready Position'
        """
        x, y, z, r = self.ready_position[:4]
        self.bot_move_to(x, y, z, r, wait=True)

    def go_position_draw(self):
        """
        moves directly to pre-defined position 'Ready Position'
        """
        x, y, z, r = self.draw_position[:4]
        self.bot_move_to(x, y, z, r, wait=True)

    def go_position_end(self):
        """
        moves directly to pre-defined position 'end position'
        """
        x, y, z, r = self.end_position[:4]
        self.bot_move_to(x, y, z, r, wait=True)

    def jump_to(self, x, y, z, r, wait=True):
        """
        Lifts pen up, and moves directly to defined coordinates (x, y, z, r)
        """
        self.add_to_list_set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=wait)

    def joint_move_to(self, j1, j2, j3, j4, wait=True):
        """
        moves specific joints direct to new angles.
        """
        self.joint_move_to(j1, j2, j3, j4, wait)

    def home(self):
        """
        Go directly to the home position 0, 0, 0, 0
        """
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        return self._send_command(msg, wait=True)

    def bot_move_to(self, x, y, z, r, wait=False):
        self.move_to(x, y, z, r, wait)

    def go_draw(self, x, y, wait=True):
        """
        Go to an x and y position with the pen touching the paper
        """
        self.coords.append((x, y))
        if self.hivemind.interrupt_bang:
            self.add_to_list_set_ptp_cmd(x, y, self.draw_position[2], 0, mode=PTPMode.MOVJ_XYZ, wait=wait)

    def go_draw_up(self, x, y, wait=True):
        """
        Lift the pen up, go to an x and y position, then lower the pen
        """
        self.coords.append((x, y))
        # TODO - Adam - this needs organising better. We have multiple funcs that are calling Dobot API primitives when we should be controlling all of those with a single command here e.g. def.send_ptp_jump and def send_ptp_movej
        self.add_to_list_set_ptp_cmd(x, y, self.draw_position[2], 0, mode=PTPMode.JUMP_XYZ, wait=wait)

    #-- creative go to position functions --#
    def go_random_draw(self):  # goes to random position on the page with pen touching page
        """
        Move to a random position within the x and y
        extents with the pen touching the page.
        """
        x = uniform(self.x_extents[0],self.x_extents[1])
        y = uniform(self.y_extents[0], self.y_extents[1])
        z = self.draw_position[2]
        r = 0

        self.coords.append((x, y))
        print("Random draw pos x:", round(x, 2)," y:", round(y,2))
        self.add_to_list_set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=True)

    def go_random_draw_up(self):   #goes to random positon on page with pen above page then back on
        """
        Lift the pen, move to a random position within the x and y extents,
        then lower the pen to draw position
        """
        x = uniform(self.x_extents[0],self.x_extents[1])
        y = uniform(self.y_extents[0], self.y_extents[1])
        z = self.draw_position[2]
        r = 0

        self.coords.append((x, y))
        print("Random draw pos above page x:",x," y:",y)
        self.add_to_list_set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=False)

    #-- move by functions --#
    def position_move_by(self, x, y, z, wait=True):
        """
        Increment the robot cartesian position by x, y, z.
        Check that the arm isn't going out of x, y, z extents
        """

        pose = self.get_pose()[:3]

        newPose = [pose[0] + x, pose[1] + y, pose[2] + z]       #calulate new position, used for checking

        # todo (ADAM) - use this to make a new func (def.check_pos) that all funcs can call
        if newPose[0] < self.x_extents[0] or newPose[0] > self.x_extents[1]:     # check x posiion
            print("delta x reset to 0")
            x = 0
        if newPose[1] < self.y_extents[0] or newPose[1] > self.y_extents[1]:     # check y position
            print("delta y reset to 0")
            y = 0
        if newPose[2] < self.z_extents[0] or newPose[2] > self.z_extents[1]:      # check z height
            print("delta z reset to 0")
            z = 0

        self.coords.append(newPose[:2])
        self.add_to_list_set_ptp_cmd(x, y, z, 0, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)

    # def joint_move_by(self, _j1, _j2, _j3, wait=True):
    #     """moves specific joints by an amount."""
    #     (j1, j2, j3, j4) = self.get_pose()[-4:]
    #     print(j1, j2, j3, j4)
    #     #if(z <= z_extents[0] + 2):  # if the arm is too low, rotate j2 slightly clockwise to raise the arm
    #     #    print("joint_move_by z too low, _j2 = -2")
    #     #    _j2 = -2
    #
    #     # newPose = [
    #     _j1 += j1
    #     _j2 += j2
    #     _j3 -= j3
    #     # ]
    #     self.add_to_list_set_ptp_cmd(_j1, _j2, _j3, j4, mode=PTPMode.MOVJ_INC, wait=wait)

    ######################
    # DIGIBOT NOTATION FUNCTIONS
    ######################
    """
      Mid level functions for drawing the shapes of the notation.
      All of these notation functions need to call the Low level functions above.
      DO NOT CALL DOBOT PRIMATIVES DIRECTY!!
      """
    def draw_stave(self, staves: int = 1):
        """
        Draws a  line across the middle of an A3 paper, symbolising a stave.
        Has optional function to draw multiple staves.
        Starts at right hand edge centre, and moves directly left.
        Args:
            staves: number of lines to draw. Default = 1
        """

        stave_gap = 2
        x = 250 - ((staves * stave_gap) / 2)
        y_start = 175
        y_end = -175
        z = 0
        r = 0

        # goto start position for line draw, without pen
        self.bot_move_to(x, y_start, z, r)
        input('place pen on paper, then press enter')

        if staves >= 1:
            # draw a line/ stave
            for stave in range(staves):
                print(f'drawing stave {stave + 1} out of {staves}')
                self.bot_move_to(x, y_end, z, r)

                if staves > 1:
                    # reset to RH and draw the rest
                    x += stave_gap

                    if (stave + 1) < staves:
                        self.jump_to(x, y_start, z, r)
        else:
            self.jump_to(x, y_end, z, r)

    def squiggle(self, arc_list: list):
        """
        accepts a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs that define a squiggle.
        list (circumference point, end point x, end point y):
            circumference point: size of arc in pixels across x axis
            end point x, end point y: distance from last/ previous position
        """
        [x, y, z, r] = self.get_pose()[0:4]
        self.coords.append((x, y))
        for arc in arc_list:
            # if self.hivemind.interrupt_bang:
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy
            sleep(0.2)

    def dot(self):
        """
        draws a small dot at current position
        """
        self.note_head(1)

    def note_head(self, size: float = 5):
        """
        draws a circle at the current position.
        Default is 5 pixels diameter.
        Args:
            size: radius in pixels
            drawing: True = pen on paper
            wait: True = wait till sequence finished
            """

        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        self.arc(x + size, y, z, r, x + 0.01, y + 0.01, z, r)

    #-- shape drawing functions --#
    def draw_square(self, size):      # draws a square at the robots current position with a size and angle (in degrees)
        """
        Draw a square from the pen's current position.
        Start from top left vertex and draw anti-clockwise.
        Positions are saved to the squares array to be accessed by other functions.
        """
        pos = self.get_pose()[:2]
        square = []

        local_pos = [
            (size, 0),
            (size, size),
            (0, size)
        ]

        for i in range(len(local_pos)):
            # if self.hivemind.interrupt_bang:
            next_pos = [
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1]
            ]
            self.go_draw(next_pos[0], next_pos[1])
            square.append(next_pos)
            self.coords.append(next_pos)

        # if self.hivemind.interrupt_bang:
        self.go_draw(pos[0], pos[1], wait=False)

        self.squares.append(square)

    def draw_triangle(self, size):
        """
        Draws a triangle from the current pen position.
        Randomly chooses a type of triangle to draw
        and uses the size parameter to determine the size.
        For irregular triangles, use draw_irregular(3).
        """
        pos = self.get_pose()[:2]     # x, y
        triangle = []

        rand_type = randrange(0,2)
        if rand_type == 0:
            #right angle triangle
            local_pos = [
                (0, 0),
                (-size, 0),
                (-size, size)
            ]

        elif rand_type == 1:
            #isosceles triangle
            local_pos = [
                (0, 0),
                (-size * 2, - size / 2),
                (- size * 2, size / 2)
            ]

        for i in range(len(local_pos)):
            # if self.hivemind.interrupt_bang:
            next_pos = [                    # next vertex to go to in world space
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1]
            ]
            # if shape_interrupt == False:
            self.go_draw(next_pos[0], next_pos[1], wait=True)
            # else:
            #     shape_interrupt = False
            #     return None

            triangle.append(next_pos)
            self.coords.append(next_pos)

        # if self.hivemind.interrupt_bang:
        self.go_draw(pos[0], pos[1])     # go back to the first vertex to join up the shape
        self.triangles.append(triangle)

    def draw_sunburst(self, r, randomAngle = True):    # draws a sunburst from the robots current position, r = size of lines, num = number of lines
        """
        Draw a sunburst from the pens position. Will draw r number of
        lines coming from the centre point.
        Can be drawn with lines at random angles between 0 and
        360 degrees or with pre-defined angles. Positions are saved
        to the sunbursts array to be accessed by other functions.
        """
        pos = self.get_pose()

        if randomAngle == True:
            random_angles = [
                uniform(0, 360),
                uniform(0, 360),
                uniform(0, 360),
                uniform(0, 360),
                uniform(0, 360)
            ]
            local_pos = [
                (r * math.sin(random_angles[0]), r * math.cos(random_angles[0])),
                (r * math.sin(random_angles[1]), r * math.cos(random_angles[1])),
                (r * math.sin(random_angles[2]), r * math.cos(random_angles[2])),
                (r * math.sin(random_angles[3]), r * math.cos(random_angles[3])),
                (r * math.sin(random_angles[4]), r * math.cos(random_angles[4]))
            ]
        else:
            local_pos = [
                (r * math.sin(320), r * math.cos(320)),
                (r * math.sin(340), r * math.cos(340)),
                (r * math.sin(0), r * math.cos(0)),
                (r * math.sin(20), r * math.cos(20)),
                (r * math.sin(40), r * math.cos(40))
            ]

        sunburst = []  #saves all points in this sunburst then saves it to the list of drawn sunbursts
        for i in range(len(local_pos)):
            # if self.hivemind.interrupt_bang:
            next_pos = [
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1],
            ]
            sunburst.append(next_pos)
            self.coords.append(next_pos)

            self.go_draw(next_pos[0], next_pos[1], wait=False)       #draw line from centre point outwards
            self.go_draw(pos[0], pos[1], wait=False)              #return to centre point to then draw another line

        self.sunbursts.append(sunburst)

    def draw_irregular_shape(self, num_vertices):
        """
        Draws an irregular shape from the current pen position with 'num_vertices'
        number of randomly generated vertices. If set to 0,
         'num_vertices' will be randomised between 3 and 10.
        Positions are saved to the irregulars array to be accessed by other functions.
        """
        pos = self.get_pose()

        if num_vertices <= 0:
            num_vertices = randrange(3, 10)

        vertices = []
        for i in range(num_vertices):
            x = uniform(-self.irregular_shape_extents, self.irregular_shape_extents)
            y = uniform(-self.irregular_shape_extents, self.irregular_shape_extents)
            vertices.append((x,y))
            self.coords.append((x,y))

        for i in range(len(vertices)):
            # if self.hivemind.interrupt_bang:
            x, y = vertices[i]
            x = pos[0] + x
            y = pos[1] + y
            # todo Adam - this needs to call a dobot mid level func (above)
            self.add_to_list_set_ptp_cmd(x, y, self.draw_position[2], 0, mode=PTPMode.MOVJ_XYZ, wait=True)

        # if self.hivemind.interrupt_bang:
        # todo Adam - this needs to call a dobot mid level func (above)
        self.add_to_list_set_ptp_cmd(pos[0], pos[1], pos[2], 0, mode=PTPMode.MOVJ_XYZ, wait=True)

        self.irregulars.append(vertices)

    def draw_circle(self, size, side=0, wait=True):
        """
        Draws a circle from the current pen position.
        'side' is used to determine which direction the circle is drawn relative
        to the pen position, allows for creation of figure-8 patterns.
        The start position, size, and side are saved to the circles list.
        """
        pos = self.get_pose()[:4]

        if side == 0:  # side is used to draw figure 8 patterns
            self.arc(pos[0] + size, pos[1] - size, pos[2], pos[3], pos[0]+ 0.01, pos[1] + 0.01, pos[2], pos[3], wait=wait)
        elif side == 1:
            self.arc(pos[0] - size, pos[1] + size, pos[2], pos[3], pos[0]+ 0.01, pos[1] + 0.01, pos[2], pos[3], wait=wait)

        circle = []
        circle.append(pos)
        circle.append(size)
        circle.append(side)
        self.coords.append(pos)

        self.circles.append(circle)

    def draw_char(self, _char, size, wait=True):
        """
        Draws a character (letter, number) on the pens current position.
        Supported characters are as follows:
        A, B, C, D, E, F, G, P. All letters consisting of just straight
        lines are drawn in this function whereas
        letters with curves are drarn in their own respective functions.
        """
        #print("Drawing letter: ", _char)
        pos = self.get_pose()[:2]     # x, y
        char = []
        char.append(_char.upper())

        jump_num = -1   # determines the characters that need a jump, cant be drawn continuously. If left as -1 then no jump is needed

        #----Calculate local_pos for each char----#
        if _char == "A" or _char == "a":

            local_pos = [
                (0, 0),                     # bottom left
                (size * 2, - size / 2),     # top
                (0, - size),                # bottom right
                (size, - size * 0.75),      # mid right
                (size, - size * 0.25)       # mid left
            ]
        elif _char == "B" or _char == "b":
            print("B")
            self.draw_b(size=size, wait=wait)
            return None

        elif _char == "C" or _char == "c":  # for characters with curves, defer to specific functions
            self.draw_c(size=size, wait=wait)
            return None                     # everything else is handled in draw_c, can exit function here

        elif _char == "D" or _char == "d":
            self.draw_d(size=size, wait=wait)
            return None

        elif _char == "E" or _char == "e":
            local_pos = [
                (0, 0),             # bottom right
                (0, size),          # bottom left
                (size * 2, size),   # top left
                (size * 2, 0),      # top right
                (size, 0),          # mid right (jump to here)
                (size, size)        # mid left
            ]

            jump_num = 4

        elif _char == "F" or _char == "f":
            local_pos = [
                (0, 0),                 # bottom left
                (size * 2, 0),          # top left
                (size * 2, - size / 2), # top right
                (size, - size / 2),     # mid right (jump to here)
                (size, 0)               # mid left
            ]

            jump_num = 3

        elif _char == "G" or _char == "g":
            self.draw_g(size=size, wait=wait)
            return None

        elif _char == "P" or _char == "p":  
            self.draw_p(size=size, wait=wait)
            return None                     

        elif _char == "Z" or _char == "z":
            local_pos = [
                (0, 0),
                (0, size),
                (size * 2, 0),
                (size * 2, size)
            ]

        else:
            print("Input: ", _char, " is not supported by draw_char")
            return None

        #----Draw character----#
        for i in range(len(local_pos)):
            next_pos = [
                pos[0] + local_pos[i][0], pos[1] + local_pos[i][1]  # calculate the next world position to draw
            ]

            if jump_num != -1:                      # for characters that need a jump
                if i == jump_num: self.go_draw_up(next_pos[0], next_pos[1])
                else:
                    self.go_draw(next_pos[0], next_pos[1], wait=True)

            else:                                   # the rest of the letters can be drawn in a continuous line
                self.go_draw(next_pos[0], next_pos[1], wait=True)

            char.append(next_pos)     # append the current position to the letter
            self.coords.append(next_pos)

        self.chars.append(char)          # add the completed character to the characters list

    def draw_p(self, size, wait=True):
        """
        Draws the letter P at the pens current position.
        Seperate from the draw_char() function as it requires an arc.
        Is called in draw_char() when P is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("P")

        local_pos = [
            (0, 0),                 # bottom of letter
            (size * 2, 0),          # top of letter
            (size * 0.75, -size * 0.85),   # peak of curve
            (size * 1.2, 0)               # middle of letter
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
            (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1])
        ]
        # if self.hivemind.interrupt_bang:
        self.go_draw(world_pos[1][0], world_pos[1][1])

        # if self.hivemind.interrupt_bang:
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)

        char.append(world_pos)
        self.chars.append(char)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_b(self, size, wait=True):
        """
        Draws the letter B at the pens current position.
        Seperate from the draw_char() function as it requires an arc.
        Is called in draw_char() when B is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("B")

        local_pos = [
            (0, 0),                 # 0 bottom left
            (size * 2, 0),          # 1 top right
            (size * 1.5, -size),    # 2 peak of top curve
            (size, 0),              # 3 mid left
            (size * 0.5, -size)     # 4 peak of bottom curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
            (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1]),
            (pos[0] + local_pos[4][0], pos[1] + local_pos[4][1])
        ]
        # if self.hivemind.interrupt_bang:
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)
        self.arc2D(world_pos[4][0], world_pos[4][1], world_pos[0][0], world_pos[0][1], wait=wait)

        char.append(world_pos)
        self.chars.append(char)
        for i in range(len(world_pos)): self.coords.append(world_pos[i])

    def draw_c(self, size, wait=True):
        """
        Draws the letter C at the pens current position.
        Seperate from the draw_char() function as it requires an arc.
        Is called in draw_char() when C is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("C")

        local_pos = [
            (size * 0.3 , 0),      # 0 bottom of curve
            (size       , size),      # 1 middle of curve
            (size * 1.7 , 0)       # 2 top of curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
        ]
        # if self.hivemind.interrupt_bang:
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)

        char.append(world_pos)
        self.chars.append(char)
        for i in range(len(world_pos)): self.coords.append(world_pos[i])

    def draw_d(self, size, wait=True):
        """
        Draws the letter D at the pens current position.
        Seperate from the draw_char() function as it requires an arc.
        Is called in draw_char() when D is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("D")

        local_pos = [
            (0, 0),                 # 0 bottom left
            (size * 2, 0),          # 1 top left
            (size, -size)           # 2 peak of curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
        ]

        # if self.hivemind.interrupt_bang:
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[0][0], world_pos[0][1], wait=wait)

        char.append(world_pos)
        self.chars.append(char)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_g(self, size, wait=True):
        """
        Draws the letter G at the pens current position.
        Seperate from the draw_char() function as it requires an arc.
        Is called in draw_char() when G is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("G")

        local_pos = [
            (0, 0),                  # 0 top right
            (- size, size),     # 1 peak of curve
            (- size * 2, 0),        # 2 bottom right
            (-size, 0),        # 3 mid right
            (-size, size / 2)  # 4 center point

        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
            (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1]),
            (pos[0] + local_pos[4][0], pos[1] + local_pos[4][1])
        ]

        # if self.hivemind.interrupt_bang:
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)
        self.go_draw(world_pos[3][0], world_pos[3][1], wait=wait)
        self.go_draw(world_pos[4][0], world_pos[4][1], wait=wait)

        char.append(world_pos)
        self.chars.append(char)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_random_char(self, size=1, wait=True):
        chars = ["A", "B", "C", "D", "E", "F", "G", "P", "Z"]

        rand_char = chars[randrange(0, len(chars))]

        self.draw_char(rand_char, size, wait)

    def create_shape_group(self, wait=True):
        """
        Function to create a new shape group, populates a list with shape
        group data and draws it using draw_shape_group().
        Is called once whenever affect module enters Repetition mode
        """

        print("creating a shape")
        pos = self.get_pose()[:3]       # position of the group
        shapes_num = randrange(2, 4)     # number of shapes in this group
        shape_group = []                # stores the current shape group
        
        for i in range(shapes_num):
            type = Shapes(randrange(6))                    # generate random shape type

            if type == Shapes.Line:                                     # if it's a line, add the type and x and y target position
                local_target_pos = uniform(-20, 20), uniform(-20, 20)   # random change in position (is added to pos to get world_pos)
                shape_group.append((type, local_target_pos))          # add the shape type and its local_pos to the group

            else:
                size = uniform(10, 30)
                shape_group.append((type, size))         # add the shape type and its size to the group

        shape_group.append((pos[0], pos[1]))           # add the group x and y position to the last index of the shape_group object
        # if self.hivemind.interrupt_bang:
        self.draw_shape_group(shape_group, 0)              # draw the group with 0 variation of size

    def draw_shape_group(self, group, variation=0):
        """
        Takes a shape group list and draws all the shapes within it. Also adds it to the
        list of shape groups and sets the last drawn shape group to this one.
        """
        pos = group[len(group) - 1]     # group pos is stored in the last index of the shape group list

        for i in range(len(group) - 1):     # last element in group is the position
            # if self.hivemind.interrupt_bang:
            match group[i][0]:              # [i][0] = shape type
                case Shapes.Square:
                    self.draw_square(group[i][1] + variation)     # [i][1] = size (when shape isn't a line)
                case Shapes.Triangle:
                    self.draw_triangle(group[i][1] + variation)   # size variation can be added when group is re-drawn
                case Shapes.Sunburst:
                    self.draw_sunburst(group[i][1] + variation)
                case Shapes.Irregular:
                    self.draw_irregular_shape(randrange(3,8))     # irregular shape will always be random
                case Shapes.Circle:
                    self.draw_circle(group[i][1] + variation)
                case Shapes.Line:
                    local_target = group[i][1]                    # [i][1] = local_target_pos (when shape is a line)
                    self.go_draw(pos[0] + local_target[0], pos[1] + local_target[1])    # draw the line then go back to original group position
                    self.go_draw(pos[0], pos[1])

            self.shape_groups.append(group)                     # add shape_group object to list
            self.last_shape_group = group                       # set most recent shape group to this one, is used in repeat_shape_group

    def repeat_shape_group(self):
        """
        Repeats the last drawn shape group with a random offset
        position and slight variation to shape sizes.
        """
        shape_group = self.last_shape_group         # get the last drawn shape group

        old_pos = shape_group[len(shape_group) - 1]     # get the position of the previous shape group ( last index in list )

        new_pos = [                                 # point at a random distance from the previous shape group
            old_pos[0] + uniform(-20, 20),          # new position at random distance from old position
            old_pos[1] + uniform(-20, 20)
        ]

        shape_group[len(shape_group) - 1] = new_pos     # set the shape group position to the new pos with offset

        # if self.hivemind.interrupt_bang:
        self.go_draw(new_pos[0], new_pos[1])    # go to new position
        self.draw_shape_group(shape_group, uniform(-3, 3))  # red-draw shape group, set variation param to random, varies sizes when re-drawing shape group

    #-- return to shape functions --#
    def return_to_square(self):     # returns to a random pre-existing square and does something
        """
        Randomly chooses a square from the 'squares' list and
        randomly chooses a behaviour to do with it.
        """
        square_length = int(len(self.squares))
        if square_length > 0:
            # if self.hivemind.interrupt_bang:
            square = self.squares[int(uniform(0, square_length))]
            print(square)

            rand = uniform(0, 1)

            if rand == 0:              # move to a random corner on the square and draw a new square with a random size
                randCorner = uniform(0,3)
                self.go_draw_up(square[randCorner][0], square[randCorner][1], square[randCorner][2], square[randCorner][3], wait=True)  # go to a random corner of the square (top right = 0, goes anti-clockwise)
                self.draw_square(uniform(20,29), True)
            else:                       # draw a cross in the square
                self.go_draw_up(square[0][0], square[0][1], square[0][2], square[0][3], wait=True)
                self.move_to(square[2][0], square[2][1], square[2][2], square[2][3], wait=True)
                self.go_draw_up(square[1][0], square[1][1], square[1][2], square[1][3], wait=True)
                self.move_to(square[3][0], square[3][1], square[3][2], square[3][3], wait=True)

                #device.move_to(square[1][0], square[1][1], square[1][2], square[1][3], wait=True)  #redraw the square from top right corner anti-clockwise
            #device.move_to(square[2][0], square[2][1], square[2][2], square[2][3], wait=True)
            #device.move_to(square[3][0], square[3][1], square[3][2], square[3][3], wait=True)
            #device.move_to(square[0][0], square[0][1], square[0][2], square[0][3], wait=True)

        else:
            print("cannot return to square, no squares in list")

    def return_to_sunburst(self):
        """
        Randomly chooses a sunburst from the 'sunbursts' list
        and randomly chooses a behaviour to do with it.
        """
        sunbursts_length = int(len(self.sunbursts))
        if sunbursts_length > 0:
            sunburst = self.sunbursts[int(uniform(0, sunbursts_length))]
            print(sunburst)

            rand = uniform(0,1)      #randomly choose between two behaviours

            if rand == 0:                  #join up the ends of the sunburst lines
                self.go_draw_up(sunburst[0][0], sunburst[0][1], sunburst[0][2], sunburst[0][3], wait=True) 
                self.move_to(sunburst[1][0], sunburst[1][1], sunburst[1][2], sunburst[1][3], wait=True)
                self.move_to(sunburst[2][0], sunburst[2][1], sunburst[2][2], sunburst[2][3], wait=True)
                self.move_to(sunburst[3][0], sunburst[3][1], sunburst[3][2], sunburst[3][3], wait=True)
                self.move_to(sunburst[4][0], sunburst[4][1], sunburst[4][2], sunburst[4][3], wait=True)
            else:                           # go to the end of one of the sunburst lines and draw another sunburst
                self.go_draw_up(sunburst[2][0], sunburst[2][1], sunburst[2][2], sunburst[2][3], wait=True)  
                self.draw_sunburst(20, True)

        else:
            print("cannot return to sunburst, no sunbursts in list")

    def return_to_irregular(self):
        """
        Randomly chooses an irregular shape from the 'irregulars'
        list and randomly chooses a behaviour to do with it.
        """
        irregulars_length = int(len(self.irregulars))
        if irregulars_length > 0:
            irregular = self.irregulars[randrange(0, irregulars_length)]

            #rand = random.uniform(0,1)     #add random choice of behaviours
            #if(rand == 0):

            rand_vertex = irregular[randrange(0,len(irregular))]
            # if self.hivemind.interrupt_bang:
            self.go_draw(rand_vertex[0], rand_vertex[1])
            self.draw_irregular_shape(randrange(3,8))

        else:
            print("Cannot return to irregular, no irregulars in list")

    def return_to_char(self):
        """
        Randomly chooses a character from the 'chars' list and
        randomly chooses a behaviour to do with it. (NOT FINISHED)
        """
        chars_length = int(len(self.chars))
        if chars_length > 0:
            char = self.chars[randrange(0, chars_length)]     # pick a char at random, do something with it

        else:
            print("Cannot return to char, no chars in list")
    
    def return_to_coord(self):
        """
        Randomly choose a coordinate from the list of coords and move the pen to it.
        Unlike the other return_to funtions it doesn't do anything other than move to that coord.
        """
        coords_length = int(len(self.coords))
        if coords_length > 0:
            coord = self.coords[randrange(0, coords_length)]
            # if self.hivemind.interrupt_bang:
            self.go_draw_up(coord[0], coord[1])
