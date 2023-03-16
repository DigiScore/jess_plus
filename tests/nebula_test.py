from nebula.nebula import Nebula

test = Nebula()
test.main_loop()

while True:
    print(test.hivemind.mic_in,
          test.hivemind.move_rnn,
          test.hivemind.self_awareness)


