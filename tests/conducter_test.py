from modules.conducter import Conducter
from time import sleep
from random import random, randrange

test = Conducter()

while True:
    rnd = random()
    print(rnd)
    # test.repetition(rnd)
    test.offpage(rnd)


    sleep(1)

