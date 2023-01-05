# install python modules
import sys
import os
import struct
from time import time, sleep
from serial.tools import list_ports
from random import randrange, getrandbits, random
import logging
from dataclasses import fields


# install dobot modules
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs

# install Nebula modules
from nebula.nebula_dataclass import NebulaDataClass

class Digibot(Dobot):
    """Controls movement and shapes drawn by Dobot.
    Inherets all the functions of Pydobot, and chances a few"""

    def __init__(self, port,
                 datadict: NebulaDataClass,
                 verbose: bool = False,
                 duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True,
                 ):
        super().__init__(port, verbose)

        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # own the dataclass
        self.datadict = datadict

        # start operating vars
        self.duration_of_piece = duration_of_piece
        self.continuous_line = continuous_line
        self.running = True
        self.old_value = 0
        self.local_start_time = time()
        # self.end_time = self.start_time + duration_of_piece
        self.pen = pen

        # calculate the inverse of speed
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        self.global_speed = ((speed - 1) * (0.1 - 1) / (10 - 1)) + 1
        print(f'user def speed = {speed}, global speed = {self.global_speed}')

        # # find available ports and locate Dobot (-1)
        # available_ports = list_ports.comports()
        # print(f'available ports: {[x.device for x in available_ports]}')
        # port = available_ports[-1].device

        # make a shared list/ dict
        self.ready_position = [250, -175, 20, 0]
        self.draw_position = [250, -175, 0, 0]
        self.end_position = (250, 175, 20, 0)

        # self.start_time = time()

        print('locating home')
        self.home()
        input('remove pen, then press enter')

        arm_speed = (((speed - 1) * (300 - 50)) / (10 - 1)) + 50
        self.speed(velocity=arm_speed,
                   acceleration=arm_speed)
        self.draw_stave(staves=staves)
        self.go_position_ready()


    ######################
    # DRAWBOT CONTROLS
    ######################
    """Mid level functions for operating the drawing and moving 
    functions of the Dobot"""

    def drawbot_control(self):
        """Listens to the realtime incoming signal that is stored in the dataclass ("user_input")
        and calculates an affectual response based on general boundaries:
            HIGH - if input stream is LOUD (0.8+) then emit, smash a random fill and break out to Daddy cycle...
            MEDIUM - if input energy is 0.3-0.8 then emit, a jump out of child loop
            LOW - nothing happens, continues with cycles
        """

        print("Started dobot control thread")
        self.go_position_draw()

        # names for affect listening
        self.affectnames = ['user_in',
                            'rnd_poetry',
                            'affect_net',
                            'self_awareness']

        # 1. daddy cycle: top level cycle lasting 6-26 seconds
        while self.running:
            # flag for breaking on big affect signal
            self.interrupt_bang = True

            # Top level calc master cycle before a change
            master_cycle = (randrange(600, 2600) / 100) # + self.global_speed
            loop_end = time() + master_cycle

            logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
            logging.debug(f"                 interrupt_listener: started! Duration =  {master_cycle} seconds")

            # 2. child cycle: waiting for interrupt  from master clock
            while time() < loop_end:
                # if a major break out then go to Daddy cycle and restart
                if not self.interrupt_bang:
                    break

                print('================')

                # 1. clear the alarms
                self.clear_alarms()
                self.move_y()

                # calc rhythmic intensity based on self-awareness factor & global speed
                intensity = getattr(self.datadict, 'self_awareness')
                logging.debug(f'////////////////////////   intensity =  {intensity}')

                rhythm_rate = (randrange(10,
                                         80) / 100) * self.global_speed
                # self.datadict['rhythm_rate'] = rhythm_rate
                setattr(self.datadict, 'rhythm_rate', rhythm_rate)
                logging.info(f'////////////////////////   rhythm rate = {rhythm_rate}')

                logging.debug('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')

                # randomly pick an input stream for this cycle
                # either user_in, random, net generation or self-awareness
                rnd = randrange(4)
                self.rnd_stream = self.affectnames[rnd]
                setattr(self.datadict, 'affect_decision', self.rnd_stream)
                logging.info(f'Random stream choice = {self.rnd_stream}')

                # hold this stream for 1-4 secs, unless interrupt bang
                end_time = time() + (randrange(1000, 4000) / 1000)
                logging.debug(f'end time = {end_time}')

                # 3. baby cycle - own time loops
                while time() < end_time:
                    logging.debug('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # make the master output the current value of the affect stream
                    # 1. go get the current value from dict
                    thought_train = getattr(self.datadict, self.rnd_stream)
                    logging.info(f'Affect stream current input value from {self.rnd_stream} == {thought_train}')

                    # 2. send to Master Output
                    setattr(self.datadict, 'master_output', thought_train)
                    logging.info(f'\t\t ==============  thought_train output = {thought_train}')

                    # # 3. emit to the client at various points in the affect cycle
                    # self.emitter(thought_train)

                    ###############################################
                    #
                    # test realtime input against the affect matrix
                    # behave as required
                    #
                    ###############################################

                    # 1. get current mic level
                    peak = getattr(self.datadict, "user_in")
                    peak_int = int(peak * 10) + 1
                    logging.info(f'testing current mic level for affect = {peak}, rounded to {peak_int}')

                    # 2. calc affect on behaviour
                    # LOUD
                    # if input stream is LOUD then smash a random fill and break out to Daddy cycle...
                    if peak > 0.7:
                        logging.info('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.random_dict_fill()

                        # B - jumps out of this loop into daddy
                        self.interrupt_bang = False

                        # C - respond
                        self.high_energy_response()

                        # D- break out of this loop, and next (cos of flag)
                        break

                    # MEDIUM
                    # if middle loud fill dict with random, all processes norm
                    elif 0.1 < peak < 0.7:
                        logging.info('interrupt MIDDLE -----------')

                        self.mid_energy_response(peak_int)

                        # A. jumps out of current local loop, but not main one
                        # break

                    # LOW
                    # nothing happens here
                    elif peak <= 0.1:
                        logging.info('interrupt LOW ----------- move Y')

                        self.move_y()

                    # and wait for a cycle
                    sleep(rhythm_rate)

        logging.info('quitting dobot director thread')

    # def level_2_cycle(self):
    #

    def mid_energy_response(self, peak):
        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        """between 2 and 8 make shapes in situ"""
        # randomly choose from the following c hoices
        randchoice = randrange(6)
        logging.debug(f'randchoice == {randchoice}')

        # 0= line to somewhere
        if randchoice == 0:
            self.move_to(x + self.rnd(peak),
                                 y + self.rnd(peak),
                                 z, 0,
                                 False)
            logging.info('Emission 3-8: draw line')

        # 1 = messy squiggles
        if randchoice == 1:
            squiggle_list = []
            for n in range(randrange(2, 4)):
                squiggle_list.append((randrange(-5, 5) / 5,
                                      randrange(-5, 5) / 5,
                                      randrange(-5, 5) / 5)
                                     )
            self.squiggle(squiggle_list)
            logging.info('Emission 3-8: small squiggle')

        # 2 = dot & line
        elif randchoice == 2:
            self.dot()
            self.move_to(x + self.rnd(peak),
                                 y + self.rnd(peak),
                                 z, 0,
                                 False)
            logging.info('Emission 3-8: dot')

        # 3 = note head
        elif randchoice == 3:
            note_size = randrange(5)
            # note_shape = randrange(20)
            self.note_head(size=note_size)
            logging.info('Emission 3-8: note head')

        # 4 = note head and line
        elif randchoice == 4:
            note_size = randrange(1, 10)
            self.note_head(size=note_size)
            self.move_to(x + self.rnd(peak),
                                 y + self.rnd(peak),
                                 z, 0,
                                 False)
            logging.info('Emission 3-8: note head and line')

        # 5 = dot
        elif randchoice == 5:
            self.dot()
            # self.move_y_random()
            logging.info('Emission 3-8: dot and line')

    def high_energy_response(self):
        """move to a random x, y position"""
        self._set_queued_cmd_clear()
        self.move_y_random()

    def random_dict_fill(self):
        """Fills the working dataclass with random values. Generally called when
        affect energy is highest"""
        for field in fields(self.datadict):
            # print(field.name)
            rnd = random()
            setattr(self.datadict, field.name, rnd)
        logging.debug(f'Data dict new random values are = {self.datadict}')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.home()
        self.close()
        self.running = False

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
        elapsed = time() - self.local_start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = (((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        if x <= 200 or x >= 300:
            x = 250

        # move z (pen head) a little
        if self.pen:
            if getrandbits(1):
                z = 0
            else:
                z = randrange(-1, 1)

        # which mode
        if self.continuous_line:
            self.move_to(x, newy, z, r, True)
        else:
            self.jump_to(x, newy, z, r, True)

        logging.info(f'Move Y to x:{round(x)} y:{round(newy)} z:{round(z)}')

    def move_y_random(self):
        """Moves x and y pen position to nearly the true Y point."""
        # How far into the piece
        elapsed = time() - self.local_start_time

        # get current y-value
        (x, y, z, r, j1, j2, j3, j4) = self.pose()
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        newy = ((((elapsed - 0) * (175 - -175)) / (self.duration_of_piece - 0)) + -175) + self.rnd(100)
        logging.debug(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # check x-axis is in range
        newx = x + self.rnd(100)
        if newx <= 200 or newx >= 300:
            newx = 250

        # # which mode
        # if self.continuous_line:
        #     self.move_to(newx, newy, 0, r, True)
        # else:
        self.jump_to(newx, newy, 0, r, True)


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


if __name__ == "__main__":
    # # find available ports and locate Dobot (-1)
    available_ports = list_ports.comports()
    print(f'available ports: {[x.device for x in available_ports]}')
    port = available_ports[-1].device
    digibot = Digibot(port=port, verbose=False)

    # print('drawing stave')
    # digibot.draw_stave()

    (x, y, z, r, j1, j2, j3, j4) = digibot.pose()
    print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')


    digibot.arc(x + 5, y, z, r, x + 0, y + 0, z, r)

    # digibot.squiggle([(5, 5, 5)])
    #
    # digibot.dot()
    #
    # digibot.close()
