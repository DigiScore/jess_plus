import logging
from enum import Enum
from random import random, randrange, uniform
from threading import Thread
from time import sleep, time

import config
from nebula.hivemind import DataBorg


class RobotMode(Enum):
    Continuous = 0
    Modification = 1
    Inspiration = 2
    Repetition = 3
    OffPage = 4


class Conducter:
    """
    Controls movement and shapes drawn by the robot.
    """
    def __init__(self, speed: int = 5):

        self.DOBOT_CONNECTED = config.dobot_connected
        verbose = config.dobot_verbose

        self.XARM_CONNECTED = config.xarm_connected

        # Start robot communication,  may need `sudo chmod 666 /dev/ttyACM0`
        if self.DOBOT_CONNECTED:
            from modules.drawDobot import Drawbot

            port = config.dobot1_port
            self.drawbot = Drawbot(port=port, verbose=verbose)

        elif self.XARM_CONNECTED:
            from modules.drawXarm import DrawXarm

            port = config.xarm1_port
            self.drawbot = DrawXarm(port)

        else:
            self.drawbot = None

        # Own the dataclass
        self.hivemind = DataBorg()

        # Start operating vars
        self.current_phrase_num = 0  # number of phrases looped through, can be used to change behaviour over time...
        self.joint_inc = 10          # scaling factor for incremental movement
        self.continuous_mode = 0     # mode for continuous module. 0 == on page, 1 == above page
        self.continuous_source = 0   # source of data used for continous movement. 0 == random, 1 == NN, 2 == peak
        self.global_speed = speed

        # Get the baseline temperature from config
        self.temperature = config.temperature

        if self.drawbot:
            print('Going to ready position...')
            self.drawbot.go_position_ready()
            input('Remove pen lid, then press ENTER')
            self.drawbot.go_position_one_two()
            self.drawbot.go_position_ready()

    def main_loop(self):
        """
        Starts the main thread for the gesture manager
        """
        gesture_thread = Thread(target=self.gesture_manager)
        gesture_thread.start()

        if self.drawbot:
            position_thread = Thread(target=self.drawbot.get_normalised_position)
            position_thread.start()
            self.drawbot.command_list_main_loop()

    def gesture_manager(self):
        """
        Listens to the realtime incoming signal and calculates an affectual
        response based on general boundaries:
            HIGH   - if input stream is LOUD (0.7+) then emit, smash a random
                     fill and break out to Daddy cycle.
            MEDIUM - if input energy is 0.1-0.7 then emit, a jump out of child
                     loop.
            LOW    - nothing happens, continues with cycles.
        """

        if self.drawbot:
            print("Started robot control thread")
            self.drawbot.go_position_draw()

        # Names for affect listening
        stream_list = config.stream_list
        stream_list_len = len(stream_list)

        while self.hivemind.running:
            ###################################################################
            # Phrase-level gesture gate: 3 - 8 seconds
            ###################################################################
            if self.XARM_CONNECTED:
                self.drawbot.random_pen()

            # Flag for breaking a phrase from big affect signal
            self.hivemind.interrupt_clear = True

            # Clear command list at start of each gesture cycle
            self.drawbot.clear_commands()

            # Get length of gesture
            phrase_length = (randrange(300, 800) / 100)  # + self.global_speed
            phrase_loop_end = time() + phrase_length

            print(f"======== GESTURE - Daddy cycle started ========", end=' ')
            print(f"Duration =  {phrase_length} seconds")

            ###################################################################
            # Randomly pick an input stream for this cycle
            # (either mic_in or stream in config.stream_list)
            ###################################################################
            if random() < 0.36:
                rnd_stream = 'mic_in'
            else:
                rnd = randrange(stream_list_len)
                rnd_stream = stream_list[rnd]

            self.hivemind.thought_train_stream = rnd_stream
            print(f"Random stream = {self.hivemind.thought_train_stream}")

            # Define robot mode for this phase length
            # Set random mode and data source for continuous mode
            robot_mode = RobotMode(randrange(4))
            if robot_mode == RobotMode.Continuous:  # randomise continuous settings
                self.continuous_mode = randrange(2)    # 0 == on page, 1 == above page
                self.continuous_source = randrange(2)  # 0 == random, 1 == NN

            while time() < phrase_loop_end:
                ###############################################################
                # Rhythm-level gesture gate: .5-2 seconds
                ###############################################################

                # if a major break out then go to Daddy cycle and restart
                if not self.hivemind.interrupt_clear:
                    print("----------------STREAM INTERRUPT----------------")
                    break

                # Clear the alarms
                if self.drawbot:
                    self.drawbot.clear_alarms()

                # Generate rhythm rate here
                rhythm_loop_end_time = time() + (randrange(500, 2000) / 1000)
                logging.debug(f'end time = {rhythm_loop_end_time}')

                # Speed for this phrase
                arm_speed = randrange(30, 500)
                if self.DOBOT_CONNECTED or self.XARM_CONNECTED:
                    self.drawbot.set_speed(arm_speed)

                while time() < rhythm_loop_end_time:
                    ###########################################################
                    # Stream the chosen data around a loop
                    ###########################################################

                    # Make master output the current value of affect stream
                    # 1. Go get the current value from dict
                    thought_train = getattr(self.hivemind, rnd_stream)
                    print(f'======== RHYTHM cycle 2 ========', end=' ')
                    print(f'Affect stream output {rnd_stream} == {thought_train}')

                    # 2. Send to Master Output
                    self.hivemind.master_stream = thought_train

                    ###########################################################
                    # Makes a response to chosen thought stream
                    ###########################################################
                    # [HIGH response]
                    if thought_train > 0.7 or not self.hivemind.interrupt_clear:
                        print('Interrupt > !!! HIGH !!!')

                        # A - Refill dict with random
                        self.hivemind.randomiser()

                        # B - Jumps out of this loop into daddy
                        self.hivemind.interrupt_clear = False

                        # C - Clears the command list in drawbot
                        self.drawbot.command_list.clear()

                        # D - Respond
                        if self.drawbot:
                            self.high_energy_response()

                        # D- Break out of this loop, and next because of flag
                        sleep(0.1)
                        break

                    # [LOW response]
                    elif thought_train < 0.1:
                        print('Interrupt < LOW : no response')
                        if self.drawbot:
                            if random() < 0.36:
                                self.continuous(thought_train)

                    # [MEDIUM response]
                    else:
                        if self.drawbot:
                            match robot_mode:  # determined at gesture loop point
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

                    sleep(0.1)

        logging.info('quitting dobot director thread')
        self.terminate()

    def repetition(self):
        """
        Create a shape group and repeat it a random number of times.
        """
        self.drawbot.go_random_jump()
        self.drawbot.create_shape_group()
        for _ in range(randrange(1, 2)):
            logging.debug("repetition of shape")
            self.drawbot.repeat_shape_group()

    def continuous(self):
        """
        Performs continuous movement in 2 different modes and from 3 different
        data sources, all randomised when the mode is randomised.
        Modes:
            0 == on page drawing (xy)
            1 == above page (xyz)
        Data sources:
            1 = random data
            2 = NN data
            3 = peak (mic input)
        """
        logging.info("Drawing continuous")
        if self.DOBOT_CONNECTED:
            move_x = uniform(-self.joint_inc, self.joint_inc)
            move_y = uniform(-self.joint_inc, self.joint_inc)
            move_z = randrange(self.joint_inc)
            self.drawbot.position_move_by(move_x, move_y, move_z, wait=True)
        if self.XARM_CONNECTED:
            self.drawbot.go_random_3d()

    def wolff_inspiration(self, peak):
        """
        Jumps to a random spot and makes a mark inspired by Wolff.
        """
        x, y = self.drawbot.get_pose()[:2]
        self.drawbot.go_random_jump()

        randchoice = randrange(6)
        logging.debug(f'Random Wolff choice: {randchoice}')

        match randchoice:
            case 0:
                logging.info('Wolff: draw line')
                self.drawbot.go_draw(x + self.rnd(peak*10),
                                     y + self.rnd(peak*10),
                                     False)

            case 1:
                logging.info('Wolff: random character')
                self.drawbot.draw_random_char(peak * randrange(10, 20))

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
                self.drawbot.position_move_by(self.rnd(peak*10),
                                              self.rnd(peak*10),
                                              0, wait=True)

            case 5:
                logging.info('Wolff: dot')
                self.drawbot.dot()

    def cardew_inspiration(self, peak):
        """
        Randomly draws a shape inspired by Cardew.
        """
        x, y = self.drawbot.get_pose()[:2]
        self.drawbot.go_random_draw()

        randchoice = randrange(6)
        logging.debug(f'Random Cardew choice == {randchoice}')

        arc_range = peak * 10
        match randchoice:
            case 0:
                logging.info('Cardew: draw arc')
                self.drawbot.arc2D(x + self.rnd(arc_range),
                                   y + self.rnd(arc_range),
                                   x + self.rnd(arc_range),
                                   y + self.rnd(arc_range))

            case 1:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for _ in range(randrange(3, 9)):
                    squiggle_list.append((self.rnd(arc_range),
                                          self.rnd(arc_range),
                                          self.rnd(arc_range)))
                self.drawbot.squiggle(squiggle_list)

            case 2:
                logging.info('Cardew: draw circle')
                side = randrange(2)
                self.drawbot.draw_circle(int(arc_range), side)

            case 3:
                logging.info('Cardew: line')
                self.drawbot.go_draw(x + self.rnd(arc_range),
                                     y + self.rnd(arc_range))

            case 4:
                logging.info('Cardew: return to coord')
                self.drawbot.return_to_coord()

            case 5:
                logging.info('Cardew: small squiggle')
                squiggle_list = []
                for _ in range(randrange(3, 9)):
                    squiggle_list.append((self.rnd(arc_range),
                                          self.rnd(arc_range),
                                          self.rnd(arc_range)))
                self.drawbot.squiggle(squiggle_list)

    def high_energy_response(self):
        """
        Clear commands to interupt current gesture and moves on to new ones.
        """
        self.drawbot.clear_commands()

    def terminate(self):
        """
        Smart collapse of all threads and comms.
        """
        print('TERMINATING')
        self.drawbot.go_position_ready()
        self.drawbot.go_position_one_two()
        self.drawbot.home()
        self.drawbot.clear_commands()
        if self.DOBOT_CONNECTED:
            self.drawbot.close()
        elif self.XARM_CONNECTED:
            self.drawbot.set_fence_mode(False)
            self.drawbot.disconnect()

    def rnd(self, power_of_command: int) -> int:
        """
        Returns a randomly generated positive or negative integer, influenced
        by the incoming power factor.
        """
        power_of_command = int(power_of_command)
        if power_of_command <= 0:
            power_of_command = 1
        pos = 1
        if random() >= 0.5:
            pos = -1
        result = (randrange(1, 5) + randrange(power_of_command)) * pos
        if result == 0:
            result = 1
        logging.debug(f'Rnd result = {result}')
        return result
