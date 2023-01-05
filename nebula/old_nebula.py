"""
Embodied AI Engine Prototype AKA "Nebula".
This object takes a live signal (such as body tracking,
or real-time sound analysis) and generates a response that
aims to be felt as co-creative. The response is a flow of
neural network emissions data packaged as a dictionary,
and is gestural over time. This, when plugged into a responding
script (such as a sound generator, or QT graphics) gives
the impression of the AI creating in-the-moment with the
human in-the-loop.

© Craig Vear 2022
cvear@dmu.ac.uk

Dedicated to Fabrizio Poltronieri
"""

""""""
# install python libraries
from random import randrange
from time import time
import tensorflow as tf
from threading import Thread
import numpy as np
from random import random, getrandbits
from time import sleep


class NebulaDataEngine():
    """An AI engine that generates gestural thought trains.
    This is the soul of embodied musicking.

    args:
        speed: general tempo/ feel of Nebula's response (0.5 ~ moderate fast, 1 ~ moderato; 2 ~ presto)"""

    def __init__(self, speed=1):
        print('building engine server')
        self.interrupt_bang = False

        # todo - global speed should be linked to bpm
        self.global_speed = speed #/ 10
        self.rnd_stream = 0

        # make a default dict for the engine
        self.datadict = {'move_rnn': 0,
                         'affect_rnn': 0,
                         'move_affect_conv2': 0,
                         'affect_move_conv2': 0,
                         'master_output': 0,
                         'user_in': 0,
                         'rnd_poetry': 0,
                         'rhythm_rnn': 0,
                         'affect_net': 0,
                         'self_awareness': 0,
                         'affect_decision': 0,
                         'rhythm_rate': 0.1}

        # name list for nets
        self.netnames = ['move_rnn',
                         'affect_rnn',
                         'move_affect_conv2',
                         'affect_move_conv2',
                         'self_awareness',  # Net name for self-awareness
                         'master_output']  # input for self-awareness

        # names for affect listening
        self.affectnames = ['user_in',
                            'rnd_poetry',
                            'affect_net',
                            'self_awareness']

        self.rhythm_rate = 1
        self.affect_listen = 0

        # fill with random values
        self.dict_fill()
        print(self.datadict)

        # instantiate nets as objects and make  models
        print('MoveRNN initialization')
        self.move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_skeleton_data.nose.x.h5')
        print('AffectRNN initialization')
        self.affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_bitalino.h5')
        print('MoveAffectCONV2 initialization')
        self.move_affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')
        print('AffectMoveCONV2 initialization')
        self.affect_move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_affect-move.h5')
        print('MoveAffectCONV2 initialization')
        self.affect_perception = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')

        # logging on/off switches
        self.net_logging = False
        self.master_logging = False
        self.streaming_logging = False
        self.affect_logging = False

        # declares all threads
        t1 = Thread(target=self.make_data)
        t2 = Thread(target=self.affect)

        # assigns them all daemons
        t1.daemon = True

        # starts them all
        t1.start()
        t2.start()


    """
    # --------------------------------------------------
    #
    # prediction and rnd num gen zone
    #
    # --------------------------------------------------
    """

    def make_data(self):
        """makes a prediction for a given net and defined input var.
        this spins in its own rhythm making data.
        Do not disturb - it has its own life cycle"""

        while True:
            # calc rhythmic intensity based on self-awareness factor & global speed
            # NB - divide not *

            intensity = self.datadict.get('self_awareness')
            # print('////////////////////////   intensity = ', intensity)
            self.rhythm_rate = self.rhythm_rate / self.global_speed  #(self.rhythm_rate * intensity) / self.global_speed
            self.datadict['rhythm_rate'] = self.rhythm_rate

            # PATCH BOARD
            # get input vars from dict (NB not always self)
            in_val1 = self.get_in_val(0) # move RNN as input
            in_val2 = self.get_in_val(1) # affect RNN as input
            in_val3 = self.get_in_val(2) # move - affect as input
            in_val4 = self.get_in_val(1) # affect RNN as input

            # send in vals to net object for prediction
            pred1 = self.move_net.predict(in_val1)
            pred2 = self.affect_net.predict(in_val2)
            pred3 = self.move_affect_net.predict(in_val3)
            pred4 = self.affect_move_net.predict(in_val4)

            # special case for self awareness stream
            self_aware_input = self.get_in_val(5) # main movement as input
            self_aware_pred = self.affect_perception.predict(self_aware_input)

            if self.net_logging:
                print(f"  'move_rnn' in: {in_val1} predicted {pred1}")
                print(f"  'affect_rnn' in: {in_val2} predicted {pred2}")
                print(f"  move_affect_conv2' in: {in_val3} predicted {pred3}")
                print(f"  'affect_move_conv2' in: {in_val4} predicted {pred4}")
                print(f"  'self_awareness' in: {self_aware_input} predicted {self_aware_pred}")

            # put predictions back into the dicts and master
            self.put_pred(0, pred1)
            self.put_pred(1, pred2)
            self.put_pred(2, pred3)
            self.put_pred(3, pred4)
            self.put_pred(4, self_aware_pred)

            # outputs a stream of random poetry
            rnd_poetry = random()
            self.datadict['rnd_poetry'] = random()
            if self.streaming_logging:
                print(f'random poetry = {rnd_poetry}')

            sleep(self.rhythm_rate)

    # function to get input value for net prediction from dictionary
    def get_in_val(self, which_dict):
        # get the current value and reshape ready for input for prediction
        input_val = self.datadict.get(self.netnames[which_dict])
        input_val = np.reshape(input_val, (1, 1, 1))
        input_val = tf.convert_to_tensor(input_val,  np.float32)
        return input_val

    # function to put prediction value from net into dictionary
    def put_pred(self, which_dict, pred):
        # randomly chooses one of te 4 predicted outputs
        out_pred_val = pred[0][randrange(4)]
        if self.master_logging:
            print(f"out pred val == {out_pred_val},   master move output == {self.datadict['master_output']}")
        # save to data dict and master move out ONLY 1st data
        self.datadict[self.netnames[which_dict]] = out_pred_val
        self.datadict['master_output'] = out_pred_val

    # fills the dictionary with rnd values for each key of data dictionary
    def dict_fill(self):
        for key in self.datadict.keys():
            rnd = random()
            self.datadict[key] = rnd

    """
    # --------------------------------------------------
    #
    # affect and streaming methods
    #
    # --------------------------------------------------
    """

    def affect(self):
        """define which feed to listen to, and duration
        and a course of affect response.
        This is defined by the master output."""
        # little val for emission control avoiding repeated vals
        self.old_val = 0

        # daddy cycle
        while True:
            if self.affect_logging:
                print('\t\t\t\t\t\t\t\t=========HIYA - DADDY cycle===========')

            # flag for breaking on big affect signal
            self.interrupt_bang = True

            # calc master cycle before a change
            master_cycle = randrange(6, 26) # * self.global_speed
            loop_end = time() + master_cycle

            if self.affect_logging:
                print(f"                 interrupt_listener: started! sleeping now for {master_cycle}...")

            # refill the dicts
            self.dict_fill()

            # child cycle - waiting for interrupt  from master clock
            while time() < loop_end:
                if self.affect_logging:
                        print('\t\t\t\t\t\t\t\t=========Hello - child cycle 1 ===========')

                # if a major break out then go to Daddy cycle
                if not self.interrupt_bang:
                    break

                # randomly pick an input stream for this cycle
                rnd = randrange(4)
                self.rnd_stream = self.affectnames[rnd]
                self.datadict['affect_decision'] = rnd
                print(self.rnd_stream)
                if self.affect_logging:
                    print(self.rnd_stream)

                # hold this stream for 1-4 secs, unless interrupt bang
                end_time = time() + (randrange(1000, 4000) / 1000)
                if self.affect_logging:
                    print('end time = ', end_time)

                # baby cycle 2 - own time loops
                while time() < end_time:
                    # get current mic level
                    peak = self.datadict["user_in"]
                    # print('mic level = ', peak)

                    if self.affect_logging:
                        print('\t\t\t\t\t\t\t\t=========Hello - baby cycle 2 ===========')

                    # go get the current value from dict
                    affect_listen = self.datadict[self.rnd_stream]
                    if self.affect_logging:
                        print('current value =', affect_listen)

                    # make the master output the current value of the stream
                    self.datadict['master_output'] = affect_listen
                    if self.master_logging:
                        print(f'\t\t ==============  master move output = {affect_listen}')

                    # emit at various points in the affect cycle
                    # might make a sound emission
                    # todo - add percentage here
                    # if getrandbits(1) == 1:
                        # print('emmission bang A')
                    self.emitter(affect_listen)
                    # else:
                        # print('no emmission bang A')

                    # calc affect on behaviour
                    # if input stream is LOUD then smash a random fill and break out to Daddy cycle...
                    if peak > 20000:
                        if self.affect_logging:
                            print('interrupt > HIGH !!!!!!!!!')

                        # A - refill dict with random
                        self.dict_fill()

                        # emit at various points in the affect cycle
                        self.emitter(affect_listen)

                        # B - jumps out of this loop into daddy
                        self.interrupt_bang = False
                        if self.affect_logging:
                            print('interrupt bang = ', self.interrupt_bang)

                        # C break out of this loop, and next (cos of flag)
                        break

                    # if middle loud fill dict with random, all processes norm
                    elif 3000 < peak < 19999:
                        if self.affect_logging:
                            print('interrupt MIDDLE -----------')
                            print('interrupt bang = ', self.interrupt_bang)

                        # emit at various points in the affect cycle
                        # might make a sound emission
                        # if getrandbits(1) == 1:
                            # print('emmission bang B')
                        self.emitter(affect_listen)
                        # else:
                            # print('no emmission bang B')

                        # refill dict with random
                        self.dict_fill()

                        # jumps out of current local loop, but not main one
                        break

                    # nothing happens here
                    elif peak <= 3000:
                        pass
                        # if self.affect_logging:
                        #     print('interrupt LOW_______________')
                        #     print('interrupt bang = ', self.interrupt_bang)

                    # and wait for a cycle
                    sleep(self.rhythm_rate)

    def emitter(self, incoming_affect_listen):
        if incoming_affect_listen != self.old_val:
            self.ai_signal.ai_str.emit(str(self.datadict))
            #print('//////////////////                   EMITTING and making sound')

            # # make sound/ move robot?
            # self.soundbot.make_sound(incoming_affect_listen, self.rhythm_rate)
            # send make sound signal to piano
            self.piano.note_to_play(incoming_affect_listen, self.rhythm_rate)

        self.old_val = incoming_affect_listen

    # parses the incoming dictionary and vars from the client
    def parse_got_dict(self, got_dict):
        self.datadict['user_in'] = got_dict.mic_level

        # user change the overall speed of the engine
        self.global_speed = got_dict.speed

        # user change tempo of outputs and parsing
        self.rhythm_rate = got_dict.baudrate

    def quit(self):
        self.running = False

