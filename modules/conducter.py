# install python modules
from time import time, sleep
from random import randrange, getrandbits, uniform
import logging
from enum import Enum
from serial.tools import list_ports
import platform

# import project modules
from nebula.hivemind import DataBorg
from modules.drawbot import Drawbot
import config

class RobotMode(Enum):
    Continuous = 0
    Modification = 1
    Inspiration = 2
    Repetition = 3
    OffPage = 4

class Conducter:
    """
    Controls movement and shapes drawn by Dobot.
    """

    def __init__(self,
                 duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True,
                 # drawbot: Drawbot = None
                 ):

        PLATFORM = platform.system()
        ROBOT_CONNECTED = config.robot

        ############################
        # Robot
        ############################
        # start dobot communications
        # may need sudo chmod 666 /dev/ttyACM0
        if ROBOT_CONNECTED:

            # find available ports and locate Dobot (-1)
            available_ports = list_ports.comports()
            print(f'available ports: {[x.device for x in available_ports]}')
            if PLATFORM == "darwin":
                port = available_ports[-1].device
            elif PLATFORM == "Windows":
                port = available_ports[0].device
            elif PLATFORM == "Linux":
                port = available_ports[-1].device

            self.drawbot = Drawbot(port=port,
                              verbose=False,
                              duration_of_piece=duration_of_piece,
                              continuous_line=continuous_line
                              )
        else:
            self.drawbot = None

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

            self.drawbot.draw_stave(staves=staves)
            self.drawbot.go_position_ready()


    ######################
    # DRAWBOT CONTROLS
    ######################
    """
    Mid level functions for operating the drawing and moving 
    functions of the Dobot
    """

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

            logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
            logging.debug(f"                 interrupt_listener: started! Duration =  {phrase_length} seconds")

            # define robot mode for this phase length
            robot_mode = RobotMode(randrange(5))

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
                    if thought_train > 0.8:
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

                        # LOW
                    elif thought_train <= 0.1:
                        logging.info('interrupt LOW ----------- move Y')

                        if self.drawbot:
                            if self.continuous_line:
                                self.drawbot.move_y()
                            else:
                                # random shapes inspired by Wolffs "1,2,3 players"
                                self.drawbot.go_random_draw_up()
                                self.drawbot.position_move_by(uniform(-joint_inc, joint_inc),
                                                              uniform(-joint_inc, joint_inc),
                                                              uniform(-joint_inc, joint_inc), wait=False)
                    # MID response
                    match robot_mode:
                        case RobotMode.Continuous:
                        # move continuously using data streams from EMD, borg

                        # todo - make this a or b. A = pulls data from a file (extracts from dataset). B = live from Hivemind
                            inc = joint_inc * current_phrase_num

                            self.drawbot.position_move_by(uniform(-inc, inc),
                                                          uniform(-inc, inc),
                                                          self.drawbot.draw_position[2],
                                             wait=False)

                        case RobotMode.Inspiration:
                            self.wolff_inspiration(thought_train)

                        case RobotMode.Modification:
                        # random shapes inspired by Cardews "Treatise"
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
                            #
                            #     draw_square(random.uniform(10, 40))  # draw a square of random size
                            #     rand_xfactor = random.randrange(-3, 3)
                            #     rand_yfactor = random.randrange(-3, 3)
                            #     position_move_by(5 * rand_xfactor, 5 * rand_yfactor, 0,
                            #                      wait=True)  # either move in positive, negative or no movement, then loop
                            pass
                            # todo - Adam to sort as discussed

                    # and wait for a cycle
                sleep(rhythm_rate)

        logging.info('quitting dobot director thread')

    def wolff_inspiration(self, peak):
        """
        jumps to a random spot and makes a mark inspired by Wolff
        """
        # get the current position
        (x, y, z, r, j1, j2, j3, j4) = self.drawbot.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # jump to a random location
        self.drawbot.go_random_draw_up()

        # randomly choose from the following choices
        randchoice = randrange(6)
        logging.debug(f'randchoice == {randchoice}')

        match randchoice:
            case 0:
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)
                logging.info('Emission: draw line')

            case 1:
                self.drawbot.draw_random_char(peak * randrange(10, 20))
                logging.info('Emission: random character')

            case 2:
                self.drawbot.dot()
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)
                logging.info('Emission: dot and line')

            case 3:
                note_size = randrange(1, 10)
                # note_shape = randrange(20)
                self.drawbot.note_head(size=note_size)
                logging.info('Emission: note head')

            case 4:
                note_size = randrange(1, 10)
                self.drawbot.note_head(size=note_size)
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)
                logging.info('Emission 3-8: note head and line')

            case 5:
                self.drawbot.dot()
                # self.move_y_random()
                logging.info('Emission: dot')

    def cardew_inspiration(self, peak):
        """
        randomly chooses a shape inspired by Cardew
        """
        (x, y, z, r, j1, j2, j3, j4) = self.drawbot.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # randomly choose from the following choices
        randchoice = randrange(6)
        logging.debug(f'randchoice == {randchoice}')

        match randchoice:
            case 0:
                self.drawbot.arc2D(x + randrange(-10, 10),
                                   y + randrange(-10, 10),
                                   x + randrange(-10, 10),
                                   y + randrange(-10, 10),
                                   )
                logging.info('Emission: draw arc')

            case 1:
                squiggle_list = []
                for n in range(randrange(3, 6)):
                    squiggle_list.append((randrange(-5, 5) / 5,
                                          randrange(-5, 5) / 5,
                                          randrange(-5, 5) / 5)
                                         )
                self.drawbot.squiggle(squiggle_list)
                logging.info('Emission: small squiggle')

            case 2:
                self.drawbot.draw_irregular_shape(int(peak * 10))
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)
                logging.info('Emission: irregular shape')

            case 3:
                # note_size = randrange(5)
                # # note_shape = randrange(20)
                # self.drawbot.note_head(size=note_size)
                # todo - Adam - new func
                # self.drawbot.return_to_random()
                logging.info('Emission: random shape')

            case 4:
                self.drawbot.go_draw(x + self.rnd(peak * 10),
                                     y + self.rnd(peak * 10))
                logging.info('Emission: line')

            case 5:
                self.drawbot.position_move_by(self.rnd(peak * 10),
                                              self.rnd(peak * 10),
                                              randrange(peak) * 10)
                logging.info('Emission: z dance')

    def high_energy_response(self):
        """
        move to a random x, y position
        """
        self.drawbot.clear_commands()
        self.drawbot.move_y_random()

    def terminate(self):
        """
        Smart collapse of all threads and comms
        """
        print('TERMINATING')
        self.drawbot.home()
        self.drawbot.close()
        self.running = False

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
