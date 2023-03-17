# install python modules
from time import time, sleep
from random import random, randrange, getrandbits, uniform
import logging
from enum import Enum
from serial.tools import list_ports
import platform
from threading import Thread

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
                 port: str,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 0,
                 ):

        # PLATFORM = platform.system()
        ROBOT_CONNECTED = config.robot

        ############################
        # Robot
        ############################
        # start dobot communications
        # may need sudo chmod 666 /dev/ttyACM0
        if ROBOT_CONNECTED:
            # # find available ports and locate Dobot (-1)
            # available_ports = list_ports.comports()
            # print(f'available ports: {[x.device for x in available_ports]}')
            # if PLATFORM == "darwin":
            #     port = available_ports[-1].device
            # elif PLATFORM == "Windows":
            #     port = available_ports[0].device
            # elif PLATFORM == "Linux":
            #     port = available_ports[-1].device
            # else:
            #     port = None

            self.drawbot = Drawbot(
                port=port,
                verbose=False,
                continuous_line=continuous_line
            )
        else:
            self.drawbot = None

        # own the dataclass
        self.hivemind = DataBorg()

        # start operating vars
        self.continuous_line = continuous_line
        self.current_phrase_num = 0  # number of phrases looped through. can be used for something to change behaviour over time...
        self.joint_inc = 10

        # calculate the inverse of speed
        # NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
        self.global_speed = speed # ((speed - 1) * (0.1 - 1) / (10 - 1)) + 1
        # print(f'user def speed = {speed}, global speed = {self.global_speed}')

        if self.drawbot:
            print('locating home')
            self.drawbot.home()
            input('remove pen lid, then press enter')

            self.drawbot.draw_stave(staves=staves)
            self.drawbot.go_position_ready()

    def main_loop(self):
        robot_thread = Thread(target=self.gesture_manager)
        robot_thread.start()

    def gesture_manager(self):
        """
        Listens to the realtime incoming signal and calculates
        an affectual response based on general boundaries:
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

        while self.hivemind.running:
            # flag for breaking a phrase from big affect signal
            self.hivemind.interrupt_bang = True

            #############################
            # Phrase-level gesture gate: 3 - 8 seconds
            #############################

            phrase_length = (randrange(300, 800) / 100) # + self.global_speed
            phrase_loop_end = time() + phrase_length

            logging.debug('\t\t\t\t\t\t\t\t=========AFFECT - Daddy cycle started ===========')
            logging.debug(f"                 interrupt_listener: started! Duration =  {phrase_length} seconds")

            # define robot mode for this phase length
            # robot_mode = RobotMode(randrange(5))
            robot_mode = randrange(10)

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

                # speed for this phrase
                # arm_speed = (((self_awareness - 1) * (300 - 50)) / (10 - 1)) + 50
                arm_speed = randrange(30, 500)
                if self.drawbot:
                    self.drawbot.speed(velocity=arm_speed,
                                       acceleration=arm_speed)

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

                    ######################################
                    #
                    # Makes a response to chosen thought stream
                    #
                    ######################################

                    # todo - can this be farmed off as an emission to a seperate thread? Need to be careful with over-run/ repeats of "HIGH"

                    if thought_train > 0.8 or not self.hivemind.interrupt_bang:
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
                    elif thought_train <= 0.2:
                        logging.info('interrupt LOW ----------- move Y')

                        if self.drawbot:
                            # if self.continuous_line:
                            self.drawbot.move_y()

                    else:
                        # MID response
                        if self.drawbot:
                            match robot_mode:
                                case 1:
                                    # move continuously using data streams from EMD, borg
                                    print("Continuous Mode")
                                    # self.continuous(thought_train)
                                    self.offpage(thought_train)

                                case 2:
                                    # random shapes inspired by Wolff's 1, 2, 3
                                    print("Inspiration/ Wollf Mode")
                                    self.wolff_inspiration(thought_train)

                                case 3:
                                    # random shapes inspired by Cardews "Treatise"
                                    print("Modification/ Cardew Mode")
                                    self.cardew_inspiration(thought_train)

                                case 4:
                                    # random movements off the page, balletic movements above the page
                                    print("OffPage Mode")
                                    self.offpage(thought_train)

                                case 5:
                                    # large, repetitive movements
                                    print("Repetition Mode")
                                    self.repetition(thought_train)

                                case 6:
                                    # random shapes inspired by Wolff's 1, 2, 3
                                    print("Inspiration/ Wollf Mode")
                                    self.wolff_inspiration(thought_train)

                                case 7:
                                    # random shapes inspired by Wolff's 1, 2, 3
                                    print("Inspiration/ Wollf Mode")
                                    self.wolff_inspiration(thought_train)

                                case 8:
                                    # random shapes inspired by Cardews "Treatise"
                                    print("Modification/ Cardew Mode")
                                    self.cardew_inspiration(thought_train)

                                case 9:
                                    # random shapes inspired by Cardews "Treatise"
                                    print("Modification/ Cardew Mode")
                                    self.cardew_inspiration(thought_train)

                    # and wait for a cycle
                sleep(rhythm_rate)

        logging.info('quitting dobot director thread')
        self.terminate()

    def repetition(self, peak):
        self.drawbot.go_random_draw_up()
        self.drawbot.create_shape_group()  # create a new shape group
        for i in range(randrange(1, 2)):  # repeat the shape group a random number of times
            logging.debug("repetition of shape")
            self.drawbot.repeat_shape_group()

    def offpage(self, peak):
        move_var = (peak * 10) * self.joint_inc
        self.drawbot.position_move_by(
            uniform(-move_var, move_var),
            uniform(-move_var, move_var),
            uniform(-move_var, move_var),
            wait=False
        )
    def continuous(self, peak):
        # todo - make this a or b. A = pulls data from a file (extracts from dataset). B = live from Hivemind
        inc = self.joint_inc * self.current_phrase_num

        if random() > 0.5:  # use mic input - probably want to change this so x, y, z aren't all the same
            self.drawbot.position_move_by(self.hivemind.mic_in,
                                          self.hivemind.mic_in,
                                          self.hivemind.mic_in,
                                          wait=False)

        else:  # todo - use EMD data. Currently uses random data
            self.drawbot.position_move_by(uniform(-inc, inc),
                                          uniform(-inc, inc),
                                          self.drawbot.draw_position[2],
                                          wait=False)

    def wolff_inspiration(self, peak):
        """
        jumps to a random spot and makes a mark inspired by Wolff
        """
        # get the current position
        (x, y, z, r, j1, j2, j3, j4) = self.drawbot.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # jump to a random location
        self.drawbot.go_random_draw_up()
        # self.drawbot.move_y_random()

        # randomly choose from the following choices
        randchoice = randrange(7)
        logging.debug(f'randchoice WOLFF == {randchoice}')

        match randchoice:
            case 0:
                logging.info('Wolff: draw line')
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)

            case 1:
                logging.info('Wolff: random character')
                self.drawbot.draw_random_char(peak * randrange(10, 20))

            case 2:
                logging.info('Wolff: dot and line')
                self.drawbot.dot()
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)

            case 3:
                logging.info('Wolff: note head')
                note_size = randrange(1, 10)
                # note_shape = randrange(20)
                self.drawbot.note_head(size=note_size)

            case 4:
                logging.info('Wolff: note head and line')
                note_size = randrange(1, 10)
                self.drawbot.note_head(size=note_size)
                self.drawbot.bot_move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z, 0,
                                     False)

            case 5:
                logging.info('Wolff: dot')
                self.drawbot.dot()

            case 6:
                logging.info('Wolff: random character')
                self.drawbot.draw_random_char(peak)

    def cardew_inspiration(self, peak):
        """
        randomly chooses a shape inspired by Cardew
        """
        (x, y, z, r, j1, j2, j3, j4) = self.drawbot.pose()
        logging.debug(f'Current position: x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

        # move Y along
        self.drawbot.move_y()

        # randomly choose from the following choices
        randchoice = randrange(6)
        logging.debug(f'randchoice CARDEW == {randchoice}')

        match randchoice:
            case 0:
                logging.info('Cardew: draw arc')
                # range = peak * 10
                self.drawbot.arc2D(x + randrange(-10, 10),
                                   y + randrange(-10, 10),
                                   x + randrange(-10, 10),
                                   y + randrange(-10, 10),
                                   )

            case 1:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for n in range(randrange(3, 9)):
                    squiggle_list.append((randrange(-5, 5),
                                          randrange(-5, 5),
                                          randrange(-5, 5))
                                         )
                self.drawbot.squiggle(squiggle_list)

            case 2:
                logging.info('Cardew: draw circle')
                self.drawbot.draw_circle(int(peak * 10))

            case 3:
                logging.info('Cardew: line')
                self.drawbot.go_draw(x + self.rnd(peak * 10),
                                     y + self.rnd(peak * 10))

            case 4:
                logging.info('Cardew: return to coord')
                self.drawbot.return_to_coord()

            case 5:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for n in range(randrange(3, 9)):
                    squiggle_list.append((randrange(-5, 5),
                                          randrange(-5, 5),
                                          randrange(-5, 5))
                                         )
                self.drawbot.squiggle(squiggle_list)

    def high_energy_response(self):
        """
        move to a random x, y position
        """
        self.drawbot.clear_commands()
        self.drawbot.return_to_coord()

    def terminate(self):
        """
        Smart collapse of all threads and comms
        """
        print('TERMINATING')
        self.drawbot.home()
        self.drawbot.close()

    def rnd(self, power_of_command: int) -> int:
        """
        Returns a randomly generated + or - integer,
        influenced by the incoming power factor
        """
        power_of_command = int(power_of_command)
        if power_of_command <= 0:
            power_of_command = 1
        pos = 1
        if getrandbits(1):
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result
