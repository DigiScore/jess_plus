import logging
from time import sleep

from nebula.nebula import Nebula


logging.basicConfig(level=logging.DEBUG)

test = Nebula()
test.main_loop()

while True:
    print(test.hivemind.mic_in,
          test.hivemind.move_rnn,
          test.hivemind.self_awareness,
          test.hivemind.eda)
    sleep(0.1)
