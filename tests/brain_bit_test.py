from brainflow.board_shim import BoardShim, BrainFlowInputParams
import logging
from time import sleep
from modules.brainbit import BrainbitReader

logging.basicConfig(level=logging.DEBUG)

bb = BrainbitReader()
bb.start()
while True:
    data = bb.read(255)
    print(data)
    sleep(1)
