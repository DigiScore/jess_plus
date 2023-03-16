from time import time
from threading import Thread
import pyaudio
import numpy as np
import logging
from random import random
from serial.tools import list_ports

from modules.conducter import Conducter
from nebula.nebula import Nebula
from nebula.nebula_dataclass import DataBorg
# from bitalino import BITalino
import config

from modules.drawbot import Drawbot


class Main:
    """
    The main script to start the robot arm drawing digital score work.
    Affect calls the local interpreter for project specific functions.
    This communicates directly to the pydobot library.
    Nebula kick-starts the AI Factory for generating NNet data and affect flows.
    This script also controls the live mic audio analyser.
    Args:
        duration_of_piece: the duration in seconds of the drawing
        continuous_line: Bool: True = will not jump between points
        speed: int the dynamic tempo of the all processes. 1 = slow, 10 = fast
        pen: bool - True for pen, false for pencil
    """
    def __init__(self, duration_of_piece: int = 120,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True):

        # config & logging for all modules
        logging.basicConfig(level=logging.DEBUG)
        ROBOT_CONNECTED = config.robot
        EEG_CONNECTED = config.eeg
        GRAPH = config.eeg_graph

        # build initial dataclass fill with random numbers
        # self.hivemind = NebulaDataClass()
        self.hivemind = DataBorg()
        logging.debug(f'Data dict initial values are = {self.hivemind}')

        ############################
        # Ai Factory
        ############################

        # init the AI factory
        self.nebula = Nebula(speed=speed)

        ############################
        # Robot
        ############################

        # start dobot communications
        if ROBOT_CONNECTED:
            # find available ports and locate Dobot (-1)
            available_ports = list_ports.comports()
            print(f'available ports: {[x.device for x in available_ports]}')
            port = available_ports[-1].device

            drawbot = Drawbot(port=port,
                                   verbose=True,
                                   duration_of_piece=duration_of_piece,
                                   continuous_line=continuous_line
                                   )
        else:
            drawbot = None

        ############################
        # Affect & Gesture management
        ############################

        self.affect = Conducter(duration_of_piece=duration_of_piece,
                                continuous_line=continuous_line,
                                speed=speed,
                                staves=staves,
                                pen=pen,
                                drawbot=drawbot
                                )

        gesture_thread = Thread(target=self.affect.gesture_manager)
        gesture_thread.start()

        # start Nebula AI Factory here after affect starts data moving
        self.nebula.main_loop()

        ############################
        # Mic listener
        ############################

        # set up mic listening funcs
        self.CHUNK = 2 ** 11
        self.RATE = 44100
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)

        # # start operating vars
        self.running = True
        self.start_time = time()
        self.end_time = self.start_time + duration_of_piece

        # start the bot listening and drawing threads
        listener_thread = Thread(target=self.listener)
        listener_thread.start()

        ############################
        # BrainBit & UI
        ############################
        # todo CRAIG get these working
        # if EEG_CONNECTED:
        #     logging.info("Starting EEG connection")
        #     self.eeg_board = BrainbitReader()
        #     self.eeg_board.start()
        #     first_brain_data = self.eeg_board.read(255)
        #     logging.info(f'Data from brainbit = {first_brain_data}')


    def listener(self):
        """Loop thread that listens to live sound and analyses amplitude.
        Normalises then stores this into the nebula dataclass for shared use."""

        print("Starting mic listening stream & thread")
        while self.running:
            if time() > self.end_time:
                self.terminate()
                self.running = False
                break

            # get amplitude from mic input
            data = np.frombuffer(self.stream.read(
                self.CHUNK,
                exception_on_overflow=False),
                                 dtype=np.int16)
            peak = np.average(np.abs(data)) * 2

            if peak > 2000:
                bars = "#" * int(50 * peak / 2 ** 16)
                logging.debug("MIC LISTENER: %05d %s" % (peak, bars))

            # normalise it for range 0.0 - 1.0
            normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
            if normalised_peak > 1.0:
                normalised_peak = 1.0

            # put normalised amplitude into Nebula's dictionary for use
            self.hivemind.mic_in = normalised_peak

            # if loud sound then 63% affect gesture manager
            if normalised_peak > 0.8:
                if random() > 0.63:
                    self.hivemind.interrupt_bang = False
                    self.hivemind.randomiser()
                    print("-----------------------------INTERRUPT----------------------------")

        logging.info('quitting listener thread')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.digibot.running = False
        self.digibot.home()
        self.digibot.close()
        # self.eeg_board.terminate()
        # self.eda.close()


if __name__ == "__main__":
    Main(
        duration_of_piece=200,
         continuous_line=False,
         speed=10,
         staves=0,
         pen=True
    )
