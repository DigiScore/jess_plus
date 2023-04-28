from modules.conducter import Conducter
from time import sleep
from random import randrange, uniform
import logging
import config
from threading import Thread


test = Conducter()
test.drawbot.go_position_ready()
test.hivemind.running = True
test.drawbot.command_list_main_loop()


def main(mode=999):

    while True:
        rnd = uniform(0.1, 0.9)
        print(rnd)

        match mode:
            case 1:
                test.repetition(rnd)
            case 2:
                test.continuous(rnd)
            case 3:
                test.wolff_inspiration(rnd)
            case 4:
                test.cardew_inspiration(rnd)
            case 5:
                test.high_energy_response()
            case 999:

                choice = randrange(5)
                match choice:
                    case 0:
                        sleep(1)
                    case 1:
                        test.repetition(rnd)
                    case 2:
                        test.continuous(rnd)
                    case 3:
                        test.wolff_inspiration(rnd)
                    case 4:
                        test.cardew_inspiration(rnd)
                    case 5:
                        test.high_energy_response()

def interrupt():
    while True:
        rnd = randrange(10, 20)
        sleep(rnd)
        print("INTERRUPTING")
        test.hivemind.interrupt_clear = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)

    t1 = Thread(target=main, args=(999,))
    t2 = Thread(target=interrupt)

    t1.start()
    t2.start()
