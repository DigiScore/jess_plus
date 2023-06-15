import logging
from brainflow.board_shim import BoardIds, BoardShim, BrainFlowInputParams
from brainflow.board_shim import BrainFlowError
from random import random
from time import sleep


class BrainbitReader:
    def __init__(self):
        # Establish all parameters for Brainflow
        self.params = BrainFlowInputParams()

        # Assign the BrainBit as the board
        self.params.board_id = BoardIds.BRAINBIT_BOARD
        logging.debug(self.params.board_id)

        # Set it logging
        BoardShim.disable_board_logger()
        logging.info('BrainBit reader ready')
        self.brain_bit = False

    def start(self):
        # Instantiate the board reading
        started = False
        print("Starting BrainBit stream...")
        while not started:
            try:
                self.board = BoardShim(BoardIds.BRAINBIT_BOARD, self.params)
                self.board_id = self.board.get_board_id()

                self.board.prepare_session()

                self.board.start_stream()  # with default options
                print(f"BrainBit stream started")
                self.brain_bit = True
                started = True

            except BrainFlowError:
                print("Unable to prepare BrainBit streaming session")
                retry = input("Retry (y/N)? ")
                if retry.lower() != "y" and retry.lower() != "yes":
                    started = True

    def read(self, num_points):
        if self.brain_bit:
            raw_data = self.board.get_board_data()[1:5]
            parse_data = raw_data.tolist()

            if len(parse_data[0][0:1]) > 0:
                t3 = parse_data[0][0:1][0]
                t4 = parse_data[1][0:1][0]
                o1 = parse_data[2][0:1][0]
                o2 = parse_data[3][0:1][0]
                self.data = [t3, t4, o1, o2]
            else:
                self.data = [0, 0, 0, 0]

        else:
            # Get dummy data instead of Brainbit stream
            self.data = [random(), random(), random(), random()]

        logging.debug(f"BrainBit data = {self.data}")
        return self.data

    def terminate(self):
        if self.brain_bit:
            self.board.stop_stream()
            self.board.release_session()


if __name__ == "__main__":
    bb = BrainbitReader()
    bb.start()
    while True:
        data = bb.read(1)
        print(data)
        sleep(1)
