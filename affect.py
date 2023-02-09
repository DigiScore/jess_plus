# install python modules
import sys
import os
import struct
from time import time, sleep
# from serial.tools import list_ports
from random import randrange, getrandbits, random
import logging
from dataclasses import fields

# install dobot modules
from pydobot import Dobot
from pydobot.enums import PTPMode
from pydobot.message import Message
from pydobot.enums.ControlValues import ControlValues
from pydobot.enums.CommunicationProtocolIDs import CommunicationProtocolIDs

# import project modules
from nebula.nebula_dataclass import DataBorg #NebulaDataClass
from drawbot import Drawbot
import config


# todo - CRAIGS script

class Affect:
    """Controls movement and shapes drawn by Dobot.
    """

    def __init__(self, port,
                 verbose: bool = False,
                 duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True,
                 ):
        # super().__init__(port, verbose)

        self.drawbot = Drawbot(port,
                               verbose,
                               duration_of_piece,
                               continuous_line)

        # set global path
        sys.path.insert(0, os.path.abspath('.'))

        # own the dataclass
        self.hivemind = DataBorg()

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

        # # make a shared list/ dict
        # self.ready_position = [250, -175, 20, 0]
        # self.draw_position = [250, -175, 0, 0]
        # self.end_position = (250, 175, 20, 0)

        # self.start_time = time()

        print('locating home')
        self.drawbot.home()
        input('remove pen, then press enter')

        # todo - this should be decided in line with self.awareness
        arm_speed = (((speed - 1) * (300 - 50)) / (10 - 1)) + 50
        self.drawbot.speed(velocity=arm_speed,
                   acceleration=arm_speed)
        self.drawbot.draw_stave(staves=staves)
        self.drawbot.go_position_ready()


    ######################
    # DRAWBOT CONTROLS
    ######################
    """Mid level functions for operating the drawing and moving 
    functions of the Dobot"""

    def gesture_manager(self):
        """Listens to the realtime incoming signal that is stored in the dataclass ("mic_in")
        and calculates an affectual response based on general boundaries:
            HIGH - if input stream is LOUD (0.8+) then emit, smash a random fill and break out to Daddy cycle...
            MEDIUM - if input energy is 0.3-0.8 then emit, a jump out of child loop
            LOW - nothing happens, continues with cycles
        """

        print("Started dobot control thread")
        self.drawbot.go_position_draw()

        # names for affect listening
        stream_list = config.stream_list
        stream_list_len = len(stream_list)

        while self.running:
            # flag for breaking a phrase from big affect signal
            self.interrupt_bang = True

            #############################
            # Phrase-level gesture gate: 3 - 8 seconds
            #############################
            # todo - calls the robot arm to do different modes
            # todo - global speed and self-awareness stretch
            # calc rhythmic intensity based on self-awareness factor & global speed
            intensity = getattr(self.hivemind, 'self_awareness')
            logging.debug(f'////////////////////////   intensity =  {intensity}')

            phrase_length = (randrange(300, 800) / 100) # + self.global_speed
            phrase_loop_end = time() + phrase_length

            logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
            logging.debug(f"                 interrupt_listener: started! Duration =  {phrase_length} seconds")

            while time() < phrase_loop_end:
                print('================')

                # if a major break out then go to Daddy cycle and restart
                if not self.interrupt_bang:
                    break

                # todo add global time stretch here (from self awareness)
                # hold this stream for 0.5-2 (or 1-4) secs, unless interrupt bang
                end_time = time() + (randrange(500, 2000) / 1000)
                logging.debug(f'end time = {end_time}')

                # 1. clear the alarms
                self.drawbot.clear_alarms()
                if self.continuous_line:
                    self.drawbot.move_y()

                # todo - CRAIG sort this out.!!
                # generate rhythm rate here
                rhythm_rate = (randrange(10,
                                         80) / 100) * self.global_speed
                self.hivemin.rhythm_rate = rhythm_rate
                logging.info(f'////////////////////////   rhythm rate = {rhythm_rate}')

                logging.debug('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')


                ##################################################################
                # choose thought stream from data streams from Nebula/ live inputs
                ##################################################################

                # randomly pick an input stream for this cycle
                # either mic_in, random, net generation or self-awareness
                rnd = randrange(stream_list_len)
                rnd_stream = stream_list[rnd]
                # setattr(self.hivemind, 'affect_decision', self.rnd_stream)
                self.hivemind.affect_decision = self.rnd_stream
                logging.info(f'Random stream choice = {self.rnd_stream}')

                #todo - conduct the NNets prediction here to avoid clogging up the CPU

                #############################
                # Rhythm-level gesture gate: 3 - 8 seconds
                # THis streams the chosen data
                #############################

                # 3. baby cycle - own time loops
                while time() < end_time:
                    logging.debug('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # make the master output the current value of the affect stream
                    # 1. go get the current value from dict
                    thought_train = getattr(self.hivemind, self.rnd_stream)
                    # thought_train = self.hivemind.rnd_stream
                    logging.info(f'Affect stream current input value from {self.rnd_stream} == {thought_train}')

                    # 2. send to Master Output
                    setattr(self.hivemind, 'master_output', thought_train)
                    # self.hivemind.master_output = thought_train
                    logging.info(f'\t\t ==============  thought_train output = {thought_train}')
                    # todo - CRAIG is this doing anything? shouldn't "peak" be the output from the thought train
                    # todo - CRAIG split this function ... mic listener CAN infuence looping behaviour, BUT "peak" should be thought streams


                    # # 3. emit to the client at various points in the affect cycle
                    # self.emitter(thought_train)

                    ###############################################
                    #
                    # test realtime input against the affect matrix
                    # behave as required
                    #
                    ###############################################

                    # 1. get current mic level
                    peak = getattr(self.hivemind, "mic_in")
                    # peak = self.hivemind.mic_in
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
                    # todo - this is why its not doing anythong BROOKS !!!
                    elif peak <= 0.1:
                        logging.info('interrupt LOW ----------- move Y')

                        if self.continuous_line:
                            self.drawbot.move_y()

                    # and wait for a cycle
                    sleep(rhythm_rate)

        logging.info('quitting dobot director thread')

    def mid_energy_response(self, peak):
        (x, y, z, r, j1, j2, j3, j4) = self.drawbot.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        """between 2 and 8 make shapes in situ"""
        # randomly choose from the following c hoices
        randchoice = randrange(6)
        logging.debug(f'randchoice == {randchoice}')

        # 0= line to somewhere
        if randchoice == 0:
            self.drawbot.bot_move_to(x + self.rnd(peak),
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
            self.drawbot.squiggle(squiggle_list)
            logging.info('Emission 3-8: small squiggle')

        # 2 = dot & line
        elif randchoice == 2:
            self.drawbot.dot()
            self.drawbot.bot_move_to(x + self.rnd(peak),
                                 y + self.rnd(peak),
                                 z, 0,
                                 False)
            logging.info('Emission 3-8: dot')

        # 3 = note head
        elif randchoice == 3:
            note_size = randrange(5)
            # note_shape = randrange(20)
            self.drawbot.note_head(size=note_size)
            logging.info('Emission 3-8: note head')

        # 4 = note head and line
        elif randchoice == 4:
            note_size = randrange(1, 10)
            self.drawbot.note_head(size=note_size)
            self.drawbot.bot_move_to(x + self.rnd(peak),
                                 y + self.rnd(peak),
                                 z, 0,
                                 False)
            logging.info('Emission 3-8: note head and line')

        # 5 = dot
        elif randchoice == 5:
            self.drawbot.dot()
            # self.move_y_random()
            logging.info('Emission 3-8: dot and line')

    def high_energy_response(self):
        """move to a random x, y position"""
        self.drawbot.clear_commands()
        self.drawbot.move_y_random()

    def random_dict_fill(self):
        """Fills the working dataclass with random values. Generally called when
        affect energy is highest"""
        # print(self.hivemind.__dict__)
        for key, value in self.hivemind.__dict__.items():
            # print("old field", field)
            rnd = random()
            setattr(self.hivemind, key, rnd)
            # field = rnd
            # print("new field", field)
        # self.hivemind.randomiser()
        logging.debug(f'Data dict new random values are = {self.hivemind}')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.drawbot.home()
        self.drawbot.close()
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
