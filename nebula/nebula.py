"""
Embodied AI Engine Prototype AKA "Nebula".
This object takes a live signal (such as body tracking,
or real-time sound analysis) and generates a response that
aims to be felt as co-creative. The response is a flow of
neural network emissions data packaged as a dictionary,
and is gestural over time. This, when plugged into a responding
script (such as a sound generator, or QT graphics) gives
the feeling of the AI creating in-the-moment with the
human in-the-loop.

© Craig Vear 2022
cvear@dmu.ac.uk

Dedicated to Fabrizio Poltronieri
"""
# import python modules
from threading import Thread
import logging
from configparser import ConfigParser
from time import sleep

# import Nebula modules
from nebula.ai_factory import AIFactory
from nebula.nebula_dataclass import DataBorg # NebulaDataClass
# from brainbit import BrainbitReader
# from bitalino import BITalino
import config

# todo JOHANNS script

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
                 speed=1,
                 # datadict=NebulaDataClass
                 ):
        print('building engine server')

        # Set global vars
        self.running = True
        # self.rnd_stream = 0
        # self.rhythm_rate = 1
        # self.affect_listen = 0

        # build the dataclass and fill with random number
        # self.datadict = datadict
        self.datadict = DataBorg()

        logging.debug(f'Data dict initial values are = {self.datadict}')

        # Build the AI factory and pass it the data dict
        self.AI_factory = AIFactory(speed) #, datadict)

        # init the EEG and EDA percepts
        # config_object = ConfigParser()
        # config_object.read('config.ini')

        # self.BRAINBIT_CONNECTED = config.brainbit
        #
        # # init brainbit reader
        # if self.BRAINBIT_CONNECTED:
        #     self.eeg_board = BrainbitReader()
        #     self.eeg_board.start()
        #     first_brain_data = self.eeg_board.read()
        #     logging.info(f'Data from brainbit = {first_brain_data}')
        #
        # # # init bitalino
        # if self.BITALINO_CONNECTED:
        #     self.eda = BITalino(BITALINO_MAC_ADDRESS)
        #     self.eda.start(BITALINO_BAUDRATE, BITALINO_ACQ_CHANNELS)
        #     first_eda_data = self.eda.read(10)
        #     logging.info(f'Data from BITalino = {first_eda_data}')

    def main_loop(self):
        """Starts the server/ AI threads
         and gets the data rolling."""
        print('Starting the Nebula Director')
        # declares all threads
        t1 = Thread(target=self.AI_factory.make_data)
        # t2 = Thread(target=self.jess_input)

        # start them all
        t1.start()
        # t2.start()

    # def jess_input(self):
    #     while self.running:
    #         # read data from bitalino
    #         if self.BITALINO_CONNECTED:
    #             eda_data = self.eda.read()
    #             # setattr(self.datadict, 'eda', eda_data)
    #             self.datadict.eda = eda_data
    #
    #         # read data from brainbit
    #         if self.BRAINBIT_CONNECTED:
    #             eeg_data = self.eeg_board.read()
    #             # setattr(self.datadict, 'eeg_board', eeg_data)
    #             self.datadict.eeg_board = eeg_data
    #             print(eeg_data)
    #
    #         sleep(0.1)

    def terminate(self):
        # self.affect.quit()
        self.AI_factory.quit()
        # self.eeg_board.terminate()
        # self.eda.close()
        self.running = False

if __name__ == '__main':
    logging.basicConfig(level=logging.DEBUG)
    test = Nebula()
    test.main_loop()
