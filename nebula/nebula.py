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

© Craig Vear 2022-23
craig.vear@nottingham.ac.uk

Dedicated to Fabrizio Poltronieri
"""
# import python modules
from threading import Thread
import logging
import numpy as np
from time import sleep, time
from modules.bitalino import BITalino


# import Nebula modules
from nebula.ai_factory import AIFactory, AIFactoryRework
from modules.listener import Listener
import config
from modules.brainbit import BrainbitReader


def scaler(in_feature, mins, maxs):
    in_feature = np.array(in_feature)
    mins = np.array(mins)
    maxs = np.array(maxs)
    in_feature = (in_feature - mins) / (maxs - mins)
    in_feature = in_feature.clip(0, 1)
    return in_feature


class Nebula(Listener,
             AIFactoryRework
             ):
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
                 Hivemind: is the central dataclass that
                     holds and shares all the  data exchanges
                     in the AI factory
                 Conducter: receives the live percept input from
                     the client and produces an affectual response
                     to it's energy input, which in turn interferes
                     with the data generation.

             Args:
                 speed: general tempo/ feel of Nebula's response (0.5 ~ moderate fast, 1 ~ moderato; 2 ~ presto)"""

    def __init__(
            self,
            speed=1,
    ):

        print('building engine server')
        Listener.__init__(self)

        # Set global vars
        self.hivemind.running = True

        # Build the AI factory and pass it the data dict
        AIFactoryRework.__init__(
            self,
            speed
        )
        self.BRAINBIT_CONNECTED = config.eeg_live
        self.BITALINO_CONNECTED = config.eda_live

        # init brainbit reader
        if self.BRAINBIT_CONNECTED:
            logging.info("Starting EEG connection")
            self.eeg_board = BrainbitReader()
            self.eeg_board.start()
            first_brain_data = self.eeg_board.read(1)
            logging.info(f'Data from brainbit = {first_brain_data}')

        # init bitalino
        if self.BITALINO_CONNECTED:
            BITALINO_MAC_ADDRESS = config.mac_address
            BITALINO_BAUDRATE = config.baudrate
            BITALINO_ACQ_CHANNELS = config.channels

            self.eda = BITalino(BITALINO_MAC_ADDRESS)
            self.eda.start(BITALINO_BAUDRATE, BITALINO_ACQ_CHANNELS)
            first_eda_data = self.eda.read(10)
            logging.info(f'Data from BITalino = {first_eda_data}')

        # work out master timing then collapse hivemind.running
        self.endtime = time() + config.duration_of_piece

    def main_loop(self):
        """Starts the server/ AI threads
         and gets the data rolling."""
        print('Starting the Nebula Director')
        # declares all threads
        t1 = Thread(target=self.make_data)
        t2 = Thread(target=self.snd_listen)
        t3 = Thread(target=self.jess_input)

        # start them all
        t1.start()
        t2.start()
        t3.start()

    def jess_input(self):
        """
        Listens to live human input
        :return:
        """
        while time() <= self.endtime:
            # read data from bitalino
            if self.BITALINO_CONNECTED:
                eda_data = self.eda.read()

                # rescale for hivemind
                raw_eda = eda_data[0][-1]
                # new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
                eda_rescale = ((raw_eda - 0) / (300 - 0)) * (1 - 0) + 0

                if eda_rescale > 1:
                    eda_rescale = 1
                logging.debug(f"eda  raw = {eda_rescale}")
                self.hivemind.eda = eda_data[0][-1]

            # read data from brainbit
            if self.BRAINBIT_CONNECTED:
                eeg = []
                eeg = self.eeg_board.read(1)
                logging.debug(f"eeg data raw = {eeg}")
                eeg_norm = scaler(eeg, self.hivemind.eeg_mins, self.hivemind.eeg_maxs)
                eeg_2d = eeg_norm[:, np.newaxis]
                self.hivemind.eeg_buffer = np.append(self.hivemind.eeg_buffer, eeg_2d, axis=1)
                self.hivemind.eeg_buffer = np.delete(self.hivemind.eeg_buffer, 0, axis=1)

            sleep(0.1)  # for 10 Hz

        self.hivemind.running = False

    # def normalise_eeg(self, eeg) -> float:
    #     """
    #     takes an eeg data atom -10000 -> 10000, and
    #     normalises it between 0.0 -> 1.0
    #     :param eeg: float
    #     :return:
    #     """
    #     # new_value = ((old_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
    #     eeg_normalised = ((eeg - -10000) / (10000 - -10000)) * (1.0 - 0.0) + 0.0
    #     return eeg_normalised

    def terminate(self):
        # self.affect.quit()
        self.AI_factory.quit()
        # self.eeg_board.terminate()
        # self.eda.close()
        self.running = False
