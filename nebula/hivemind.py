from dataclasses import dataclass
from random import random, randrange


# DataBorg Pattern
# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html
# https://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
class DataBorg:
    __hivemind = None

    def __init__(self):
        if not DataBorg.__hivemind:
            DataBorg.__hivemind = self.__dict__

            ######################
            # Outputs from NNets in AI Factory
            ######################
            self.move_rnn: float = random()
            """Net 1 raw emission"""

            self.affect_rnn: float = random()
            """Net 2 raw emission"""

            self.move_affect_conv2: float = random()
            """Net 3 raw emission"""

            self.affect_move_conv2: float = random()
            """Net 4 raw emission"""

            self.self_awareness: float = random()
            """Net that has some self awareness - ???"""

            ######################
            # Outputs from NNets in AI Factory rework
            ######################
            self.eda2flow: float = random()
            """Net 1 raw emission"""

            self.eeg2flow: float = random()
            """Net 2 raw emission"""

            self.core2flow: float = random()
            """Net 3 raw emission"""

            ######################
            # Human inputs
            ######################
            self.mic_in: float = random()
            """Percept input stream from client e.g. live mic level"""

            self.eeg: list = [
                random(),
                random(),
                random(),
                random()
            ]
            """Live data from brainbit"""

            # TODO
            # self.eeg_buffer: np.array

            self.eeg_normalised: list = [
                random(),
                random(),
                random(),
                random()
            ]
            """normalised eeg output"""

            self.eeg_single: float = random()
            """pre-processed single data atom from eeg for thought train"""

            self.eda: int = 0
            """Live data from Bitalino"""

            ######################
            # Additional streams
            ######################

            self.master_stream: float = random()
            """Master output from the affect process"""

            self.rnd_poetry: float = random()
            """Random stream to spice things up"""

            self.thought_train_stream: str = " "
            """Current stream chosen by affect process"""

            self.rhythm_rate: float = randrange(30, 100) / 100
            """Internal clock/ rhythm sub division"""

            ######################
            # Robot vars
            ######################

            self.current_robot_x_y_z: tuple = (0, 0, 0)
            """Actual cartesian coords reported by Dobot"""

            self.current_nnet_x_y_z: tuple = (0, 0, 0)
            """Generated output of robot movement from NNets"""

            ######################
            # Running vars
            ######################

            self.interrupt_bang: bool = True
            """Signals an interrupt to the gesture manager"""

            self.running: bool = True
            """Master running bool for whole script"""

        else:
            self.__dict__ = DataBorg.__hivemind

    def randomiser(self):
        """ Blitz's the DataBorg dict with random numbers"""
        self.move_rnn = random()
        self.affect_rnn = random()
        self.move_affect_conv2 = random()
        self.affect_move_conv2 = random()
        self.master_stream = random()
        self.mic_in = random()
        self.rnd_poetry = random()
        # self.affect_net = random()
        self.self_awareness = random()
        # self.affect_decision = ""
        self.rhythm_rate = randrange(30, 100) / 100
        # self.rnd_stream = ""
        self.eeg = [random(),
                    random(),
                    random(),
                    random()]
        self.eeg_single = random()
