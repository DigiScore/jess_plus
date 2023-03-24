from nebula.nebula import Nebula
import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG)

test = Nebula()
test.main_loop()

while True:
    print(test.hivemind.mic_in,
          test.hivemind.move_rnn,
          test.hivemind.self_awareness)
    sleep(0.1)

