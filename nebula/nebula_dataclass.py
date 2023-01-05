from dataclasses import dataclass
from random import random, randrange

# todo - dataclasses can be quite slow.
#  Perhaps replace with record class, slots or other [HIGH]

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
