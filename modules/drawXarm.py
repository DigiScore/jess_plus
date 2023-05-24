import logging
import math
import numpy as np
from enum import Enum
from random import choice, getrandbits, randrange, uniform
from threading import Thread
from time import time, sleep

from xarm.wrapper.xarm_api import XArmAPI

import config
from nebula.hivemind import DataBorg


class Shapes(Enum):
    Square = 0
    Triangle = 1
    Sunburst = 2
    Irregular = 3
    Circle = 4
    Line = 5


class DrawXarm(XArmAPI):
    """
    Translation class for xArm control and primitive commands of robot arm.
    """
    def __init__(self, port):
        self.hivemind = DataBorg()

        # Init and inherit the XArm_API library
        XArmAPI.__init__(self, port)

        # Get XArm ready to move
        self.motion_enable(enable=True)
        self.set_mode(0)
        self.set_state(state=0)
        boundary_limits = [
            config.xarm_x_extents[1] + config.xarm_irregular_shape_extents,
            config.xarm_x_extents[0] - config.xarm_irregular_shape_extents,
            config.xarm_y_extents[1] + config.xarm_irregular_shape_extents,
            config.xarm_y_extents[0] - config.xarm_irregular_shape_extents,
            config.xarm_z_extents[1] + config.xarm_irregular_shape_extents,
            config.xarm_z_extents[0] - 1]
        self.set_reduced_tcp_boundary(boundary_limits)
        self.set_fence_mode(False)

        # Setup call back for error detection
        self.register_error_warn_changed_callback(
            callback=self.callback_error_manager
        )

        # Init coord params
        self.z = 158
        self.roll = None
        self.pitch = None
        self.yaw = 0
        self.wait = False
        self.speed = 150
        self.mvacc = 150

        # Roll and pitch with pens
        self.compass = [[180, 15],  # north
                        [180, -15],  # south
                        [195, 0],  # east
                        [165, 0]]  # west
        # Roll and pitch as free dance
        self.compass_range = [[270, 90],  # roll min-max
                              [-100, 100]]  # pitch min-max

        self.home()
        self.random_pen()

        # Make a shared list / dict
        self.ready_position = [sum(config.xarm_x_extents)/2, 0, self.z + 100]
        self.draw_position = [sum(config.xarm_x_extents)/2, 0, self.z]
        self.position_one = [sum(config.xarm_x_extents)/2,
                             config.xarm_y_extents[0],
                             self.z]
        self.position_two = [sum(config.xarm_x_extents)/2,
                             config.xarm_y_extents[1],
                             self.z]
        self.x_extents = config.xarm_x_extents
        self.y_extents = config.xarm_y_extents
        self.z_extents = config.xarm_z_extents
        self.irregular_shape_extents = config.xarm_irregular_shape_extents

        self.squares = []
        self.sunbursts = []
        self.irregulars = []
        self.circles = []
        self.triangles = []
        self.chars = ["A", "B", "C", "D", "E", "F", "G", "P", "Z"]

        self.shape_groups = []  # list of shape groups [shape type, size, pos]
        self.coords = []  # list of coordinates drawn

        self.last_shape_group = None

        self.duration_of_piece = config.duration_of_piece
        self.start_time = time()
        self.go_position_ready()

    ###########################################################################
    # Command queue control & safety checks
    ###########################################################################
    def callback_error_manager(self, item):
        """
        Listen to errors, clear alarms and reset to go_random_3d position.
        """
        logging.debug(f'NUMBER OF CMD IN CACHE: {self.cmd_num}')
        logging.debug(f"ITEM: {item}, STATE: {self.get_state()}")
        self.clear_alarms()
        # If Safety Boundary Limit or Speed Exceeds Limit
        if item['error_code'] == 35 or item['error_code'] == 24:
            self.go_random_3d()

    def command_list_main_loop(self):
        """
        Main loop thread for parsing command loop and rocker lock.
        """
        list_thread = Thread(target=self.manage_command_list)
        list_thread.start()

    def manage_command_list(self):
        while self.hivemind.running:
            if self.hivemind.interrupted:
                self.clear_commands()
                logging.info('Clearing command list')
                self.hivemind.interrupted = False

            sleep(0.05)

    def get_normalised_position(self):
        while self.hivemind.running:
            pose = self.position[:3]

            norm_x = ((pose[0] - self.x_extents[0]) / (self.x_extents[1] - self.x_extents[0])) * (1 - 0) + 0
            norm_y = ((pose[1] - self.y_extents[0]) / (self.y_extents[1] - self.y_extents[0])) * (1 - 0) + 0
            norm_z = ((pose[2] - self.z_extents[0]) / (self.z_extents[1] - self.z_extents[0])) * (1 - 0) + 0

            norm_xyz = (norm_x, norm_y, norm_z)
            norm_xyz = tuple(np.clip(norm_xyz, 0.0, 1.0))
            norm_xy_2d = np.array(norm_xyz[:2])[:, np.newaxis]

            self.hivemind.current_robot_x_y_z = norm_xyz
            self.hivemind.current_robot_x_y = np.append(self.hivemind.current_robot_x_y, norm_xy_2d, axis=1)
            self.hivemind.current_robot_x_y = np.delete(self.hivemind.current_robot_x_y, 0, axis=1)

            sleep(0.1)

    def safety_position_check(self,
                              pose: tuple) -> tuple:
        """
        Check that generated move does not exceed defined extents, if it does,
        adjust to remain inside

        Parameters
        ----------
        pose : tuple
            The (x, y, z) position.

        Returns
        -------
        return_pose : tuple
            The corrected (x, y, z) position.
        """
        x, y, z = pose
        pos_changed = False

        # Check x
        if x < self.x_extents[0]:
            x = self.x_extents[0]
            pos_changed = True
        elif x > self.x_extents[1]:
            x = self.x_extents[1]
            pos_changed = True

        # Check x
        if y < self.y_extents[0]:
            y = self.y_extents[0]
            pos_changed = True
        elif y > self.y_extents[1]:
            y = self.y_extents[1]
            pos_changed = True

        # Check z
        if z < self.z_extents[0]:
            z = self.z_extents[0]
            pos_changed = True
        elif z > self.z_extents[1]:
            z = self.z_extents[1]
            pos_changed = True

        return_pose = (x, y, z)
        return return_pose

    def rnd(self, power_of_command: int) -> int:
        """
        Return a randomly generated positive or negative integer, influenced by
        the incoming power factor.
        """
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (uniform(1, 10) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result

    def clear_alarms(self) -> None:
        """
        Clear the alarms logs and warnings.
        """
        if self.has_warn:
            self.clean_warn()
        if self.has_error:
            self.set_state(state=4)
            self.clean_error()
            self.motion_enable(enable=True)
            self.set_state(state=0)

    def clear_commands(self):
        """
        Clear the command cache and waits for next.
        """
        self.set_state(4)
        sleep(0.1)
        self.set_state(0)

    def force_queued_stop(self):
        """
        Emergency stop (set_state(4) -> motion_enable(True) -> set_state(0))
        and return to ZERO.
        """
        self.emergency_stop()

    def get_pose(self):
        """
        Get the robot pose.
        """
        pose = self.last_used_position
        logging.debug(f'POSITION: {self.position[:3]}')
        logging.debug(f'LAST_USED: {pose[:3]}')
        return pose

    def set_speed(self, arm_speed):
        """
        Set speed and max acceleration.
        """
        self.speed = arm_speed
        self.mvacc = arm_speed

    ###########################################################################
    # Core functions
    ###########################################################################
    # Low level functions for communicating direct to xArm primitives. All the
    # notation functions below need to call these.
    def arc(self,
            pose1: list = None,
            pose2: list = None,
            percent: int = 100,
            speed: int = 100,
            mvacc: int = 100,
            wait: bool = False):
        """
        Draw an arc define by the current pose and 2 other poses.Calls xarm
        move_circle, pose = [x, y, z, roll, pitch, yaw] in catesian
        coordinates.
        """
        logging.info('Arc / circle')
        self.move_circle(pose1=pose1,
                         pose2=pose2,
                         percent=percent,
                         speed=speed,
                         mvacc=mvacc,
                         wait=True)
        pose = self.position[:3]
        self.bot_move_to(*pose)  # for updating cache last used position

    def bot_move_to(self,
                    x: float = None,
                    y: float = None,
                    z: float = None,
                    speed: int = 100,
                    mvacc: int = 100,
                    wait: bool = False,
                    relative: bool = False):
        """
        Move to the position (x, y, z) at a given speed and acceleration.
        """
        self.set_position(x=x,
                          y=y,
                          z=z,
                          roll=self.roll,
                          pitch=self.pitch,
                          yaw=self.yaw,
                          speed=speed,
                          mvacc=mvacc,
                          wait=wait,
                          relative=relative)

    def tool_move(self,
                  abs_angle: int,
                  speed: int = 100,
                  mvacc: int = 100,
                  wait: bool = False):
        """
        Moves the tool to an absolute angle.
        """
        self.set_servo_angle(servo_id=6,
                             angle=abs_angle,
                             speed=speed,
                             mvacc=mvacc,
                             wait=wait,
                             relative=False)

    def random_pen(self):
        if config.xarm_multi_pen:
            random_pen = choice(self.compass)
        else:
            random_pen = [uniform(*self.compass_range[0]),
                          uniform(*self.compass_range[1])]
        self.roll, self.pitch = random_pen

    def move_y(self):
        """
        Move the pen across the y-axis aligned to the delta change in time
        across the duration of the piece.
        """
        # How far into the piece
        elapsed = time() - self.start_time

        # Get current y-value
        x, y, z = self.get_pose()[:3]
        newy = ((elapsed * (self.y_extents[1] - self.y_extents[0])) / (self.duration_of_piece)) + self.y_extents[1]

        # Check x-axis is in range
        if x <= config.xarm_x_extents[0] or x >= config.xarm_x_extents[1]:
            x = (config.xarm_x_extents[1] - config.xarm_x_extents[0]) / 2

        logging.info(f'Move x:{round(x)} y:{round(newy)} z:{round(z)}')
        self.bot_move_to(x=x,
                         y=newy,
                         z=self.z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

    def go_position_ready(self):
        """
        Move directly to pre-defined ready position.
        """
        x, y, z = self.ready_position
        self.set_fence_mode(False)
        self.bot_move_to(x=x,
                         y=y,
                         z=z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=True)
        self.set_fence_mode(config.xarm_fenced)

    def go_position_one_two(self):
        """
        Move to prep positions one two with jumps.
        """
        self.go_draw_up(*self.position_one[:2], wait=True)
        self.go_draw_up(*self.position_two[:2], wait=True)

    def go_position_draw(self):
        """
        Move directly to pre-defined drawing position.
        """
        x, y, z = self.draw_position
        self.set_fence_mode(False)
        self.bot_move_to(x=x,
                         y=y,
                         z=z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=True)
        self.set_fence_mode(config.xarm_fenced)

    def home(self):
        """
        Go directly to the home position.
        """
        self.set_fence_mode(False)
        self.bot_move_to(x=180, y=0, z=500, wait=True)

    def go_draw(self, x, y, wait=False):
        """
        Go to an x and y position with the pen touching the paper.
        """
        self.coords.append((x, y))
        self.bot_move_to(x=x,
                         y=y,
                         z=self.z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

    def go_draw_up(self,
                   x: float,
                   y: float,
                   wait: bool = False):
        """
        Lift the pen up, go to an x and y position, then lower the pen.
        """
        jump_height = abs(self.ready_position[-1] - self.z)
        old_x, old_y = self.get_pose()[:2]
        self.coords.append((x, y))

        # Jump off page
        self.bot_move_to(x=old_x,
                         y=old_y,
                         z=self.z + jump_height,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

        # Move to new position
        self.bot_move_to(x=x,
                         y=y,
                         z=self.z + jump_height,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

        # Put pen on paper
        self.bot_move_to(x=x,
                         y=y,
                         z=self.z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

    def go_random_draw(self):
        """
        Move to a random position within the x and y extents with the pen
        touching the page.
        """
        x = uniform(config.xarm_x_extents[0], config.xarm_x_extents[1])
        y = uniform(config.xarm_y_extents[0], config.xarm_y_extents[1])

        self.coords.append((x, y))
        print("Random draw pos x:", round(x, 2), " y:", round(y, 2))
        self.bot_move_to(x=x,
                         y=y,
                         z=self.z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=self.wait)

    def go_random_3d(self):
        """
        Move to a random position within the x, y and z extents in 3D space.
        """
        x = uniform(config.xarm_x_extents[0], config.xarm_x_extents[1])
        y = uniform(config.xarm_y_extents[0], config.xarm_y_extents[1])
        z = uniform(config.xarm_z_extents[0], config.xarm_z_extents[1])

        self.random_pen()

        self.coords.append((x, y))
        print(f"Random 3D pos x: {round(x, 2)}, y: {round(y, 2)}, z: {round(z, 2)}")
        self.set_fence_mode(False)
        self.bot_move_to(x=x,
                         y=y,
                         z=z,
                         speed=self.speed,
                         mvacc=self.mvacc,
                         wait=True)
        self.set_fence_mode(config.xarm_fenced)

    def go_random_jump(self):
        """
        Lift the pen, move to a random position within the x and y extents,
        then lower the pen to draw position.
        """
        x = uniform(config.xarm_x_extents[0], config.xarm_x_extents[1])
        y = uniform(config.xarm_y_extents[0], config.xarm_y_extents[1])

        self.coords.append((x, y))
        print("Random draw pos above page x:", x, " y:", y)
        self.go_draw_up(x=x, y=y)

    def position_move_by(self, dx, dy, dz, wait=False):
        """
        Increment the robot cartesian position by x, y, z. Check that the arm
        isn't going out of x, y, z extents.
        """

        pose = self.get_pose()[:3]

        new_pose = [pose[0] + dx, pose[1] + dy, pose[2] + dz]
        new_corrected_pose = self.safety_position_check(new_pose)
        logging.debug(f'NEW_CORRECTED: {new_corrected_pose}')

        self.coords.append(new_corrected_pose[:2])
        self.bot_move_to(x=new_corrected_pose[0],
                         y=new_corrected_pose[1],
                         z=new_corrected_pose[2],
                         speed=self.speed,
                         mvacc=self.mvacc,
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
            List of arcs.
        """
        x, y, z = self.get_pose()[:3]
        self.coords.append((x, y))

        for arc in arc_list:
            _, dx, dy = arc[0], arc[1], arc[2]

            self.arc(pose1=[x + dx, y, self.z, self.roll, self.pitch, self.yaw],
                     pose2=[x + dx, y + dy, self.z, self.roll, self.pitch, self.yaw],
                     percent=randrange(40, 90),
                     speed=self.speed,
                     mvacc=self.mvacc,
                     wait=True)

            x, y = self.position[:2]

    def dot(self):
        """
        Draw a small dot at current position.
        """
        self.note_head(1)

    def note_head(self, size: float = 5):
        """
        draws a circle at the current position. Default is 5 pixels diameter.

        Parameters
        ----------
        size : float
            Size of the note in mm.
        """
        x, y = self.get_pose()[:2]
        self.arc(pose1=[x + size, y, self.z, self.roll, self.pitch, self.yaw],
                 pose2=[x, y + size, self.z, self.roll, self.pitch, self.yaw],
                 percent=100,
                 speed=self.speed,
                 mvacc=self.mvacc,
                 wait=self.wait)

    def arc2D(self,
              pose1_x: int,
              pose1_y: int,
              pose2_x: int,
              pose2_y: int,
              wait: bool = False):
        """
        Simplified arc function for drawing 2D arcs on the x, y axis.
            Pose 1 x and y determine the coordinates of the first point.
            Pose 2 x and y determine the coordinates of the second point.
        """
        current_x, current_y = self.get_pose()[:2]
        dx = pose1_x - current_x
        pose1 = [pose1_x, current_y, self.z, self.roll, self.pitch, self.yaw]
        pose2 = [pose1_x, current_y + dx, self.z, self.roll, self.pitch, self.yaw]
        rnd_percent = randrange(40, 90)

        self.arc(pose1=pose1,
                 pose2=pose2,
                 percent=rnd_percent,
                 speed=self.speed,
                 mvacc=self.mvacc,
                 wait=self.wait)

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
        x, y = self.get_pose()[:2]
        square = []

        local_pos = [(size, 0), (size, size), (0, size)]

        for i in range(len(local_pos)):
            next_pos = [
                x + local_pos[i][0],
                y + local_pos[i][1]
            ]
            self.go_draw(x=next_pos[0],
                         y=next_pos[1],
                         wait=self.wait)

            square.append(next_pos)
            self.coords.append(next_pos)

        self.go_draw(x=x,
                     y=y,
                     wait=self.wait)

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
            local_pos = [
                (0, 0),
                (-size, 0),
                (-size, size)
            ]

        elif rand_type == 1:
            # Isosceles triangle
            local_pos = [
                (0, 0),
                (-size * 2, - size / 2),
                (- size * 2, size / 2)
            ]

        for i in range(len(local_pos)):
            # Next vertex to go to in world space
            next_pos = [
                pos[0] + local_pos[i][0],
                pos[1] + local_pos[i][1]
            ]
            self.go_draw(x=next_pos[0],
                         y=next_pos[1],
                         wait=self.wait)

            triangle.append(next_pos)
            self.coords.append(next_pos)

        # Go back to the first vertex to join up the shape
        self.go_draw(x=pos[0], y=pos[1], wait=self.wait)
        self.triangles.append(triangle)

    def draw_sunburst(self, r, randomAngle=True):  # draws a sunburst from the robots current position, r = size of lines, num = number of lines
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

            # Draw line from centre point outwards
            self.go_draw(x=next_pos[0], y=next_pos[1], wait=self.wait)

            # Return to centre point to then draw another line
            self.go_draw(x=pos[0], y=pos[1], wait=self.wait)

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
            self.go_draw(x=x, y=y, wait=self.wait)

        # Return to centre point to then draw another line
        self.go_draw(x=pos[0], y=pos[1], wait=self.wait)

        self.irregulars.append(vertices)

    def draw_circle(self, size, side=0, wait=False):
        """
        Draw a circle from the current pen position, following the 'side'
        direction. Allows for creation of figure-8 patterns. The start
        position, size, and side are saved to the circles list.
        """
        x, y, z = self.get_pose()[:3]
        self.coords.append((x, y))

        if side == 0:
            pose1 = [x + size, y, self.z, self.roll, self.pitch, self.yaw]
            pose2 = [x, y + size, self.z, self.roll, self.pitch, self.yaw]

        elif side == 1:
            pose1 = [x - size, y, self.z, self.roll, self.pitch, self.yaw]
            pose2 = [x, y - size, self.z, self.roll, self.pitch, self.yaw]

        self.arc(pose1=pose1,
                 pose2=pose2,
                 percent=100,
                 speed=self.speed,
                 mvacc=self.mvacc,
                 wait=self.wait)

    def draw_char(self, _char, size, wait=False):
        """
        Draw a character (letter, number) on the pen's current position.
        Supported characters are as follows:
        A, B, C, D, E, F, G, P, Z. All letters consisting of just straight
        lines are drawn in this function whereas letters with curves are drawn
        in their own respective functions.
        """
        pos = self.get_pose()[:2]  # x, y
        char = []
        char.append(_char.upper())

        jump_num = -1  # determines the characters that need a jump, cant be drawn continuously. If left as -1 then no jump is needed

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
            logging.warning("Input: ", _char, " is not supported by draw_char")
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
                self.go_draw(next_pos[0], next_pos[1], wait=self.wait)

            char.append(next_pos)  # append the current position to the letter
            self.coords.append(next_pos)

    def draw_p(self, size, wait=False):
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

        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=self.wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_b(self, size, wait=False):
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
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=self.wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=self.wait)
        self.arc2D(world_pos[4][0], world_pos[4][1], world_pos[0][0], world_pos[0][1], wait=self.wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_c(self, size, wait=False):
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
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=self.wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_d(self, size, wait=False):
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
        self.go_draw(world_pos[1][0], world_pos[1][1], wait=self.wait)
        self.arc2D(world_pos[2][0], world_pos[2][1], world_pos[0][0], world_pos[0][1], wait=self.wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_g(self, size, wait=False):
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
        self.arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=self.wait)
        self.go_draw(world_pos[3][0], world_pos[3][1], wait=self.wait)
        self.go_draw(world_pos[4][0], world_pos[4][1], wait=self.wait)

        char.append(world_pos)
        for i in range(len(world_pos)):
            self.coords.append(world_pos[i])

    def draw_random_char(self, size=1, wait=False):
        rand_char = self.chars[randrange(0, len(self.chars))]
        logging.info(rand_char)
        self.draw_char(rand_char, size, wait)

    def create_shape_group(self, wait=False):
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

        shape_group.append(
            (pos[0], pos[1]))  # add the group x and y position to the last index of the shape_group object
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
                    self.go_draw(pos[0] + local_target[0], pos[1] + local_target[1])  # draw the line
                    self.go_draw(pos[0], pos[1])  # go back to original group position

            self.shape_groups.append(group)  # add shape_group object to list
            self.last_shape_group = group  # set most recent shape group to this one, is used in repeat_shape_group

    def repeat_shape_group(self):
        """
        Repeat the last drawn shape group with a random offset position and
        slight variation to shape sizes.
        """
        shape_group = self.last_shape_group  # get the last drawn shape group

        old_pos = shape_group[
            len(shape_group) - 1]  # get the position of the previous shape group ( last index in list )

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
