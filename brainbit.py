from brainflow.board_shim import BoardShim, BrainFlowInputParams
from time import sleep
from random import random


class BrainbitReader:
    def __init__(self):
        # Establish all parameters for Brainflow
        self.params = BrainFlowInputParams()

        # Assign the BrainBit as the board
        self.params.board_id = 7

        # set it logging
        BoardShim.enable_dev_board_logger()
        print('BrainBit reader ready')
        self.brain_bit = False

    def start(self):
        # instantiate the board reading
        try:
            self.board = BoardShim(self.params.board_id,
                                   self.params)

            self.board.prepare_session()

            # board.start_stream () # use this for default options
            self.board.start_stream(2) # removed 48000
            print('BrainBit stream started')
            self.brain_bit = True
        except:
            print("BrainBit ALT started")


    def read(self):
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
        return self.data

    def terminate(self):
        self.board.stop_stream()
        self.board.release_session()


if __name__ == "__main__":
    bb = BrainbitReader()
    bb.start()
    while True:
        data = bb.read()
        print(data)
        sleep(1)
