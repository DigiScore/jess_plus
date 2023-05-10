import logging
import math
import numpy as np
import struct
from enum import Enum
from random import choice, getrandbits, random, randrange, uniform
from threading import Thread
from time import time, sleep

from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs

import config
from nebula.hivemind import DataBorg


class Shapes(Enum):
    Square = 0
    Triangle = 1
    Sunburst = 2
    Irregular = 3
    Circle = 4
    Line = 5


class Drawbot(Dobot):
    """
    Translation class for Digibot control and primitive commands of robot arm.
    """
    def __init__(self, port, verbose):
        self.hivemind = DataBorg()

        # Init and inherit the Dobot library
        super().__init__(port, verbose)

        # Shared list / dict
        self.ready_position = [250, 0, 20, 0]
        self.draw_position = [250, 0, 0, 0]
        self.position_one = [250, config.y_extents[0], 0, 0]
        self.position_two = [250, config.xarm_y_extents[1], 0, 0]
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
        self.chars = ["A", "B", "C", "D", "E", "F", "G", "P", "Z"]

        self.shape_groups = []  # list of shape groups [shape type, size, pos]
        self.coords = []  # list of coordinates drawn
        self.positions = []
        self.last_shape_group = None

        # Create a command list
        self.command_list = []
        self.wait = True  # TODO: potential issue with the Dobot wait method

        # Timing vars
        self.duration_of_piece = config.duration_of_piece
        self.start_time = time()

    ###########################################################################
    # Command queue control & safety checks
    ###########################################################################
    def command_list_main_loop(self):
        """
        Main loop thread for parsing command loop and rocker lock
        """
        print("Started command list thread")
        list_thread = Thread(target=self.manage_command_list)
        list_thread.start()

    def manage_command_list(self):
        """
        Watches hivemind.interrupt_bang for `False` then clears command_list.
        """
        while self.hivemind.running:
            if not self.hivemind.interrupt_clear:
                self.clear_commands()
                logging.info("Cleared commands")
                self.hivemind.interrupt_clear = True

            if self.command_list:
                if random() >= 0.36:
                    msg_to_send = self.command_list.pop(0)
                else:
                    msg_to_send = choice(self.command_list)
                self._send_command(msg=msg_to_send, wait=self.wait)
            sleep(0.05)

    def custom_set_ptp_cmd(self,
                           params: list,
                           cmd_id: int = 84,
                           mode: PTPMode = None,
                           wait: bool = True):
        """
        Builds a Message for Dobot and adds to command list.

        Parameters
        ----------
        params : list
            List of parameters to build Message.

        cmd_id : int
            Dobot hex id for command.

        mode : int
            Optional. Is building a set_ptp_cmd.

        wait : bool
            Defers to global self.wait.
        """

        msg = Message()
        msg.id = cmd_id
        msg.ctrl = 0x03
        msg.params = bytearray([])
        if mode:
            msg.params.extend(bytearray([mode.value]))
        for _p in params:
            msg.params.extend(bytearray(struct.pack('f', _p)))

        if self.hivemind.interrupt_clear:
            print('Sending message ', msg)
            self.command_list.append(msg)

    def _send_command(self,
                      msg: Message,
                      wait: bool = False):
        """
        Override the Dobot function, but still sends and receives Messages to
        Dobot. Controls all wait commands using command_id. Implements a
        try-except to avoid struct errors. Pops next command in Q.

        Parameters
        ----------
        msg : Message
            A message object.

        wait : bool
            Whether to wait for the command to be executed.

        Returns
        -------
        response
            Read response from the Dobot.
        """
        self.lock.acquire()
        self._send_message(msg)
        response = self._read_message()
        self.lock.release()

        return response

    def get_normalised_position(self):
        """
        While running generate the normalised x, y, z position for NNets
        """
        while self.hivemind.running:
            pose = self.get_pose()[:3]

            norm_x = ((pose[0] - config.x_extents[0]) / (config.x_extents[1] - config.x_extents[0])) * (1 - 0) + 0
            norm_y = ((pose[1] - config.y_extents[0]) / (config.y_extents[1] - config.y_extents[0])) * (1 - 0) + 0
            norm_z = ((pose[2] - config.z_extents[0]) / (config.z_extents[1] - config.z_extents[0])) * (1 - 0) + 0

            norm_xyz = (norm_x, norm_y, norm_z)
            norm_xyz = tuple(np.clip(norm_xyz, 0.0, 1.0))
            norm_xy_2d = np.array(norm_xyz[:2])[:, np.newaxis]

            self.hivemind.current_robot_x_y_z = norm_xyz
            self.hivemind.current_robot_x_y = np.append(self.hivemind.current_robot_x_y, norm_xy_2d, axis=1)
            self.hivemind.current_robot_x_y = np.delete(self.hivemind.current_robot_x_y, 0, axis=1)

            sleep(0.1)

    def safety_position_check(self,
                              x: float,
                              y: float,
                              z: float) -> tuple:
        """
        Check generated move does not exceed defined extents, if it does,
        adjust to remain inside.

        Parameters
        ----------
        x : float
            x coordinate
        y : float
            y coordinate
        z : float
            z coordinate

        Returns
        -------
        return_pose : tuple
            The corrected (x, y, z) position.
        """
        pos_changed = False

        # Check x
        if x < config.x_extents[0]:
            x = config.x_extents[0]
            pos_changed = True
        elif x > config.x_extents[1]:
            x = config.x_extents[1]
            pos_changed = True

        # Check y
        if y < config.y_extents[0]:
            y = config.y_extents[0]
            pos_changed = True
        elif y > config.y_extents[1]:
            y = config.y_extents[1]
            pos_changed = True

        # Check z
        if z < config.z_extents[0]:
            z = config.z_extents[0]
            pos_changed = True
        elif z > config.z_extents[1]:
            z = config.z_extents[1]
            pos_changed = True

        return_pose = (x, y, z)
        return return_pose

    def rnd(self, power_of_command: int) -> int:
        """
        Return a randomly generated positive or negative integer, influenced
        by the incoming power factor.
        """
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result

    def clear_alarms(self) -> None:
        """
        Clear the alarms log and LED.
        """
        msg = Message()
        msg.id = 20  # this should be 21, but that doesn't work...
        msg.ctrl = 0x01
        self._send_command(msg)  # empty response

    def clear_commands(self):
        """
        Clear all commands in Dobot buffer.
        """
        self._set_queued_cmd_stop_exec()
        sleep(0.1)
        self._set_queued_cmd_clear()
        sleep(0.1)
        self._set_queued_cmd_start_exec()

    def get_pose(self):
        """
        Get the robot pose.
        """
        return self.pose()

    ###########################################################################
    # Core functions
    ###########################################################################
    # Low level functions for communicating direct to Dobot primitives. All the
    # notation functions below need to call these.
    def arc(self, x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=True):
        """
        Draw an arc defined by:
            a) Circumference of arc (x, y, z, r)
            b) Finishing coordinates (cirx, ciry, cirz, cirr)
        """
        self.coords.append((x, y))
        params = [x, y, z, r, cir_x, cir_y, cir_z, cir_r]
        self.custom_set_ptp_cmd(params=params,
                                cmd_id=101,
                                mode=None,
                                wait=wait)

    def arc2D(self, apex_x, apex_y, target_x, target_y, wait=True):
        """
        Simplified arc function for drawing 2D arcs on the x, y axis.
            Apex x and y determine the coordinates of the apex of the curve.
            Target x and y determine the end point of the curve.
        """
        pos = self.get_pose()
        self.coords.append(pos[:2])
        params = [apex_x, apex_y, pos[2], pos[3], target_x, target_y, pos[2], pos[3]]
        self.custom_set_ptp_cmd(params=params,
                                cmd_id=101,
                                mode=None,
                                wait=wait)

    def move_y(self):
        """
        Move the pen across the y-axis aligned to the delta change in time
        across the duration of the piece.
        """
        # How far into the piece
        elapsed = time() - self.start_time

        # Get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        newy = (((elapsed - 0) * (2*175)) / (self.duration_of_piece - 0)) - 175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # Check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # Which mode
        self.bot_move_to(x, newy, z, r, self.wait)

        logging.info(f'Move to x:{round(x)} y:{round(newy)} z:{round(z)}')

    def move_y_random(self):
        """
        Move x and y pen position to nearly the true y point.
        """
        # How far into the piece
        elapsed = time() - self.start_time

        # Get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        newy = (((elapsed - 0) * (2*175)) / (self.duration_of_piece - 0)) - 175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # Check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        self.jump_to(x + self.rnd(10), newy + self.rnd(10), 0, r, self.wait)

    def go_position_ready(self):
        """
        Move directly to pre-defined ready position.
        """
        x, y, z, r = self.ready_position[:4]
        self.bot_move_to(x, y, z, r, wait=self.wait)

    def go_position_one_two(self):
        """
        Move to prep positions one two with jumps.
        """
        self.go_draw_up(*self.position_one[:2], wait=True)
        self.go_draw_up(*self.position_two[:2], wait=True)

    def go_position_draw(self):
        """
        Move directly to pre-defined draw position.
        """
        x, y, z, r = self.draw_position[:4]
        self.bot_move_to(x, y, z, r, wait=self.wait)

    def go_position_end(self):
        """
        Moves directly to pre-defined end position.
        """
        x, y, z, r = self.end_position[:4]
        self.bot_move_to(x, y, z, r, wait=self.wait)

    def joint_move_to(self, j1, j2, j3, j4, wait=True):
        """
        Move specific joints direct to new angles.
        """
        self.joint_move_to(j1, j2, j3, j4, self.wait)

    def home(self):
        """
        Go directly to the home position (0, 0, 0, 0).
        """
        msg = Message()
        msg.id = CommunicationProtocolIDs.SET_HOME_CMD
        msg.ctrl = ControlValues.THREE
        return self._send_command(msg, wait=True)

    def bot_move_to(self, x, y, z, r, wait=True):
        self.move_to(x, y, z, r, self.wait)

    def set_speed(self, arm_speed: float = 100):
        self.speed(velocity=arm_speed, acceleration=arm_speed)

    def go_draw(self,
                x: float,
                y: float,
                wait: bool = True):
        """
        Go to an x and y position with the pen touching the paper.
        """
        nx, ny, nz = self.safety_position_check(x, y, 0)
        self.coords.append((nx, ny))
        self.custom_set_ptp_cmd(params=[x, y, self.draw_position[2], 0],
                                mode=PTPMode.MOVJ_XYZ,
                                wait=self.wait)

    def go_draw_up(self, x, y, wait=True):
        """
        Lift the pen up, go to an x and y position, then lower the pen.
        """
        nx, ny, nz = self.safety_position_check(x, y, 0)
        self.coords.append((nx, ny))
        self.custom_set_ptp_cmd(params=[x, y, self.draw_position[2], 0],
                                mode=PTPMode.JUMP_XYZ,
                                wait=self.wait)

    def go_random_draw(self):
        """
        Move to a random position within the x and y extents with the pen
        touching the page.
        """
        x = uniform(self.x_extents[0], self.x_extents[1])
        y = uniform(self.y_extents[0], self.y_extents[1])
        z = self.draw_position[2]
        r = 0

        nx, ny, nz = self.safety_position_check(x, y, 0)
        self.coords.append((nx, ny))
        logging.info("Random draw pos x:", round(x, 2), " y:", round(y, 2))
        self.custom_set_ptp_cmd(params=[x, y, z, r],
                                mode=PTPMode.MOVJ_XYZ,
                                wait=True
                                )

    def go_random_jump(self):
        """
        Lift the pen, move to a random position within the x and y extents,
        then lower the pen to draw position.
        """
        x = uniform(self.x_extents[0], self.x_extents[1])
        y = uniform(self.y_extents[0], self.y_extents[1])

        nx, ny, nz = self.safety_position_check(x, y, 0)
        self.coords.append((nx, ny))
        logging.info("Random draw pos above page x:", nx, " y:", ny)
        self.custom_set_ptp_cmd(params=[nx, ny, 0, 0],
                                mode=PTPMode.JUMP_XYZ,
                                wait=self.wait)

    def position_move_by(self, dx, dy, dz, wait=True):
        """
        Increment the robot cartesian position by x, y, z. Check that the arm
        isn't going out of x, y, z extents.
        """
        x, y, z = self.get_pose()[:3]
        x += dx
        y += dy
        z += randrange(self.z_extents[1])

        nx, ny, nz = self.safety_position_check(x, y, z)
        self.coords.append((nx, ny))
        self.custom_set_ptp_cmd(params=[nx, ny, nz, 0],
                                mode=PTPMode.MOVJ_XYZ,
                                wait=self.wait)

    ###########################################################################
    # Notation functions
    ###########################################################################
    # Mid level functions for drawing the shapes of the notation.
    # All of these notation functions need to call the low level functions
    # above and not the Dobot primitives directly.
    def squiggle(self, arc_list: list):
        """
        Draw a squiggle based on a list of tuples that define a sequence of
        x, y deltas to create a sequence of arcs.

        Parameters
        ----------
        arc_list : list
            List of (circumference point, end point x, end point y).
            Circumference point being size of arc in pixels across x axis. End
            point x and end point y being distance from last / previous
            position.
        """
        [x, y, z, r] = self.get_pose()[0:4]
        self.coords.append((x, y))
        for arc in arc_list:
            circumference, dx, dy = arc[0], arc[1], arc[2]
            self.arc(x + circumference, y, z, r, x + dx, y + dy, z, r)
            x += dx
            y += dy
            sleep(0.2)

    def dot(self):
        """
        Draws a small dot at current position.
        """
        self.note_head(1)

    def note_head(self, size: float = 5):
        """
        Draws a circle at the current position.
        Default is 5 pixels diameter.
        Args:
            size: radius in pixels
            drawing: True = pen on paper
            wait: True = wait till sequence finished
            """
        (x, y, z, r, j1, j2, j3, j4) = self.get_pose()
        self.arc(x + size, y, z, r, x + 0.01, y + 0.01, z, r)

    def draw_square(self, size):
        """
        Draw a square from the pen's current position. Start from top left
        vertex and draw anti-clockwise. Positions are saved to the squares
        array to be accessed by other functions.

        Parameters
        ----------
        size : float
            Size of the square.
        """
        pos = self.get_pose()[:2]
        square = []
        local_pos = [(size, 0), (size, size), (0, size)]

        for i in range(len(local_pos)):
            next_pos = [
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1]
            ]
            self.go_draw(next_pos[0], next_pos[1])
            square.append(next_pos)
            self.coords.append(next_pos)

        self.go_draw(pos[0], pos[1], wait=self.wait)
        self.squares.append(square)

    def draw_triangle(self, size):
        """
        Draw a triangle from the current pen position. Randomly chooses a type
        of triangle to draw and uses the size parameter to determine the size.
        For irregular triangles, use draw_irregular (3).

        Parameters
        ----------
        size : float
            Size of the triangle.
        """
        pos = self.get_pose()[:2]  # x, y
        triangle = []

        rand_type = randrange(0, 2)
        if rand_type == 0:
            # Right angle triangle
            local_pos = [(0, 0), (-size, 0), (-size, size)]

        elif rand_type == 1:
            # Isosceles triangle
            local_pos = [(0, 0),
                         (-size * 2, - size / 2),
                         (- size * 2, size / 2)]

        for i in range(len(local_pos)):
            # Next vertex to go to in world space
            next_pos = [pos[0] + local_pos[i][0],
                        pos[1] + local_pos[i][1]]

            self.go_draw(next_pos[0], next_pos[1], wait=self.wait)

            triangle.append(next_pos)
            self.coords.append(next_pos)

        self.go_draw(pos[0], pos[1])  # go back to the first vertex to join up the shape
        self.triangles.append(triangle)

    def draw_sunburst(self, r, randomAngle=True):
        """
        Draw a sunburst from the pens position. Will draw r number of lines
        coming from the centre point. Can be drawn with lines at random angles
        between 0 and 360 degrees or with pre-defined angles. Positions are
        saved to the sunbursts array to be accessed by other functions.

        Parameters
        ----------
        r : float
            Size of the lines.

        randomAngle : bool
            Random angle.
        """
        pos = self.get_pose()

        if randomAngle is True:
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

        sunburst = []  # saves all points in this sunburst then saves it to the list of drawn sunbursts
        for i in range(len(local_pos)):
            next_pos = [
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1],
            ]
            sunburst.append(next_pos)
            self.coords.append(next_pos)

            self.go_draw(next_pos[0], next_pos[1], wait=self.wait)  # draw line from centre point outwards
            self.go_draw(pos[0], pos[1], wait=self.wait)  # return to centre point to then draw another line

        self.sunbursts.append(sunburst)

    def draw_irregular_shape(self, num_vertices):
        """
        Draw an irregular shape from the current pen position with. Positions
        are saved to the irregulars array to be accessed by other functions.

        Parameters
        ----------
        num_vertices : int
            Number of randomly generated vertices. If set to 0, will be
            randomised between 3 and 10.
        """
        pos = self.get_pose()

        if num_vertices <= 0:
            num_vertices = randrange(3, 10)

        vertices = []
        for i in range(num_vertices):
            x = uniform(-self.irregular_shape_extents, self.irregular_shape_extents)
            y = uniform(-self.irregular_shape_extents, self.irregular_shape_extents)
            vertices.append((x, y))
            self.coords.append((x, y))

        for i in range(len(vertices)):
            x, y = vertices[i]
            x = pos[0] + x
            y = pos[1] + y
            self.go_draw(x, y, self.wait)

        self.go_draw(pos[0], pos[1], self.wait)

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
            self.arc(pos[0] + size,
                     pos[1] - size,
                     pos[2],
                     pos[3],
                     pos[0] + 0.01,
                     pos[1] + 0.01,
                     pos[2],
                     pos[3],
                     wait=self.wait)
        elif side == 1:
            self.arc(pos[0] - size,
                     pos[1] + size,
                     pos[2],
                     pos[3],
                     pos[0] + 0.01,
                     pos[1] + 0.01,
                     pos[2],
                     pos[3],
                     wait=self.wait)

        circle = []
        circle.append(pos)
        circle.append(size)
        circle.append(side)
        self.coords.append(pos)

        self.circles.append(circle)

    def draw_char(self,
                  _char: str,
                  size: float,
                  wait=True):
        """
        Draw a character (letter, number) on the pen's current position.
        Supported characters are as follows:
        A, B, C, D, E, F, G, P, Z. All letters consisting of just straight
        lines are drawn in this function whereas letters with curves are drawn
        in their own respective functions.
        """
        logging.info("Drawing letter: ", _char)
        pos = self.get_pose()[:2]     # x, y
        char = []
        _char = _char.upper()
        char.append(_char)

        jump_num = -1  # determines the characters that need a jump, can't be drawn continuously. If left as -1 then no jump is needed

        # Calculate local_pos for each char
        if _char == "A" or _char == "a":
            local_pos = [
                (0, 0),                  # bottom left
                (size * 2, - size / 2),  # top
                (0, - size),             # bottom right
                (size, - size * 0.75),   # mid right
                (size, - size * 0.25)    # mid left
            ]
        elif _char == "B" or _char == "b":
            self.draw_b(size=size, wait=self.wait)
            return None

        elif _char == "C" or _char == "c":  # for characters with curves, defer to specific functions
            self.draw_c(size=size, wait=self.wait)
            return None

        elif _char == "D" or _char == "d":
            self.draw_d(size=size, wait=self.wait)
            return None

        elif _char == "E" or _char == "e":
            local_pos = [
                (0, 0),            # bottom right
                (0, size),         # bottom left
                (size * 2, size),  # top left
                (size * 2, 0),     # top right
                (size, 0),         # mid right (jump to here)
                (size, size)       # mid left
            ]

            jump_num = 4

        elif _char == "F" or _char == "f":
            local_pos = [
                (0, 0),                  # bottom left
                (size * 2, 0),           # top left
                (size * 2, - size / 2),  # top right
                (size, - size / 2),      # mid right (jump to here)
                (size, 0)                # mid left
            ]

            jump_num = 3

        elif _char == "G" or _char == "g":
            self.draw_g(size=size, wait=self.wait)
            return None

        elif _char == "P" or _char == "p":
            self.draw_p(size=size, wait=self.wait)
            return None

        elif _char == "Z" or _char == "z":
            local_pos = [
                (0, 0),
                (0, size),
                (size * 2, 0),
                (size * 2, size)
            ]

        else:
            logging.warning(f"Input {_char} is not supported by draw_char")
            return None

        # Draw character
        for i in range(len(local_pos)):
            next_pos = [
                pos[0] + local_pos[i][0], pos[1] + local_pos[i][1]  # calculate the next world position to draw
            ]

            if jump_num != -1:  # for characters that need a jump
                if i == jump_num:
                    self.go_draw_up(next_pos[0], next_pos[1])
                else:
                    self.go_draw(next_pos[0], next_pos[1], wait=self.wait)

            else:  # the rest of the letters can be drawn in a continuous line
                self.go_draw(next_pos[0], next_pos[1], wait=True)

            char.append(next_pos)  # append the current position to the letter
            self.coords.append(next_pos)

    def draw_p(self, size, wait=True):
        """
        Draw the letter P at the pens current position.
        Separate from the draw_char() function as it requires an arc.
        Is called in draw_char() when P is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("P")

        local_pos = [
            (0, 0),                       # bottom of letter
            (size * 2, 0),                # top of letter
            (size * 0.75, -size * 0.85),  # peak of curve
            (size * 1.2, 0)               # middle of letter
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
            (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1])
        ]
        self.go_draw(world_pos[1][0], world_pos[1][1])

        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_b(self, size, wait=True):
        """
        Draw the letter B at the pens current position.
        Separate from the draw_char() function as it requires an arc.
        Is called in draw_char() when B is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("B")

        local_pos = [
            (0, 0),               # 0 bottom left
            (size * 2, 0),        # 1 top right
            (size * 1.5, -size),  # 2 peak of top curve
            (size, 0),            # 3 mid left
            (size * 0.5, -size)   # 4 peak of bottom curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
            (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1]),
            (pos[0] + local_pos[4][0], pos[1] + local_pos[4][1])
        ]
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)
        self.arc2D(world_pos[4][0], world_pos[4][1], world_pos[0][0], world_pos[0][1], wait=wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_c(self, size, wait=True):
        """
        Draw the letter C at the pens current position.
        Separate from the draw_char() function as it requires an arc.
        Is called in draw_char() when C is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("C")

        local_pos = [
            (size * 0.3, 0),  # 0 bottom of curve
            (size, size),     # 1 middle of curve
            (size * 1.7, 0)   # 2 top of curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
        ]
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_d(self, size, wait=True):
        """
        Draw the letter D at the pens current position.
        Separate from the draw_char() function as it requires an arc.
        Is called in draw_char() when D is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("D")

        local_pos = [
            (0, 0),         # 0 bottom left
            (size * 2, 0),  # 1 top left
            (size, -size)   # 2 peak of curve
        ]

        world_pos = [
            (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
            (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
            (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
        ]
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[0][0], world_pos[0][1], wait=wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_g(self, size, wait=True):
        """
        Draw the letter G at the pens current position.
        Separate from the draw_char() function as it requires an arc.
        Is called in draw_char() when G is passed as the _char parameter.
        """
        pos = self.get_pose()[:4]
        char = []
        char.append("G")

        local_pos = [
            (0, 0),            # 0 top right
            (- size, size),    # 1 peak of curve
            (- size * 2, 0),   # 2 bottom right
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
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)
        self.go_draw(world_pos[3][0], world_pos[3][1], wait=wait)
        self.go_draw(world_pos[4][0], world_pos[4][1], wait=wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_random_char(self, size=1, wait=True):
        """
        Draw a random character from the list of available characters.
        """

        rand_char = self.chars[randrange(0, len(self.chars))]
        logging.info(rand_char)
        self.draw_char(rand_char, size, self.wait)

    def create_shape_group(self, wait=True):
        """
        Create a new shape group, populates a list with shape group data and
        draws it using draw_shape_group(). Is called once whenever Conducter
        enters repetition mode.
        """
        logging.info("Creating a shape")
        pos = self.get_pose()[:3]  # position of the group
        shapes_num = randrange(2, 4)  # number of shapes in this group
        shape_group = []  # stores the current shape group

        for i in range(shapes_num):
            type = Shapes(randrange(6))  # generate random shape type

            if type == Shapes.Line:  # if it's a line, add the type and x and y target position
                local_target_pos = uniform(-20, 20), uniform(-20, 20)  # random change in position
                shape_group.append((type, local_target_pos))  # add the shape type and its local_pos to the group

            else:
                size = uniform(10, 30)
                shape_group.append((type, size))  # add the shape type and its size to the group

        shape_group.append((pos[0], pos[1]))  # add the group x, y positions to last index of shape_group object
        self.draw_shape_group(shape_group, 0)  # draw the group with 0 variation of size

    def draw_shape_group(self, group, variation=0):
        """
        Take a shape group list and draws all the shapes within it. Also adds
        it to the list of shape groups and sets the last drawn shape group to
        this one.
        """
        pos = group[len(group) - 1]  # group pos is stored in the last index of the shape group list

        for i in range(len(group) - 1):  # last element in group is the position
            match group[i][0]:  # [i][0] = shape type
                case Shapes.Square:
                    self.draw_square(group[i][1] + variation)  # [i][1] = size (when shape isn't a line)
                case Shapes.Triangle:
                    self.draw_triangle(group[i][1] + variation)  # size variation can be added when group is re-drawn
                case Shapes.Sunburst:
                    self.draw_sunburst(group[i][1] + variation)
                case Shapes.Irregular:
                    self.draw_irregular_shape(randrange(3, 8))  # irregular shape will always be random
                case Shapes.Circle:
                    self.draw_circle(group[i][1] + variation)
                case Shapes.Line:
                    local_target = group[i][1]  # [i][1] = local_target_pos (when shape is a line)
                    self.go_draw(pos[0] + local_target[0], pos[1] + local_target[1])  # draw line
                    self.go_draw(pos[0], pos[1])  # go back to original group position

            self.shape_groups.append(group)  # add shape_group object to list
            self.last_shape_group = group  # set most recent shape group to this one, is used in repeat_shape_group

    def repeat_shape_group(self):
        """
        Repeat the last drawn shape group with a random offset position and
        slight variation to shape sizes.
        """
        shape_group = self.last_shape_group  # get the last drawn shape group

        old_pos = shape_group[len(shape_group) - 1]  # get the position of the previous shape group

        new_pos = [
            old_pos[0] + uniform(-20, 20),
            old_pos[1] + uniform(-20, 20)
        ]

        shape_group[len(shape_group) - 1] = new_pos  # set the shape group position to the new pos with offset

        self.go_draw(new_pos[0], new_pos[1])  # go to new position
        self.draw_shape_group(shape_group, uniform(-3, 3))  # red-draw shape group, set variation param to random, varies sizes when re-drawing shape group

    def return_to_coord(self):
        """
        Randomly choose a coordinate from the list of coords and move the pen
        to it. Unlike the other return_to functions it doesn't do anything
        other than move to that coord.
        """
        coords_length = int(len(self.coords))
        if coords_length > 0:
            coord = self.coords[randrange(0, coords_length)]
            self.go_draw_up(coord[0], coord[1])
