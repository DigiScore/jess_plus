# install python modules
import sys
import os
from time import time, sleep
from random import randrange, getrandbits, random, uniform
import logging
from enum import Enum

# import project modules
from nebula.nebula_dataclass import DataBorg
from drawbot import Drawbot
import config

# todo - CRAIGS script


class RobotMode(Enum):
    Continuous = 0
    Modification = 1
    Inspiration = 2
    Repetition = 3
    OffPage = 4


class Affect:
    """Controls movement and shapes drawn by Dobot.
    """

    def __init__(self,
                 duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True,
                 drawbot: Drawbot = None
                 ):
        # super().__init__(port, verbose)

        self.drawbot = drawbot

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

        if self.drawbot:
            print('locating home')
            self.drawbot.home()
            input('remove pen lid, then press enter')

            # # todo CRAIG this should be decided in line with self.awareness
            # arm_speed = (((speed - 1) * (300 - 50)) / (10 - 1)) + 50
            # self.drawbot.speed(velocity=arm_speed,
            #            acceleration=arm_speed)
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

        if self.drawbot:
            print("Started dobot control thread")
            self.drawbot.go_position_draw()

        # names for affect listening
        stream_list = config.stream_list
        stream_list_len = len(stream_list)
        current_phrase_num = 0  # number of phrases looped through. can be used for something to change behaviour over time...
        joint_inc = 10


        while self.running:
            # flag for breaking a phrase from big affect signal
            self.hivemind.interrupt_bang = True

            #############################
            # Phrase-level gesture gate: 3 - 8 seconds
            #############################
            # todo CRAIG calls the robot arm to do different modes
            # todo CRAIG global speed and self-awareness stretch
            # # calc rhythmic intensity based on self-awareness factor & global speed
            # intensity = getattr(self.hivemind, 'self_awareness')
            # logging.debug(f'////////////////////////   intensity =  {intensity}')

            phrase_length = (randrange(300, 800) / 100) # + self.global_speed
            phrase_loop_end = time() + phrase_length

            # define robot mode
            robot_mode = RobotMode(randrange(5))

            logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
            logging.debug(f"                 interrupt_listener: started! Duration =  {phrase_length} seconds")

            while time() < phrase_loop_end:
                print('================')

                # if a major break out then go to Daddy cycle and restart
                if not self.hivemind.interrupt_bang:
                    print("-----------------------------INTERRUPT----------------------------")
                    break

                # 1. clear the alarms
                if self.drawbot:
                    self.drawbot.clear_alarms()
                    if self.continuous_line:
                        self.drawbot.move_y()

                # todo - CRAIG sort this out.!!
                # generate rhythm rate here
                rhythm_rate = (randrange(10,
                                         80) / 100) #* self.global_speed
                self.hivemind.rhythm_rate = rhythm_rate
                logging.info(f'////////////////////////   rhythm rate = {rhythm_rate}')
                logging.debug('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 started ===========')

                ##################################################################
                # choose thought stream from data streams from Nebula/ live inputs
                ##################################################################

                # randomly pick an input stream for this cycle
                # either mic_in, random, net generation or self-awareness
                rnd = randrange(stream_list_len)
                rnd_stream = stream_list[rnd]
                self.hivemind.thought_train_stream = rnd_stream
                logging.info(f'Random stream choice = {rnd_stream}')
                print(self.hivemind.thought_train_stream)

                #############################
                # Rhythm-level gesture gate: .5-2 seconds
                # THis streams the chosen data
                #############################
                # todo CRAIG add global time stretch here (from self awareness)
                # rhythmic loop 0.5-2 (or 1-4) secs, unless interrupt bang
                rhythm_loop = time() + (randrange(500, 2000) / 1000)
                logging.debug(f'end time = {rhythm_loop}')

                while time() < rhythm_loop:
                    logging.debug('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # make the master output the current value of the affect stream
                    # 1. go get the current value from dict
                    thought_train = getattr(self.hivemind, rnd_stream)
                    # thought_train = self.hivemind.rnd_stream
                    logging.info(f'######################           Affect stream output {rnd_stream} == {thought_train}')

                    # 2. send to Master Output
                    # setattr(self.hivemind, 'master_stream', thought_train)
                    self.hivemind.master_stream = thought_train
                    logging.info(f'\t\t ==============  thought_train output = {thought_train}')

                    # 3. modify speed and accel through self awareness
                    # # todo CRAIG this should be decided in line with self.awareness
                    # calc rhythmic intensity based on self-awareness factor & global speed
                    self_awareness = getattr(self.hivemind, 'self_awareness')
                    logging.debug(f'////////////////////////   self_awareness =  {self_awareness}')
                    arm_speed = (((self_awareness - 1) * (300 - 50)) / (10 - 1)) + 50
                    if self.drawbot:
                        self.drawbot.speed(velocity=arm_speed,
                               acceleration=arm_speed)

                    ######################################
                    #
                    # Makes a response to chosen thought stream
                    #
                    ######################################

                    match robot_mode:
                        case RobotMode.Continuous:
                        # move continuously using data streams from EMD, borg

                            inc = joint_inc * current_phrase_num

                            self.drawbot.position_move_by(uniform(-inc, inc),
                                                          uniform(-inc, inc),
                                                          self.drawbot.draw_position[2],
                                             wait=False)

                        case RobotMode.Inspiration:
                            # random shapes inspired by Wolffs "1,2,3 players"
                            # go_random_draw_up()
                            # self.drawbot.position_move_by(uniform(-joint_inc, joint_inc),
                            #                               uniform(-joint_inc, joint_inc),
                            #                               uniform(-joint_inc, joint_inc), wait=False)
                            self.wolff_inspiration(thought_train)

                        case RobotMode.Modification:
                        # random shapes inspired by Cardews "Treatise"
                        # go_random_draw_up()
                        # draw_sunburst(random.uniform(20, 40), True)
                        #
                        # if (random.randrange(0, 1) == 1):
                        #     return_to_sunburst()

                            self.cardew_inspiration(thought_train)

                        case RobotMode.OffPage:
                        # random movements off the page, balletic movements above the page
                        # print("OffPage Mode")

                            self.drawbot.joint_move_by(uniform(-joint_inc, joint_inc),
                                                       uniform(-joint_inc, joint_inc),
                                                       uniform(-joint_inc, joint_inc), wait=False)

                        case RobotMode.Repetition:
                        # large, repetitive movements
                        # print("Repetition Mode")

                            draw_square(random.uniform(10, 40))  # draw a square of random size
                            rand_xfactor = random.randrange(-3, 3)
                            rand_yfactor = random.randrange(-3, 3)
                            position_move_by(5 * rand_xfactor, 5 * rand_yfactor, 0,
                                             wait=True)  # either move in positive, negative or no movement, then loop

                    if thought_train > 0.7:
                        logging.info('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.hivemind.randomiser()

                        # B - jumps out of this loop into daddy
                        self.hivemind.interrupt_bang = False

                        # C - respond
                        if self.drawbot:
                            self.high_energy_response()

                        # D- break out of this loop, and next (cos of flag)
                        break

                    # MEDIUM
                    # if middle loud fill dict with random, all processes norm
                    elif 0.1 < thought_train < 0.7:
                        logging.info('interrupt MIDDLE -----------')

                        if self.drawbot:
                            self.mid_energy_response(thought_train)

                        # A. jumps out of current local loop, but not main one
                        # break

                    # LOW
                    # nothing happens here
                    elif thought_train <= 0.1:
                        logging.info('interrupt LOW ----------- move Y')

                        if self.drawbot:
                            if self.continuous_line:
                                self.drawbot.move_y()

                    # and wait for a cycle
                    sleep(rhythm_rate)

        logging.info('quitting dobot director thread')

    def wolff_inspiration(self, peak):
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



    def cardew_inspiration(self, peak):
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
