from time import sleep, time
from threading import Thread
import pyaudio
import numpy as np
import logging
from serial.tools import list_ports
from configparser import ConfigParser
import threading

from digibot import Digibot
from nebula.nebula import Nebula
from nebula.nebula_dataclass import NebulaDataClass
from brainbit import BrainbitReader
# from bitalino import BITalino
import config

import pyqtgraph as pg
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations
from pyqtgraph.Qt import QtGui, QtCore



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
        ROBOT_CONNECTED = config.robot
        EEG_CONNECTED = config.eeg
        GRAPH = config.eeg_graph

        # build initial dataclass fill with random numbers
        # self.datadict = NebulaDataClass()
        self.datadict = NebulaDataClass()
        logging.debug(f'Data dict initial values are = {self.datadict}')

        ############################
        # Ai Factory
        ############################

        # init the AI factory
        self.nebula = Nebula(speed=speed,
                             datadict=self.datadict)

        ############################
        # Robot
        ############################

        # start dobot communications
        if ROBOT_CONNECTED:
            # find available ports and locate Dobot (-1)
            available_ports = list_ports.comports()
            print(f'available ports: {[x.device for x in available_ports]}')
            port = available_ports[-1].device

            self.digibot = Digibot(port=port,
                                   verbose=False,
                                   duration_of_piece=duration_of_piece,
                                   continuous_line=continuous_line,
                                   speed=speed,
                                   staves=staves,
                                   pen=pen,
                                   datadict=self.datadict
                                   )
            dobot_thread = Thread(target=self.digibot.drawbot_control)
            dobot_thread.start()

        # start Nebula AI Factory
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
        if EEG_CONNECTED:
            logging.info("Starting EEG connection")
            self.eeg_board = BrainbitReader(self.datadict)
            self.eeg_board.start()
            first_brain_data = self.eeg_board.read(255)
            logging.info(f'Data from brainbit = {first_brain_data}')

            # todo - graph widget doesnt show. need different solution.
            # try:
            if GRAPH:
                print("building UI")
                Graph(self.eeg_board)


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
            # self.datadict['user in'] = normalised_peak

        logging.info('quitting listener thread')

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.digibot.running = False
        self.digibot.home()
        self.digibot.close()
        # self.eeg_board.terminate()
        # self.eda.close()

class Graph:
    def __init__(self, eeg_board):
        print("Initialising EEG graph")
        self.eeg_board = eeg_board
        self.eeg_board_shim = eeg_board.board
        # self.board_id = self.eeg_board_shim.get_board_id()
        self.exg_channels = self.eeg_board_shim.get_exg_channels(self.eeg_board_shim .board_id)
        self.sampling_rate = self.eeg_board_shim.get_sampling_rate(self.eeg_board_shim .board_id)
        self.update_speed_ms = 50
        self.window_size = 4
        self.num_points = self.window_size * self.sampling_rate

        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsLayoutWidget(title='BrainFlow Plot', size=(800, 600))

        self._init_timeseries()
        print("here")

        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(self.update_speed_ms)

        # self.app.update()
        self.gui_thread = threading.Timer(self.update_speed_ms, self.update)
        self.gui_thread.start()

        QtGui.QApplication.instance().exec_()

    def _init_timeseries(self):
        self.plots = list()
        self.curves = list()
        for i in range(len(self.exg_channels)):
            p = self.win.addPlot(row=i, col=0)
            p.showAxis('left', False)
            p.setMenuEnabled('left', False)
            p.showAxis('bottom', False)
            p.setMenuEnabled('bottom', False)
            if i == 0:
                p.setTitle('TimeSeries Plot')
            self.plots.append(p)
            curve = p.plot()
            self.curves.append(curve)

    def update(self):
        # read brainbit and populate DataBorg
        data = self.eeg_board.read(self.num_points)
        # print("updating")
        for count, channel in enumerate(self.exg_channels):
            # plot timeseries
            DataFilter.detrend(data[channel], DetrendOperations.CONSTANT.value)
            DataFilter.perform_bandpass(data[channel], self.sampling_rate, 3.0, 45.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 48.0, 52.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            DataFilter.perform_bandstop(data[channel], self.sampling_rate, 58.0, 62.0, 2,
                                        FilterTypes.BUTTERWORTH.value, 0)
            self.curves[count].setData(data[channel].tolist())

        self.app.processEvents()
        # self.app.update()


if __name__ == "__main__":
    Main(duration_of_piece=200,
         continuous_line=True,
         speed=10,
         staves=0,
         pen=True)
