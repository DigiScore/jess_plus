from dataclasses import dataclass
from random import random, randrange


#Dataclass Pattern
@dataclass
class NebulaDataClass:
    """Dataclass containing all the data emissions
    and user input to and from Nebula"""

    move_rnn: float = random()
    """Net 1 raw emission"""

    affect_rnn: float = random()
    """Net 2 raw emission"""

    move_affect_conv2: float = random()
    """Net 3 raw emission"""

    affect_move_conv2: float = random()
    """Net 4 raw emission"""

    master_output: float = random()
    """Master output from the affect process"""

    user_in: float = random()
    """Percept input stream from client e.g. live mic level"""

    rnd_poetry: float = random()
    """Random stream to spice things up"""

    affect_net: float = random()
    """Output from affect module"""

    self_awareness: float = random()
    """Net that has some self awareness - ???"""

    affect_decision: str = " "
    """Current stream chosen by affect process"""

    rhythm_rate: float = randrange(30, 100) / 100
    """Internal clock/ rhythm sub division"""

    # eeg: list
    """Live data from brainbit"""

    eda: int = 0
    """Live data from Bitalino"""


#Borg Pattern
class Borg:

    __monostate = None

    def __init__(self):
        if not Borg.__monostate:
            Borg.__monostate = self.__dict__
            self.move_rnn: float = random()
            """Net 1 raw emission"""

            self.affect_rnn: float = random()
            """Net 2 raw emission"""

            self.move_affect_conv2: float = random()
            """Net 3 raw emission"""

            self.affect_move_conv2: float = random()
            """Net 4 raw emission"""

            self.master_output: float = random()
            """Master output from the affect process"""

            self.user_in: float = random()
            """Percept input stream from client e.g. live mic level"""

            self.rnd_poetry: float = random()
            """Random stream to spice things up"""

            self.affect_net: float = random()
            """Output from affect module"""

            self.self_awareness: float = random()
            """Net that has some self awareness - ???"""

            self.affect_decision: str = " "
            """Current stream chosen by affect process"""

            self.rhythm_rate: float = randrange(30, 100) / 100
            """Internal clock/ rhythm sub division"""

            self.eeg: list = [0, 0, 0, 0]
            """Live data from brainbit"""

            self.eda: int = 0
            """Live data from Bitalino"""

            self.fields = ["move_rnn",
                           "affect_rnn",
                           "move_affect_conv2",
                           "affect_move_conv2",
                           "master_output",
                           "user_in",
                           "rnd_poetry",
                           "affect_net",
                           "self_awareness",
                           "affect_decision",
                           "rhythm_rate",
                           "eeg",
                           "eda"
                           ]

        else:
            self.__dict__ = Borg.__monostate

