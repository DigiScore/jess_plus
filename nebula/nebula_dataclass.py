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
            # Human inputs
            ######################
            self.mic_in: float = random()
            """Percept input stream from client e.g. live mic level"""

            self.eeg: list = [0, 0, 0, 0]
            """Live data from brainbit"""

            self.eda: int = 0
            """Live data from Bitalino"""

            ######################
            # Additional streams
            ######################

            self.master_stream: float = random()
            """Master output from the affect process"""

            self.rnd_poetry: float = random()
            """Random stream to spice things up"""

            # self.affect_net: float = random()
            # """Output from affect module"""

            self.thought_train_stream: str = " "
            """Current stream chosen by affect process"""

            self.rhythm_rate: float = randrange(30, 100) / 100
            """Internal clock/ rhythm sub division"""

            # self.rnd_stream: str = ""
            # """Stream name currently used for active data"""

            ######################
            # Additional vars
            ######################

            self.interrupt_bang = True

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



#
# #Dataclass Pattern
# @dataclass
# class NebulaDataClass:
#     """Dataclass containing all the data emissions
#     and user input to and from Nebula"""
#
#     move_rnn: float = random()
#     """Net 1 raw emission"""
#
#     affect_rnn: float = random()
#     """Net 2 raw emission"""
#
#     move_affect_conv2: float = random()
#     """Net 3 raw emission"""
#
#     affect_move_conv2: float = random()
#     """Net 4 raw emission"""
#
#     master_output: float = random()
#     """Master output from the affect process"""
#
#     mic_in: float = random()
#     """Percept input stream from client e.g. live mic level"""
#
#     rnd_poetry: float = random()
#     """Random stream to spice things up"""
#
#     affect_net: float = random()
#     """Output from affect module"""
#
#     self_awareness: float = random()
#     """Net that has some self awareness - ???"""
#
#     affect_decision: str = " "
#     """Current stream chosen by affect process"""
#
#     rhythm_rate: float = randrange(30, 100) / 100
#     """Internal clock/ rhythm sub division"""
#
#     # eeg_board: list
#     """Live data from brainbit"""
#
#     eda: int = 0
#     """Live data from Bitalino"""
#

