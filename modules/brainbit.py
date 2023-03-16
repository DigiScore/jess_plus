from brainflow.board_shim import BoardShim, BrainFlowInputParams
from time import sleep
from random import random
import logging

from nebula.hivemind import DataBorg


class BrainbitReader:
    def __init__(self):
        # Establish all parameters for Brainflow
        self.params = BrainFlowInputParams()

        # Assign the BrainBit as the board
        self.params.board_id = 7

        # set it logging
        BoardShim.enable_dev_board_logger()
        logging.info('BrainBit reader ready')
        self.brain_bit = False

        # get dataclass
        self.hivemind = DataBorg()

    def start(self):
        # instantiate the board reading
        try:
            self.board = BoardShim(7,
                                   self.params)
            self.board_id = self.board.get_board_id()

            self.board.prepare_session()

            # board.start_stream () # use this for default options
            self.board.start_stream(450000) # removed 2
            logging.info('BrainBit stream started')
            self.brain_bit = True
        except:
            logging.info("BrainBit ALT started")

    def read(self, num_points):
        if self.brain_bit:
            raw_data = self.board.get_board_data()[1:5]
            parse_data = raw_data.tolist()

            if len(parse_data[0][0:1]) > 0:
                t2 = parse_data[0][0:1][0]
                t4 = parse_data[1][0:1][0]
                n1 = parse_data[2][0:1][0]
                n2 = parse_data[3][0:1][0]
                self.data = [t2,
                             t4,
                             n1,
                             n2]
            else:
                self.data = [0, 0, 0, 0]

        else:
            """get dummy data instead of Brainbit stream."""
            self.data = [random(),
                         random(),
                         random(),
                         random()
                         ]

        logging.debug(f"BrainBit data = {self.data}")
        self.hivemind.eeg = self.data
        return self.data

    def terminate(self):
        self.board.stop_stream()
        self.board.release_session()


