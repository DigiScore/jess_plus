from modules.conducter import Conducter
from time import sleep
from random import random, randrange
import logging

logging.basicConfig(level=logging.INFO)

test = Conducter()

while True:
    arm_speed = randrange(20, 200)
    if test.drawbot:
        test.drawbot.speed(velocity=arm_speed,
                           acceleration=arm_speed)

    rnd = random()
    print(rnd)

    choice = randrange(7)

    match choice:
        case 0:
            sleep(1)
        case 1:
            test.repetition(rnd)
        case 2:
            test.offpage(rnd)
        case 3:
            test.continuous(rnd)
        case 4:
            test.wolff_inspiration(rnd)
        case 5:
            test.cardew_inspiration(rnd)
        case 6:
            test.high_energy_response()


