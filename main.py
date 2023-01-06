from time import sleep, time
from threading import Thread
import pyaudio
import numpy as np
import logging
from serial.tools import list_ports
from configparser import ConfigParser

from digibot import Digibot
from nebula.nebula import Nebula
from nebula.nebula_dataclass import NebulaDataClass, Borg
from brainbit import BrainbitReader
from bitalino import BITalino

class Main:
    """
    The main script to start the robot arm drawing digital score work.
    Digibot calls the local interpreter for project specific functions.
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
        logging.basicConfig(level=logging.INFO)

        config_object = ConfigParser()
        config_object.read('config.ini')
        #
        # BITALINO_BAUDRATE = config_object['BITALINO'].getint('baudrate')
        # BITALINO_ACQ_CHANNELS = config_object['BITALINO']['channels']
        # BITALINO_MAC_ADDRESS = config_object['BITALINO']['mac_address']
        #
        # BITALINO_CONNECTED = config_object['HARDWARE']['bitalino']
        # BRAINBIT_CONNECTED = config_object['HARDWARE']['brainbit']
        DOBOT_CONNECTED = config_object['HARDWARE']['dobot']
        #
        # # init brainbit reader
        # if BRAINBIT_CONNECTED:
        #     self.eeg = BrainbitReader()
        #     self.eeg.start()
        #     first_brain_data = self.eeg.read()
        #     logging.debug(f'Data from brainbit = {first_brain_data}')
        #
        # # init bitalino
        # if BITALINO_CONNECTED:
        #     self.eda = BITalino(BITALINO_MAC_ADDRESS)
        #     self.eda.start(BITALINO_BAUDRATE, BITALINO_ACQ_CHANNELS)
        #     first_eda_data = self.eda.read(10)
        #     logging.debug(f'Data from BITalino = {first_eda_data}')

        # build initial dataclas
        # build the dataclass and fill with random number
        self.datadict = NebulaDataClass()
        logging.debug(f'Data dict initial values are = {self.datadict}')

        # find available ports and locate Dobot (-1)
        available_ports = list_ports.comports()
        print(f'available ports: {[x.device for x in available_ports]}')
        port = available_ports[-1].device

        # start dobot communications
        if DOBOT_CONNECTED:
            self.digibot = Digibot(port=port,
                               datadict=self.datadict,
                               verbose=False,
                               duration_of_piece=duration_of_piece,
                               continuous_line=continuous_line,
                               speed=speed,
                               staves=staves,
                               pen=pen
                               )

        # start Nebula AI Factory
        self.nebula = Nebula(datadict=self.datadict,
                             speed=speed,
                             )
        self.nebula.main_loop()

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
        dobot_thread = Thread(target=self.digibot.drawbot_control)

        listener_thread.start()
        dobot_thread.start()

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
            setattr(self.datadict, 'user_in', normalised_peak)

        logging.info('quitting listener thread')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.digibot.running = False
        self.digibot.home()
        self.digibot.close()
        # self.eeg.terminate()
        # self.eda.close()


if __name__ == "__main__":
    Main(duration_of_piece=200,
         continuous_line=True,
         speed=10,
         staves=0,
         pen=True)

