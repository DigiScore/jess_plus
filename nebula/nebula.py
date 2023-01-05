"""
Embodied AI Engine Prototype AKA "Nebula".
This object takes a live signal (such as body tracking,
or real-time sound analysis) and generates a response that
aims to be felt as co-creative. The response is a flow of
neural network emissions data packaged as a dictionary,
and is gestural over time. This, when plugged into a responding
script (such as a sound generator, or QT graphics) gives
the impression of the AI creating in-the-moment with the
human in-the-loop.

© Craig Vear 2022
cvear@dmu.ac.uk

Dedicated to Fabrizio Poltronieri
"""
# import python modules
from random import random, randrange
from threading import Thread
import logging
from time import sleep
from queue import Queue

# import Nebula modules
from nebula.ai_factory import AIFactory
# from nebula.affect import Affect
from nebula.nebula_dataclass import NebulaDataClass

class Nebula:
    """Nebula is the core "director" of an AI factory.
     It generates data in response to incoming percpts
    from human-in-the-loop interactions, and responds
    in-the-moment to the gestural input of live data.
    There are 4 components:
        Nebula: as "director" it coordinates the overall
            operations of the AI Factory
        AIFactory: builds the neural nets that form the
            factory, coordinates data exchange,
            and liases with the common data dict
        NebulaDataClass: is the central dataclass that
            holds and shares all the  data exchanges
            in the AI factory
        Affect: receives the live percept input from
            the client and produces an affectual response
            to it's energy input, which in turn interferes
            with the data generation.

    Args:
        speed: general tempo/ feel of Nebula's response (0.5 ~ moderate fast, 1 ~ moderato; 2 ~ presto)"""

    def __init__(self,
                 datadict: NebulaDataClass,
                 speed=1,
                 ):
        print('building engine server')

        # Set global vars
        self.interrupt_bang = False
        self.rnd_stream = 0
        self.rhythm_rate = 1
        self.affect_listen = 0

        # build the dataclass and fill with random number
        self.datadict = datadict
        logging.debug(f'Data dict initial values are = {self.datadict}')

        # Build the AI factory and pass it the data dict
        self.AI_factory = AIFactory(self.datadict, speed)

    def main_loop(self):
        """Starts the server/ AI threads
         and gets the data rolling."""
        print('Starting the Nebula Director')
        # declares all threads
        t1 = Thread(target=self.AI_factory.make_data)

        # start them all
        t1.start()

    #################################
    #
    # High Level I/O for the client
    # will generally be used in a server thread
    #
    #################################
    #
    # def user_emission_list(self):
    #     """This list is highest level comms back to client """
    #     return self.emission_list

    # def user_live_emission_data(self):
    #     """Returns the current value of the AI factory master output"""
    #     return self.affect.live_emission_data
    #     # return getattr(self.datadict, 'master_output')

    # def user_input(self, user_input_value: float):
    #     """High-level input from client usually from
    #     real-time percept.
    #     Must be normalised 0.0-1.0"""
    #     print('Nebula user input', user_input_value)
    #     setattr(self.datadict, 'user_in', user_input_value)

    def terminate(self):
        # self.affect.quit()
        self.AI_factory.quit()

if __name__ == '__main':
    logging.basicConfig(level=logging.INFO)
    test = Nebula()
    test.director()

