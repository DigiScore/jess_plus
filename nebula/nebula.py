"""
Embodied AI Engine Prototype AKA "Nebula". This object takes a live signal
(such as body tracking, or real-time sound analysis) and generates a response
that aims to be felt as co-creative. The response is a flow of neural network
emissions data packaged as a dictionary, and is gestural over time. This, when
plugged into a responding script (such as a sound generator, or QT graphics)
gives the feeling of the AI creating in-the-moment with the human in-the-loop.

© Craig Vear 2022-23
craig.vear@nottingham.ac.uk

Dedicated to Fabrizio Poltronieri
"""
import logging
import numpy as np
from threading import Thread
from time import sleep, time

import config
from modules.bitalino import BITalino
from modules.brainbit import BrainbitReader
from modules.listener import Listener
from nebula.ai_factory import AIFactoryRework


def scaler(in_feature, mins, maxs):
    in_feature = np.array(in_feature)
    mins = np.array(mins)
    maxs = np.array(maxs)
    in_feature = (in_feature - mins) / (maxs - mins)
    in_feature = in_feature.clip(0, 1)
    return in_feature


class Nebula(Listener, AIFactoryRework):
    """
    Nebula is the core "director" of an AI factory. It generates data in
    response to incoming percepts from human-in-the-loop interactions, and
    responds in-the-moment to the gestural input of live data.
    There are 4 components:
        - Nebula: as "director" it coordinates the overall operations of the AI
        Factory.
        - AIFactory: builds the neural nets that form the factory, coordinates
        data exchange, and liases with the common data dict.
        - Hivemind: is the central dataclass that holds and shares all the data
        exchanges in the AI factory.
        - Conducter: receives the live percept input from the client and
        produces an affectual response to it's energy input, which in turn
        interferes with the data generation.
    """
    def __init__(self, speed=1):
        """
        Parameters
        ----------
        speed
            General tempo/ feel of Nebula's response (0.5 ~ moderate fast,
            1 ~ moderato, 2 ~ presto).
        """
        print('Building engine server')
        Listener.__init__(self)

        # Set global vars
        self.hivemind.running = True

        # Build the AI factory and pass it the data dict
        AIFactoryRework.__init__(self, speed)
        self.BRAINBIT_CONNECTED = config.eeg_live
        self.BITALINO_CONNECTED = config.eda_live

        # Init brainbit reader
        if self.BRAINBIT_CONNECTED:
            logging.info("Starting EEG connection")
            self.eeg_board = BrainbitReader()
            self.eeg_board.start()
            first_brain_data = self.eeg_board.read(1)
            logging.info(f'Data from brainbit = {first_brain_data}')

        # Init bitalino
        if self.BITALINO_CONNECTED:
            BITALINO_MAC_ADDRESS = config.mac_address
            BITALINO_BAUDRATE = config.baudrate
            BITALINO_ACQ_CHANNELS = config.channels

            self.eda = BITalino(BITALINO_MAC_ADDRESS)
            self.eda.start(BITALINO_BAUDRATE, BITALINO_ACQ_CHANNELS)
            first_eda_data = self.eda.read(1)[0]
            logging.info(f'Data from BITalino = {first_eda_data}')

        # Work out master timing then collapse hivemind.running
        self.endtime = time() + config.duration_of_piece

    def main_loop(self):
        """
        Starts the server / AI threads and gets the data rolling.
        """
        print('Starting the Nebula director')
        # Declare all threads
        t1 = Thread(target=self.make_data)
        t2 = Thread(target=self.snd_listen)
        t3 = Thread(target=self.jess_input)

        # Start them all
        t1.start()
        t2.start()
        t3.start()

    def jess_input(self):
        """
        Listen to live human input.
        """
        while self.hivemind.running:
            if time() >= self.endtime:
                break
            # Read data from bitalino
            if self.BITALINO_CONNECTED:
                # Get raw data
                eda_raw = [self.eda.read(1)[0][-1]]
                logging.debug(f"eda data raw = {eda_raw}")
                # # Replace min and max for scaling
                # if eda_raw[0] > self.hivemind.eda_maxs[0]:
                #     self.hivemind.eda_maxs[0] = eda_raw[0]
                # if eda_raw[0] < self.hivemind.eda_mins[0]:
                #     self.hivemind.eda_mins[0] = eda_raw[0]
                # Rescale between 0 and 1
                eda_norm = scaler(eda_raw, self.hivemind.eda_mins,
                                  self.hivemind.eda_maxs)
                # Buffer append and pop
                eda_2d = eda_norm[:, np.newaxis]
                self.hivemind.eda_buffer = np.append(self.hivemind.eda_buffer,
                                                     eda_2d, axis=1)
                self.hivemind.eda_buffer = np.delete(self.hivemind.eda_buffer,
                                                     0, axis=1)
            else:
                # Random data if no bitalino
                self.hivemind.eda_buffer = np.random.uniform(size=(1, 50))

            # Read data from brainbit
            if self.BRAINBIT_CONNECTED:
                # Get raw data
                eeg = self.eeg_board.read(1)
                logging.debug(f"eeg data raw = {eeg}")
                # # Replace mins and maxs for scaling
                # for i_ch, eeg_ch in enumerate(eeg):
                #     if eeg_ch > self.hivemind.eeg_maxs[i_ch]:
                #         self.hivemind.eeg_maxs[i_ch] = eeg_ch
                #     if eeg_ch < self.hivemind.eeg_mins[i_ch]:
                #         self.hivemind.eeg_mins[i_ch] = eeg_ch
                # Rescale between 0 and 1
                eeg_norm = scaler(eeg, self.hivemind.eeg_mins,
                                  self.hivemind.eeg_maxs)
                # Buffer append and pop
                eeg_2d = eeg_norm[:, np.newaxis]
                self.hivemind.eeg_buffer = np.append(self.hivemind.eeg_buffer,
                                                     eeg_2d, axis=1)
                self.hivemind.eeg_buffer = np.delete(self.hivemind.eeg_buffer,
                                                     0, axis=1)
            else:
                # Random data if no brainbit
                self.hivemind.eeg_buffer = np.random.uniform(size=(4, 50))

            sleep(0.1)  # for 10 Hz

        self.hivemind.running = False

    def terminate(self):
        """
        Terminate threads and connections like a grownup.
        """
        if self.BRAINBIT_CONNECTED:
            self.eeg_board.terminate()
        if self.BITALINO_CONNECTED:
            self.eda.close()
