# install python modules
from time import sleep, time
from random import getrandbits, random, randrange, uniform
import logging
from enum import Enum
from threading import Thread

# import project modules
from nebula.hivemind import DataBorg
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
                 speed: int = 5,
                 ):

        # PLATFORM = platform.system()
        self.DOBOT_CONNECTED = config.dobot_connected
        verbose = config.dobot_verbose

        self.XARM_CONNECTED = config.xarm_connected

        ############################
        # Robot
        ############################
        # start dobot communications
        # may need sudo chmod 666 /dev/ttyACM0
        if self.DOBOT_CONNECTED:
            from modules.drawDobot import Drawbot

            port = config.dobot1_port
            self.drawbot = Drawbot(
                port=port,
                verbose=verbose,
            )
        elif self.XARM_CONNECTED:
            from modules.drawXarm import DrawXarm
            port = config.xarm1_port
            self.drawbot = DrawXarm(port)

        else:
            self.drawbot = None

        # own the dataclass
        self.hivemind = DataBorg()

        # start operating vars
        self.current_phrase_num = 0  # number of phrases looped through. can be used for something to change behaviour over time...
        self.joint_inc = 10          # scaling factor for incremental movement
        self.continuous_mode = 0     # mode for continuous module. 0 == on page, 1 == above page
        self.continuous_source = 0   # source of data used for continous movement. 0 == random, 1 == NN, 2 == peak

        # calculate the inverse of speed (NOT IMPLEMENTED)
        self.global_speed = speed   # ((speed - 1) * (0.1 - 1) / (10 - 1)) + 1

        # get the baseline temperature from config
        self.temperature = config.temperature

        if self.drawbot:
            print('locating home')
            self.drawbot.home()
            input('remove pen lid, then press enter')

            # self.drawbot.draw_stave(staves=staves)
            self.drawbot.go_position_ready()

    def main_loop(self):
        """
        starts the main thread for the gesture manager
        """
        gesture_thread = Thread(target=self.gesture_manager)
        command_list_thread = Thread(target=self.drawbot.manage_command_list)
        if self.drawbot:
            position_thread = Thread(target=self.drawbot.get_normalised_position)
            position_thread.start()

        # start threads
        command_list_thread.start()
        gesture_thread.start()

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
            #############################
            #
            # Phrase-level gesture gate: 3 - 8 seconds
            #
            #############################

            # flag for breaking a phrase from big affect signal
            self.hivemind.interrupt_clear = True

            # clear command list at start of each gesture cycle
            # self.drawbot.command_list.clear()
            self.drawbot.clear_commands()

            # get length of gesture
            phrase_length = (randrange(300, 800) / 100) # + self.global_speed
            phrase_loop_end = time() + phrase_length

            print(f"========= GESTURE - Daddy cycle started =========== Duration =  {phrase_length} seconds")

            ##################################################################
            # choose thought stream from data streams from Nebula/ live inputs
            ##################################################################

            # randomly pick an input stream for this cycle
            # either mic_in, random, net generation or self-awareness
            if random() < 0.36:
                rnd_stream = 'mic_in'
            else:
                rnd = randrange(stream_list_len)
                rnd_stream = stream_list[rnd]

            self.hivemind.thought_train_stream = rnd_stream
            print(f"Random stream = {self.hivemind.thought_train_stream}")

            # define robot mode for this phase length
            # set random mode and data source for continuous mode
            robot_mode = RobotMode(randrange(4))
            if robot_mode == RobotMode.Continuous:         # randomise continuous settings
                self.continuous_mode = randrange(2)      # 0 == on page, 1 == above page
                self.continuous_source = randrange(2)    # 0 == random, 1 == NN

            while time() < phrase_loop_end:
                #############################
                # Rhythm-level gesture gate: .5-2 seconds
                #############################

                # if a major break out then go to Daddy cycle and restart
                if not self.hivemind.interrupt_clear:
                    print("-----------------------------STREAM INTERRUPT----------------------------")
                    break

                # 1. clear the alarms
                if self.drawbot:
                    self.drawbot.clear_alarms()

                # # generate rhythm rate here
                rhythm_loop = time() + (randrange(500, 2000) / 1000)
                logging.debug(f'end time = {rhythm_loop}')

                # speed for this phrase
                arm_speed = randrange(30, 500)
                if self.DOBOT_CONNECTED or self.XARM_CONNECTED:
                    self.drawbot.set_speed(arm_speed)

                while time() < rhythm_loop:
                    #############################
                    # THis streams the chosen data around a loop
                    #############################

                    # make the master output the current value of the affect stream
                    # 1. go get the current value from dict
                    thought_train = getattr(self.hivemind, rnd_stream)
                    print(
                        f'========= RHYTHM cycle 2 ===========Affect stream output {rnd_stream} == {thought_train}')

                    # 2. send to Master Output
                    self.hivemind.master_stream = thought_train

                    ######################################
                    #
                    # Makes a response to chosen thought stream
                    #
                    ######################################

                    if thought_train > 0.8 or not self.hivemind.interrupt_clear:
                        print('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.hivemind.randomiser()

                        # B - jumps out of this loop into daddy
                        self.hivemind.interrupt_clear = False

                        # C - clears the command list in drawbot
                        self.drawbot.command_list.clear()

                        # D - respond
                        if self.drawbot:
                            self.high_energy_response()

                        # D- break out of this loop, and next (cos of flag)
                        sleep(0.1)
                        break

                        # LOW
                    elif thought_train <= 0.2 or not self.hivemind.interrupt_clear:
                        print('interrupt LOW ----------- no response')

                        if self.drawbot:
                            if random() < 0.36:
                                self.continuous(thought_train)
                            else:
                                sleep(0.1)

                    else:
                        # MID response
                        if self.drawbot:
                            match robot_mode:
                                case RobotMode.Continuous:
                                    # move continuously using data streams from EMD, borg
                                    print("Continuous Mode")
                                    self.continuous(thought_train)

                                case RobotMode.Modification:
                                    # random shapes inspired by Cardews "Treatise"
                                    print("Modification/ Cardew Mode")
                                    self.cardew_inspiration(thought_train)

                                case RobotMode.Inspiration:
                                    # random shapes inspired by Wolff's 1, 2, 3
                                    print("Inspiration/ Wolff Mode")
                                    self.wolff_inspiration(thought_train)

                                case RobotMode.Repetition:
                                    # large repeating gestures
                                    print("Repetition Mode")
                                    self.repetition(thought_train)

                    # and wait for a cycle
                    # sleep(rhythm_rate)
                    sleep(0.1)

        logging.info('quitting dobot director thread')
        self.terminate()

    def repetition(self, peak):
        self.drawbot.go_random_jump()
        self.drawbot.create_shape_group()  # create a new shape group
        for i in range(randrange(1, 2)):  # repeat the shape group a random number of times
            logging.debug("repetition of shape")
            self.drawbot.repeat_shape_group()

    def continuous(self,
                   peak: float):
        """
        Performs continuous movement in 2 different modes and from 3 different data sources, all randomised when the mode is randomised.
        Modes: 0 == on page drawing (xy), 1 == above page (xyz)
        Data sources: 1 = random data, 2 = NN data, 3 = peak (mic input)
        """

        # match self.continuous_mode:
        #     case 0:     # on page (z axis at draw height)
        #         match self.continuous_source:
        #             case 0:     # random data
        #                 move_x = uniform(-self.joint_inc, self.joint_inc)
        #                 move_y = uniform(-self.joint_inc, self.joint_inc)
        #
        #             case 1:     # NN data
        #                 move_x = uniform(self.hivemind.audio2core_2d[0, -1], - self.hivemind.audio2core_2d[0, -1]) * self.joint_inc
        #                 move_y = uniform(self.hivemind.audio2core_2d[1, -1], - self.hivemind.audio2core_2d[1, -1]) * self.joint_inc
        #
        #         move_z = 0
        #
        #     case 1:     # above page (z axis affected by data)
        #         # move_z = 0
        #         match self.continuous_source:
        #             case 0:     # random data
        #                 move_x = uniform(-self.joint_inc, self.joint_inc)
        #                 #move_y = uniform(-self.joint_inc, self.joint_inc)
        #                 move_z = uniform(-self.joint_inc, self.joint_inc)
        #
        #             case 1:     # NN data
        #                 move_x = uniform(self.hivemind.flow2core_2d[0, -1], - self.hivemind.flow2core_2d[0, -1]) * self.joint_inc
        #                 #move_y = uniform(self.hivemind.flow2core_2d[1], -self.hivemind.flow2core_2d[1]) * self.joint_inc
        #                 move_z = uniform(self.hivemind.flow2core_2d[1, -1], + self.hivemind.flow2core_2d[1, -1]) * self.joint_inc
        #
        #         move_y = 0

        move_x = uniform(-self.joint_inc, self.joint_inc) # * self.hivemind.mic_in
        move_y = uniform(-self.joint_inc, self.joint_inc) # * self.hivemind.mic_in
        move_z = randrange(self.joint_inc) # * self.hivemind.mic_in
        self.drawbot.position_move_by(move_x, move_y, move_z, wait=True)

    def wolff_inspiration(self, peak):
        """
        jumps to a random spot and makes a mark inspired by Wolff
        """
        # get the current position
        x, y, z = self.drawbot.get_pose()[:3]

        # jump to a random location
        self.drawbot.go_random_jump()

        # randomly choose from the following choices
        randchoice = randrange(6)
        logging.debug(f'randchoice WOLFF == {randchoice}')

        match randchoice:
            case 0:
                logging.info('Wolff: draw line')
                self.drawbot.move_to(x + self.rnd(peak),
                                     y + self.rnd(peak),
                                     z,
                                     False)

            case 1:
                logging.info('Wolff: random character')
                self.drawbot.draw_random_char(peak * randrange(10, 20))

            # TEMPORARY UNTIL ADAM COMPLETES
            # case 1:
            #     logging.info('Wolff: dot and line')
            #     self.drawbot.dot()

            case 2:
                logging.info('Wolff: dot')
                self.drawbot.dot()

            case 3:
                logging.info('Wolff: note head')
                note_size = randrange(1, 10)
                # note_shape = randrange(20)
                self.drawbot.note_head(size=note_size)

            case 4:
                logging.info('Wolff: note head and line')
                note_size = randrange(1, 10)
                self.drawbot.note_head(size=note_size)
                self.drawbot.position_move_by(self.rnd(peak), self.rnd(peak), 0, wait=True)    # draw small line from note head

            case 5:
                logging.info('Wolff: dot')
                self.drawbot.dot()

    def cardew_inspiration(self, peak):
        """
        randomly chooses a shape inspired by Cardew
        """
        x, y, z = self.drawbot.get_pose()[:3]

        # move Y along
        self.drawbot.move_y()

        # randomly choose from the following choices
        randchoice = randrange(6)
        logging.debug(f'randchoice CARDEW == {randchoice}')

        match randchoice:
            case 0:
                logging.info('Cardew: draw arc')
                are_range = peak * 10
                self.drawbot.arc2D(x + uniform(-are_range, are_range),
                                   y + uniform(-are_range, are_range),
                                   x + uniform(-are_range, are_range),
                                   y + uniform(-are_range, are_range)
                                   )

            case 1:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for n in range(randrange(3, 9)):
                    squiggle_list.append((uniform(-5, 5),
                                          uniform(-5, 5),
                                          uniform(-5, 5))
                                         )
                self.drawbot.squiggle(squiggle_list)

            case 2:
                logging.info('Cardew: draw circle')
                side = randrange(2)
                self.drawbot.draw_circle(int(peak * 10),
                                         side
                                         )

            case 3:
                logging.info('Cardew: line')
                self.drawbot.go_draw(x + self.rnd(peak * 10),
                                     y + self.rnd(peak * 10)
                                     )

            case 4:
                logging.info('Cardew: return to coord')
                self.drawbot.return_to_coord()

            case 5:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for n in range(randrange(3, 9)):
                    squiggle_list.append((uniform(-5, 5),
                                          uniform(-5, 5),
                                          uniform(-5, 5))
                                         )
                self.drawbot.squiggle(squiggle_list)

    def high_energy_response(self):
        """
        move to a random x, y position
        """
        # clear robot command cache
        self.drawbot.clear_commands()

    def terminate(self):
        """
        Smart collapse of all threads and comms
        """
        print('TERMINATING')
        self.drawbot.clear_commands()
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
        if random() >= 0.5:
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        logging.debug(f'Rnd result = {result}')
        return result
