from time import time
from threading import Thread
import pyaudio
import numpy as np
import logging
from random import random
from serial.tools import list_ports

from modules.conducter import Conducter
from nebula.nebula import Nebula
from nebula.hivemind import DataBorg
# from bitalino import BITalino
import config

# from modules.drawbot import Drawbot


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

        # logging for all modules
        logging.basicConfig(level=logging.INFO)

        # build initial dataclass fill with random numbers
        self.hivemind = DataBorg()
        logging.debug(f'Data dict initial values are = {self.hivemind}')

        ############################
        # Ai Factory
        ############################
        # init the AI factory (inherits AIFactory, Listener)
        nebula = Nebula(speed=speed)

        ############################
        # Conducter & Gesture management (controls Drawbot)
        ############################
        self.robot1 = Conducter(
            duration_of_piece=duration_of_piece,
            continuous_line=continuous_line,
            speed=speed,
            staves=staves,
            pen=pen,
        )

        robot_thread = Thread(target=self.robot1.gesture_manager)

        # start Nebula AI Factory here after affect starts data moving
        robot_thread.start()
        nebula.main_loop()

        # # start operating vars
        # self.start_time = time()
        # self.end_time = self.start_time + duration_of_piece

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.hivemind.running = False
        # self.digibot.home()
        # self.digibot.close()
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
