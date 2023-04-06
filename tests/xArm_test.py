import pydobot
import random
import time
import math
# import keyboard
import struct
from enum import Enum
from time import sleep

from xarm.wrapper.xarm_api import XArmAPI
from modules.drawXarm import DrawXarm
import config

# class RobotMode(Enum):
#     Continuous = 0
#     Modification = 1
#     Inspiration = 2
#     Repetition = 3
#     OffPage = 4

# arm = XArmAPI('192.168.1.222')
# arm.motion_enable(enable=True)
# arm.set_mode(0)
# arm.set_state(state=0)

# instantiate a drawXarm
port = config.xarm1_port
drawbot = DrawXarm(port)

# x, y, z, roll, pitch, yaw

# rl = -180
# pt = 0
# yw= 0

# poses = [
#     [300,  0,   80, rl, pt, yw],
#     [400,  100, 80, rl, pt, yw],
#     [300,  100, 80, rl, pt, yw],
#     [400, -100, 80, rl, pt, yw],
#     [300,  0,   80, rl, pt, yw]
# ]

# # for p in poses:

# ret = drawbot.set_position(*poses[1], speed=50, mvacc=100, wait=True)
# print('set_position, ret: {}'.format(ret))

# #
# drawbot.note_head()
# ret = drawbot.move_circle(pose1=poses[1], pose2=poses[2], percent=100, speed=200, mvacc=1000, wait=True)
# print('move_circle, ret: {}'.format(ret))
#
# # sleep(10)
# # drawbot.clear_commands()
#
#
# ret = drawbot.move_circle(pose1=poses[3], pose2=poses[4], percent=100, speed=200, mvacc=1000, wait=True)
# print('move_circle, ret: {}'.format(ret))

# drawbot.reset(wait=True)
drawbot.disconnect()
#
# ###---Device default positions---###
# ready_position = [250, 0, 20, 0]
# draw_position = [250, 0, -10, 0]
# end_position = [250, 0, 50, 0]
#
# ###---Global vars---###
# x_extents = [160, 350]
# y_extents = [-150, 150]
# z_extents = [draw_position[2], 150]
# irregular_shape_extents = 50
# zigzag_steps = 10
#
# squares = []
# sunbursts = []
# irregulars = []
# circles = []
# triangles = []
# chars = []
#
# shape_interrupt = False
#
# current_mode = RobotMode.Continuous
#
# #-----go to position functions-----#
# def go_position_ready():
#     """Go to the pre-defined ready position. (250, 0, 20)"""
#     x, y, z, r = ready_position[:4]
#     device._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=True)
#
# def go_position_draw():
#     """Go to the pre-defined draw position. (250, 0, -10)"""
#     x, y, z, r = draw_position[:4]
#     device._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=True)
#
# def go_position_end():
#     """Go to the pre-defined end position. (250, 0, 50)"""
#     x, y, z, r = end_position[:4]
#     device._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=True)
#
# def go(x, y, z, wait=True):
#     """Go to an x, y, z position"""
#     device._set_ptp_cmd(x, y, z, 0, mode=PTPMode.MOVJ_XYZ, wait=wait)
#
# def go_draw(x,y, wait=True):
#     """Go to an x and y position with the pen touching the paper"""
#     device._set_ptp_cmd(x, y, draw_position[2], 0, mode=PTPMode.MOVJ_XYZ, wait=wait)
#
# def go_draw_up(x, y, wait=True):
#     """Lift the pen up, go to an x and y position, then lower the pen"""
#     device._set_ptp_cmd(x, y, draw_position[2], 0, mode=PTPMode.JUMP_XYZ, wait=wait)
#
# #-----creative go to position functions-----#
# def go_random_draw():  # goes to random position on the page with pen touching page
#     """Move to a random position within the x and y extents with the pen touching the page."""
#     x = random.uniform(x_extents[0],x_extents[1])
#     y = random.uniform(y_extents[0], y_extents[1])
#     z = draw_position[2]
#     r = 0
#     print("Random draw pos x:", round(x, 2)," y:", round(y,2))
#     device._set_ptp_cmd(x, y, z, r, mode=PTPMode.MOVJ_XYZ, wait=True)
#
# def go_random_draw_up():   #goes to random positon on page with pen above page then back on
#     """Lift the pen, move to a random position within the x and y extents, then lower the pen to draw position."""
#     x = random.uniform(x_extents[0],x_extents[1])
#     y = random.uniform(y_extents[0], y_extents[1])
#     z = draw_position[2]
#     r = 0
#
#     print("Random draw pos above page x:",x," y:",y)
#
#     #device.move_to(pose[0], pose[1], ready_position[2], pose[3], wait=True)    # lift pen up
#     #device.move_to(x, y, ready_position[2], 0, wait=True)           # go to random pos above page
#     #device.move_to(x, y, draw_position[2], 0, wait=True)            # move pen down to page
#     device._set_ptp_cmd(x, y, z, r, mode=PTPMode.JUMP_XYZ, wait=True)
#
# def go_position_zigzag(x, y, z, wait=True):
#     pos = device.pose()[:3]
#
#     dx = x - pos[0]
#     dy = y - pos[1]
#
#     dist = math.sqrt(dx**2 + dy**2)
#     zig_num = round(dist / 6, 0)
#     zig_dist = dist / zig_num
#
#     pos = [
#         pos[0] + zig_num * dx / dist,
#         pos[1] + zig_num * dx / dist
#     ]
#
#     positions = []
#     string = ""
#
#     for i in range(int(zig_num)):
#         _pos = [ pos[0] + (zig_dist * i) * dx / dist, pos[1] + (zig_dist * i) * dy / dist ]
#         positions.append( _pos )
#         string = string + "| x:" + str(round(_pos[0],0)) + "  y:"+ str(round(_pos[1],0))
#     print(string)
#
#     for i in range(len(positions)):
#         go_draw(positions[i][0], positions[i][1], True)
#
# def go_random_zigzag():
#     x = random.uniform(x_extents[0],x_extents[1])
#     y = random.uniform(y_extents[0], y_extents[1])
#     print("Zig zagging to random pos x: ", round(x,2), "   y: ", round(y,2))
#     go_position_zigzag(x, y, 0, True)
#
# def go_position_curve():
#     print("curve")
#
# #-----move by functions-----#
# def position_move_by(x, y, z, wait=True):
#     """Increment the robot cartesian position by x, y, z. Check that the arm isn't going out of x, y, z extents."""
#
#     pose = device.pose()[:3]
#
#     newPose = [pose[0] + x, pose[1] + y, pose[2] + z]       #calulate new position, used for checking
#
#     if(newPose[0] < x_extents[0] or newPose[0] > x_extents[1]):     # check x posiion
#         print("delta x reset to 0")
#         x = 0
#     if(newPose[1] < y_extents[0] or newPose[1] > y_extents[1]):     # check y position
#         print("delta y reset to 0")
#         y = 0
#     if(newPose[2] < z_extents[0] or newPose[2] > z_extents[1]):      # check z height
#         print("delta z reset to 0")
#         z = 0
#
#     device._set_ptp_cmd(x, y, z, 0, mode=PTPMode.MOVJ_XYZ_INC, wait=wait)
#
# def joint_move_by(_j1, _j2, _j3, wait=True):
#     """moves specific joints by an amount."""
#     (j1, j2, j3, j4) = device.pose()[-4:]
#
#     #if(z <= z_extents[0] + 2):  # if the arm is too low, rotate j2 slightly clockwise to raise the arm
#     #    print("joint_move_by z too low, _j2 = -2")
#     #    _j2 = -2
#
#     newPose = [
#         _j1 + j1,
#         _j2 + j2,
#         _j3 + j3
#     ]
#     device._set_ptp_cmd(_j1, _j2, _j3, j4, mode=PTPMode.MOVJ_INC, wait=wait)
#
# #-----drawing movement behaviour functions-----#
# def draw_square(size):      # draws a square at the robots current position with a size and angle (in degrees)
#     """Draw a square from the pen's current position. Start from top left vertex and draw anti-clockwise.
#     Positions are saved to the squares array to be accessed by other functions."""
#     pos = device.pose()[:2]
#     square = []
#
#     local_pos = [
#         (size, 0),
#         (size, size),
#         (0, size)
#     ]
#
#     for i in range(len(local_pos)):
#         next_pos = [
#             pos[0] + local_pos[i][0],
#             pos[1] + local_pos[i][1]
#         ]
#         go_draw(next_pos[0], next_pos[1])
#         square.append(next_pos)
#
#     go_draw(pos[0], pos[1], wait=False)
#
#     squares.append(square)
#
# def draw_triangle(size):
#     """Draws a triangle from the current pen position. Randomly chooses a type of triangle to draw
#     and uses the size parameter to determine the size. For irregular triangles, use draw_irregular(3)."""
#     pos = device.pose()[:2]     # x, y
#     triangle = []
#
#     rand_type = random.randrange(0,2)
#     if(rand_type == 0):
#         #right angle triangle
#         local_pos = [
#             (0, 0),
#             (-size, 0),
#             (-size, size)
#         ]
#
#     elif(rand_type == 1):
#         #isosceles triangle
#         local_pos = [
#             (0, 0),
#             (-size * 2, - size / 2),
#             (- size * 2, size / 2)
#         ]
#
#     for i in range(len(local_pos)):
#         next_pos = [                    # next vertex to go to in world space
#             pos[0] + local_pos[i][0],
#             pos[1] + local_pos[i][1]
#         ]
#         if shape_interrupt == False:
#             go_draw(next_pos[0], next_pos[1], wait=True)
#         else:
#             shape_interrupt = False
#             return None
#
#         triangle.append(next_pos)
#
#     go_draw(pos[0], pos[1])     # go back to the first vertex to join up the shape
#     triangles.append(triangle)
#
# def draw_sunburst(r, randomAngle):    # draws a sunburst from the robots current position, r = size of lines, num = number of lines
#     """Draw a sunburst from the pens position. Will draw r number of lines coming from the centre point.
#     Can be drawn with lines at random angles between 0 and 360 degrees or with pre-defined angles. Positions are saved to the sunbursts array to be accessed by other functions."""
#     pos = device.pose()
#     device.speed(200,200)
#
#     if(randomAngle == True):
#         random_angles = [
#             random.uniform(0,360),
#             random.uniform(0,360),
#             random.uniform(0,360),
#             random.uniform(0,360),
#             random.uniform(0,360)
#         ]
#         local_pos = [
#             (r * math.sin(random_angles[0]),r * math.cos(random_angles[0])),
#             (r * math.sin(random_angles[1]),r * math.cos(random_angles[1])),
#             (r * math.sin(random_angles[2]),r * math.cos(random_angles[2])),
#             (r * math.sin(random_angles[3]),r * math.cos(random_angles[3])),
#             (r * math.sin(random_angles[4]),r * math.cos(random_angles[4]))
#         ]
#     else:
#         local_pos = [
#             (r * math.sin(320),r * math.cos(320)),
#             (r * math.sin(340),r * math.cos(340)),
#             (r * math.sin(0),r * math.cos(0)),
#             (r * math.sin(20),r * math.cos(20)),
#             (r * math.sin(40),r * math.cos(40))
#         ]
#
#     sunburst = []  #saves all points in this sunburst then saves it to the list of drawn sunbursts
#     for i in range(len(local_pos)):
#
#         next_pos = [
#             pos[0] + local_pos[i][0],
#             pos[1] + local_pos[i][1],
#         ]
#         sunburst.append(next_pos)
#
#         go_draw(next_pos[0], next_pos[1], wait=False)       #draw line from centre point outwards
#         go_draw(pos[0], pos[1], wait=False)              #return to centre point to then draw another line
#
#     sunbursts.append(sunburst)
#
# def draw_irregular_shape(num_vertices):
#     """Draws an irregular shape from the current pen position with 'num_vertices' number of randomly generated vertices. If set to 0, 'num_vertices' will be randomised between 3 and 10.
#     Positions are saved to the irregulars array to be accessed by other functions."""
#     pos = device.pose()
#
#     if(num_vertices <= 0):
#         num_vertices = random.randrange(3, 10)
#
#     vertices = []
#     for i in range(num_vertices):
#         x = random.uniform(-irregular_shape_extents,irregular_shape_extents)
#         y = random.uniform(-irregular_shape_extents, irregular_shape_extents)
#         vertices.append((x,y))
#
#     for i in range(len(vertices)):
#         x, y = vertices[i]
#         x = pos[0] + x
#         y = pos[1] + y
#         device._set_ptp_cmd(x, y, draw_position[2], 0, mode=PTPMode.MOVJ_XYZ, wait=True)
#
#     device._set_ptp_cmd(pos[0], pos[1], pos[2], 0, mode=PTPMode.MOVJ_XYZ, wait=True)
#     irregulars.append(vertices)
#
# def draw_spiral(radius, height, distance, revolutions):
#     print("drawing spiral")
#     pos = device.pose()
#
#     for i in range(revolutions * 360):
#         angle = i * math.pi / 180
#         print("calculated angle: ", angle)
#         x = radius * math.cos(angle)
#         print("calculated x: ", x)
#         y = radius * math.sin(angle)
#         print("calculated y: ", y)
#         z = height - distance * angle / (2 * math.pi)
#         print("calculated z: ", z)
#
#         x = x + pos[0]
#         y = y + pos[1]
#         z = z + pos[2]
#
#         device._set_ptp_cmd(x, y, z, 0, mode=PTPMode.MOVJ_XYZ, wait=True)
#         print("moved robot")
#         #time.sleep(0.05)
#
# def draw_char(_char, size, wait=True):
#     """Draws a character (letter, number) on the pens current position. Supported characters are as follows:
#     A, B, C, D, E, F, G, P. All letters consisting of just straight lines are drawn in this function whereas
#     letters with curves are drarn in their own respective functions."""
#     #print("Drawing letter: ", _char)
#     pos = device.pose()[:2]     # x, y
#     char = []
#     char.append(_char.upper())
#
#     jump_num = -1   # determines the characters that need a jump, cant be drawn continuously. If left as -1 then no jump is needed
#
#     #----Calculate local_pos for each char----#
#     if _char == "A" or _char == "a":
#
#         local_pos = [
#             (0, 0),                     # bottom left
#             (size * 2, - size / 2),     # top
#             (0, - size),                # bottom right
#             (size, - size * 0.75),      # mid right
#             (size, - size * 0.25)       # mid left
#         ]
#     elif _char == "B" or _char == "b":
#         print("B")
#         draw_b(size=size, wait=wait)
#         return None
#
#     elif _char == "C" or _char == "c":  # for characters with curves, defer to specific functions
#         draw_c(size=size, wait=wait)
#         return None                     # everything else is handled in draw_c, can exit function here
#
#     elif _char == "D" or _char == "d":
#         draw_d(size=size, wait=wait)
#         return None
#
#     elif _char == "E" or _char == "e":
#         local_pos = [
#             (0, 0),             # bottom right
#             (0, size),          # bottom left
#             (size * 2, size),   # top left
#             (size * 2, 0),      # top right
#             (size, 0),          # mid right (jump to here)
#             (size, size)        # mid left
#         ]
#
#         jump_num = 4
#
#     elif _char == "F" or _char == "f":
#         local_pos = [
#             (0, 0),                 # bottom left
#             (size * 2, 0),          # top left
#             (size * 2, - size / 2), # top right
#             (size, - size / 2),     # mid right (jump to here)
#             (size, 0)               # mid left
#         ]
#
#         jump_num = 3
#
#     elif _char == "G" or _char == "g":
#         draw_g(size=size, wait=wait)
#         return None
#
#     elif _char == "P" or _char == "p":
#         draw_p(size=size, wait=wait)
#         return None
#
#     elif _char == "Z" or _char == "z":
#         local_pos = [
#             (0, 0),
#             (0, size),
#             (size * 2, 0),
#             (size * 2, size)
#         ]
#
#     else:
#         print("Input: ", _char, " is not supported by draw_char")
#         return None
#
#     #----Draw character----#
#     for i in range(len(local_pos)):
#         next_pos = [
#             pos[0] + local_pos[i][0], pos[1] + local_pos[i][1]  # calculate the next world position to draw
#         ]
#
#         if jump_num != -1:                      # for characters that need a jump
#             if i == jump_num: go_draw_up(next_pos[0], next_pos[1])
#             else: go_draw(next_pos[0], next_pos[1], wait=True)
#
#         else:                                   # the rest of the letters can be drawn in a continuous line
#             go_draw(next_pos[0], next_pos[1], wait=True)
#
#         char.append(next_pos)     # append the current position to the letter
#
#     chars.append(char)          # add the completed character to the characters list
#
# def draw_p(size, wait=True):
#     """Draws the letter P at the pens current position. Seperate from the draw_char() function as it requires an arc.
#     Is called in draw_char() when P is passed as the _char parameter."""
#     pos = device.pose()[:4]
#     char = []
#     char.append("P")
#
#     local_pos = [
#         (0           , 0),                 # bottom of letter
#         (size * 2    , 0),          # top of letter
#         (size * 0.75 , -size * 0.85),   # peak of curve
#         (size * 1.2  , 0)               # middle of letter
#     ]
#
#     world_pos = [
#         (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
#         (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
#         (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
#         (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1])
#     ]
#
#     go_draw(world_pos[1][0], world_pos[1][1])
#     arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)
#
#     char.append(world_pos)
#     chars.append(char)
#
# def draw_b(size, wait=True):
#     """Draws the letter B at the pens current position. Seperate from the draw_char() function as it requires an arc.
#     Is called in draw_char() when B is passed as the _char parameter."""
#     pos = device.pose()[:4]
#     char = []
#     char.append("B")
#
#     local_pos = [
#         (0, 0),                 # 0 bottom left
#         (size * 2, 0),          # 1 top right
#         (size * 1.5, -size),    # 2 peak of top curve
#         (size, 0),              # 3 mid left
#         (size * 0.5, -size)     # 4 peak of bottom curve
#     ]
#
#     world_pos = [
#         (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
#         (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
#         (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
#         (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1]),
#         (pos[0] + local_pos[4][0], pos[1] + local_pos[4][1])
#     ]
#
#     go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
#     arc2D(world_pos[2][0], world_pos[2][1], world_pos[3][0], world_pos[3][1], wait=wait)
#     arc2D(world_pos[4][0], world_pos[4][1], world_pos[0][0], world_pos[0][1], wait=wait)
#
#     char.append(world_pos)
#     chars.append(char)
#
# def draw_c(size, wait=True):
#     """Draws the letter C at the pens current position. Seperate from the draw_char() function as it requires an arc.
#     Is called in draw_char() when C is passed as the _char parameter."""
#     pos = device.pose()[:4]
#     char = []
#     char.append("C")
#
#     local_pos = [
#         (size * 0.3 , 0),      # 0 bottom of curve
#         (size       , size),      # 1 middle of curve
#         (size * 1.7 , 0)       # 2 top of curve
#     ]
#
#     world_pos = [
#         (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
#         (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
#         (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
#     ]
#
#     arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)
#
#     char.append(world_pos)
#     chars.append(char)
#
# def draw_d(size, wait=True):
#     """Draws the letter D at the pens current position. Seperate from the draw_char() function as it requires an arc.
#     Is called in draw_char() when D is passed as the _char parameter."""
#     pos = device.pose()[:4]
#     char = []
#     char.append("D")
#
#     local_pos = [
#         (0, 0),                 # 0 bottom left
#         (size * 2, 0),          # 1 top left
#         (size, -size)           # 2 peak of curve
#     ]
#
#     world_pos = [
#         (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
#         (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
#         (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1])
#     ]
#
#     go_draw(world_pos[1][0], world_pos[1][1], wait=wait)
#     arc2D(world_pos[2][0], world_pos[2][1], world_pos[0][0], world_pos[0][1], wait=wait)
#
#     char.append(world_pos)
#     chars.append(char)
#
# def draw_g(size, wait=True):
#     """Draws the letter G at the pens current position. Seperate from the draw_char() function as it requires an arc.
#     Is called in draw_char() when G is passed as the _char parameter."""
#     pos = device.pose()[:4]
#     char = []
#     char.append("G")
#
#     local_pos = [
#         (0, 0),                  # 0 top right
#         (- size     , size),     # 1 peak of curve
#         (- size * 2 , 0),        # 2 bottom right
#         (-size      , 0),        # 3 mid right
#         (-size      , size / 2)  # 4 center point
#
#     ]
#
#     world_pos = [
#         (pos[0] + local_pos[0][0], pos[1] + local_pos[0][1]),
#         (pos[0] + local_pos[1][0], pos[1] + local_pos[1][1]),
#         (pos[0] + local_pos[2][0], pos[1] + local_pos[2][1]),
#         (pos[0] + local_pos[3][0], pos[1] + local_pos[3][1]),
#         (pos[0] + local_pos[4][0], pos[1] + local_pos[4][1])
#     ]
#
#     arc2D(world_pos[1][0], world_pos[1][1], world_pos[2][0], world_pos[2][1], wait=wait)
#     go_draw(world_pos[3][0], world_pos[3][1], wait=wait)
#     go_draw(world_pos[4][0], world_pos[4][1], wait=wait)
#
#     char.append(world_pos)
#     chars.append(char)
#
# def draw_random_char(size, wait=True):
#     chars = ["A", "B", "C", "D", "E", "F", "G", "P", "Z"]
#
#     rand_char = chars[random.randrange(0, len(chars))]
#
#     draw_char(rand_char, size, wait)
#
# def draw_circle(size, side=0, wait=True):
#     """Draws a circle from the current pen position. 'side' is used to determine which direction the circle is drawn relative
#     to the pen position, allows for creation of figure-8 patterns.The start position, size, and side are saved to the circles list."""
#     pos = device.pose()[:4]
#
#     if(side == 0):  # side is used to draw figure 8 patterns
#         arc(pos[0] + size, pos[1] - size, pos[2], pos[3], pos[0]+ 0.01, pos[1] + 0.01, pos[2], pos[3], wait=wait)
#     elif(side == 1):
#         arc(pos[0] - size, pos[1] + size, pos[2], pos[3], pos[0]+ 0.01, pos[1] + 0.01, pos[2], pos[3], wait=wait)
#
#     circle = []
#     circle.append(pos)
#     circle.append(size)
#     circle.append(side)
#
#     circles.append(circle)
#
# def arc2D(apex_x, apex_y, target_x, target_y, wait=True):
#     """Simplified arc function for drawing 2D arcs on the xy axis. apex_x and y determine
#     the coordinates of the apex of the curve. target_x and y determine the end point of the curve"""
#     pos = device.pose()
#
#     msg = Message()
#     msg.id = 101
#     msg.ctrl = 0x03
#     msg.params = bytearray([])
#     msg.params.extend(bytearray(struct.pack('f', apex_x)))
#     msg.params.extend(bytearray(struct.pack('f', apex_y)))
#     msg.params.extend(bytearray(struct.pack('f', pos[2])))
#     msg.params.extend(bytearray(struct.pack('f', pos[3])))
#     msg.params.extend(bytearray(struct.pack('f', target_x)))
#     msg.params.extend(bytearray(struct.pack('f', target_y)))
#     msg.params.extend(bytearray(struct.pack('f', pos[2])))
#     msg.params.extend(bytearray(struct.pack('f', pos[3])))
#     return device._send_command(msg, wait)
#
# def arc(x, y, z, r, cir_x, cir_y, cir_z, cir_r, wait=False):
#         """Draws an arc defined by a) position at apex of the curve (x, y, z, r),
#         with b) a finishing coordinates (cirx, ciry, cirz, cirr.
#         """
#         msg = Message()
#         msg.id = 101
#         msg.ctrl = 0x03
#         msg.params = bytearray([])
#         msg.params.extend(bytearray(struct.pack('f', x)))
#         msg.params.extend(bytearray(struct.pack('f', y)))
#         msg.params.extend(bytearray(struct.pack('f', z)))
#         msg.params.extend(bytearray(struct.pack('f', r)))
#         msg.params.extend(bytearray(struct.pack('f', cir_x)))
#         msg.params.extend(bytearray(struct.pack('f', cir_y)))
#         msg.params.extend(bytearray(struct.pack('f', cir_z)))
#         msg.params.extend(bytearray(struct.pack('f', cir_r)))
#         return device._send_command(msg, wait)
#
# #-----non-drawing movement behaviour functions-----
# def return_to_square():     # returns to a random pre-existing square and does something
#     """Randomly chooses a square from the 'squares' list and randomly chooses a behaviour to do with it."""
#     square_length = int(len(squares))
#     if(square_length > 0):
#         square = squares[int(random.uniform(0, square_length))]
#         print(square)
#
#         rand = random.uniform(0, 1)
#
#         if(rand == 0):              # move to a random corner on the square and draw a new square with a random size
#             randCorner = random.uniform(0,3)
#             go_draw_up(square[randCorner][0], square[randCorner][1], square[randCorner][2], square[randCorner][3], wait=True)  # go to a random corner of the square (top right = 0, goes anti-clockwise)
#             draw_square(random.uniform(20,29), True)
#         else:                       # draw a cross in the square
#             go_draw_up(square[0][0], square[0][1], square[0][2], square[0][3], wait=True)
#             device.move_to(square[2][0], square[2][1], square[2][2], square[2][3], wait=True)
#             go_draw_up(square[1][0], square[1][1], square[1][2], square[1][3], wait=True)
#             device.move_to(square[3][0], square[3][1], square[3][2], square[3][3], wait=True)
#
#         #device.move_to(square[1][0], square[1][1], square[1][2], square[1][3], wait=True)  #redraw the square from top right corner anti-clockwise
#         #device.move_to(square[2][0], square[2][1], square[2][2], square[2][3], wait=True)
#         #device.move_to(square[3][0], square[3][1], square[3][2], square[3][3], wait=True)
#         #device.move_to(square[0][0], square[0][1], square[0][2], square[0][3], wait=True)
#
#     else:
#         print("cannot return to square, no squares in list")
#
# def return_to_sunburst():
#     """Randomly chooses a sunburst from the 'sunbursts' list and randomly chooses a behaviour to do with it."""
#     sunbursts_length = int(len(sunbursts))
#     if(sunbursts_length > 0):
#         sunburst = sunbursts[int(random.uniform(0, sunbursts_length))]
#         print(sunburst)
#
#         rand = random.uniform(0,1)      #randomly choose between two behaviours
#
#         if(rand == 0):                  #join up the ends of the sunburst lines
#             go_draw_up(sunburst[0][0], sunburst[0][1], sunburst[0][2], sunburst[0][3], wait=True)
#             device.move_to(sunburst[1][0], sunburst[1][1], sunburst[1][2], sunburst[1][3], wait=True)
#             device.move_to(sunburst[2][0], sunburst[2][1], sunburst[2][2], sunburst[2][3], wait=True)
#             device.move_to(sunburst[3][0], sunburst[3][1], sunburst[3][2], sunburst[3][3], wait=True)
#             device.move_to(sunburst[4][0], sunburst[4][1], sunburst[4][2], sunburst[4][3], wait=True)
#         else:                           # go to the end of one of the sunburst lines and draw another sunburst
#             go_draw_up(sunburst[2][0], sunburst[2][1], sunburst[2][2], sunburst[2][3], wait=True)
#             draw_sunburst(20, True)
#
#     else:
#         print("cannot return to sunburst, no sunbursts in list")
#
# def return_to_irregular():
#     """Randomly chooses an irregular shape from the 'irregulars' list and randomly chooses a behaviour to do with it."""
#     irregulars_length = int(len(irregulars))
#     if(irregulars_length > 0):
#         irregular = irregulars[random.randrange(0, irregulars_length)]
#
#         #rand = random.uniform(0,1)     #add random choice of behaviours
#         #if(rand == 0):
#
#         rand_vertex = irregular[random.randrange(0,len(irregular))]
#         go_draw(rand_vertex[0], rand_vertex[1])
#         draw_irregular_shape(random.randrange(3,8))
#
#     else:
#         print("Cannot return to irregular, no irregulars in list")
#
# def return_to_char():
#     """Randomly chooses a character from the 'chars' list and randomly chooses a behaviour to do with it. (NOT FINISHED)"""
#     chars_length = int(len(chars))
#     if(chars_length > 0):
#         char = chars[random.randrange(0, chars_length)]     # pick a char at random, do something with it
#
#     else:
#         print("Cannot return to char, no chars in list")
#
# start_pos = device.pose()    # robot pose when program begins
# print(f'beginning pose= x:{round(start_pos[0], 2)} y:{round(start_pos[1], 2)} z:{round(start_pos[2], 2)} j1:{round(start_pos[4], 2)} j2:{round(start_pos[5], 2)} j3:{round(start_pos[6], 2)} j4:{round(start_pos[7], 2)}')
#
# go_position_ready()
# input("Device at ready positon. Press enter to go to draw position.")
# go_random_draw()
# input("Device at random draw positon. Move pen onto page and press enter to begin drawing.")
#
# for i in range(10):
#     draw_random_char(i * 4)
#     go_random_zigzag()
#
# #for i in range(15):
# #    draw_circle(i + 5, i % 2, wait=True)   #figure 8 circles
#
# running = False
# current_phrase_num = 0  # number of phrases looped through. can be used for something to change behaviour over time...
# joint_inc = 10
#
# while running:
#
#     phrase_length = random.uniform(5, 15)
#     phrase_loop_end = time.time() + phrase_length
#
#     current_mode = RobotMode(random.randrange(5))   # maybe add a check to ensure that the same mode isnt picked twice in a row
#     print("Current phase: ", current_phrase_num, " with length: ", phrase_length, ". Current mode set to: ", current_mode)
#
#     current_phrase_num += 1
#
#     while time.time() < phrase_loop_end:
#
#         if(keyboard.is_pressed("g")):
#             shape_interrupt = True
#             print("interrupt")
#
#         if(current_mode == RobotMode.Continuous):
#             #move continuously using data streams from EMD, borg
#
#             inc = joint_inc * current_phrase_num
#
#             position_move_by(random.uniform(-inc, inc), random.uniform(-inc, inc), draw_position[2], wait=False)
#
#         elif(current_mode == RobotMode.Inspiration):
#             # random shapes inspired by Wolffs "1,2,3 players"
#             #go_random_draw_up()
#             position_move_by(random.uniform(-joint_inc,joint_inc), random.uniform(-joint_inc,joint_inc), random.uniform(-joint_inc,joint_inc), wait=False)
#
#         elif(current_mode == RobotMode.Modification):
#             # random shapes inspired by Cardews "Treatise"
#             go_random_draw_up()
#             draw_sunburst(random.uniform(20,40), True)
#
#             if(random.randrange(0,1) == 1):
#                 return_to_sunburst()
#
#         elif(current_mode == RobotMode.OffPage):
#             # random movements off the page, balletic movements above the page
#             #print("OffPage Mode")
#
#             joint_move_by(random.uniform(-joint_inc,joint_inc), random.uniform(-joint_inc,joint_inc), random.uniform(-joint_inc,joint_inc), wait=False)
#
#         elif(current_mode == RobotMode.Repetition):
#             # large, repetitive movements
#             #print("Repetition Mode")
#
#             draw_square(random.uniform(10,40))                           # draw a square of random size
#             rand_xfactor = random.randrange(-3, 3)
#             rand_yfactor = random.randrange(-3, 3)
#             position_move_by(5 * rand_xfactor, 5 * rand_yfactor, 0, wait=True) # either move in positive, negative or no movement, then loop
#
#             #go_random_position_draw()
#
#
# """factor = 3
# print("movement: wasd e q, speed r f, stop l ")
# while loop:                ## keyboard controls for joints
#     if keyboard.is_pressed("w"):
#         joint_move_by(0,factor,0,0, False)   # up
#     if keyboard.is_pressed("s"):
#         joint_move_by(0,-factor,0,0, False)   #down
#     if keyboard.is_pressed("a"):
#         joint_move_by(factor,0,0,0, False)   # left
#     if keyboard.is_pressed("d"):
#         joint_move_by(-factor,0,0,0, False)  # right
#     if keyboard.is_pressed("e"):
#         joint_move_by(0,0,0,factor, False)  # j3
#     if keyboard.is_pressed("q"):
#         joint_move_by(0,0,0,-factor, False)  # j3
#     if keyboard.is_pressed("r"):
#         factor += 0.1
#         print("factor changed to: ", factor)
#     if keyboard.is_pressed("f"):
#         factor -= 0.1
#         print("factor changed to: ", factor)
#     if keyboard.is_pressed("l"):
#         loop = False"""
#
# go_position_end()
# input("Device at end positon. Press enter to finish.")
#
# device.close()
