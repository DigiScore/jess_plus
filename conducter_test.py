from modules.conducter import Conducter
from time import sleep
from random import random, randrange
import logging
import config

def main(mode=999):

    test = Conducter()

    while True:
        rnd = random()
        print(rnd)
        arm_speed = randrange(20, 200)
        # test.drawbot.speed(
        #     velocity=arm_speed,
        #     acceleration=arm_speed
        # )

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(4)
