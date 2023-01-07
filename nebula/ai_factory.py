# install python modules
import logging
from random import random, randrange
import tensorflow as tf
import numpy as np
from time import sleep

# install Nebula modules
from nebula.nebula_dataclass import NebulaDataClass, Borg


class AIFactory:
    """Builds a factory of neural networks and manages the data flows."""

    def __init__(self,
                 speed: float = 1
                 ):
        print('Building the AI Factory')
        # todo - build as a class where user only inputs the list of nets required

        """Builds the individual neural nets that constitute the AI factory.
        This will need modifying if and when a new AI factory design is implemented.
        NB - the list of netnames will also need updating"""

        self.net_logging = False
        self.datadict = Borg()
        self.global_speed = speed
        self.running = True

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

        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

        # name list for nets that align to factory above
        self.netnames = ['move_rnn',
                         'affect_rnn',
                         'move_affect_conv2',
                         'affect_move_conv2',
                         'self_awareness',  # Net name for self-awareness
                         'master_output']  # input for self-awareness

        self.net_patch_board = 0

    def make_data(self):
        """Makes a prediction for a given net and defined input var.
        This spins in its own rhythm, making data and is dynamic
        to the "awareness" of interactivity.

        Do not disturb - it has its own life cycle"""

        # now spin the plate and do its own ting
        while self.running:
            # get the first rhythm rate from the datadict
            # rhythm_rate = getattr(self.datadict, 'rhythm_rate') # + self.global_speed
            rhythm_rate = self.datadict.rhythm_rate


            # PATCH BOARD - CROSS PLUGS NET OUTPUTS TO INPUTS
            # get input vars from dict (NB not always self)
            in_val1 = self.get_in_val(0)  # move RNN as input
            in_val2 = self.get_in_val(1)  # affect RNN as input
            in_val3 = self.get_in_val(2)  # move - affect as input
            in_val4 = self.get_in_val(1)  # affect RNN as input

            # send in vals to net object for prediction
            pred1 = self.move_net.predict(in_val1, verbose=0)
            pred2 = self.affect_net.predict(in_val2, verbose=0)
            pred3 = self.move_affect_net.predict(in_val3, verbose=0)
            pred4 = self.affect_move_net.predict(in_val4, verbose=0)

            # special case for self awareness stream
            self_aware_input = self.get_in_val(5)  # main movement as input
            self_aware_pred = self.affect_perception.predict(self_aware_input, verbose=0)

            # emits a stream of random poetry
            # setattr(self.datadict, 'rnd_poetry', random())
            self.datadict.rnd_poetry = random()

            logging.debug(f"  'move_rnn' in: {in_val1} predicted {pred1}")
            logging.debug(f"  'affect_rnn' in: {in_val2} predicted {pred2}")
            logging.debug(f"  move_affect_conv2' in: {in_val3} predicted {pred3}")
            logging.debug(f"  'affect_move_conv2' in: {in_val4} predicted {pred4}")
            logging.debug(f"  'self_awareness' in: {self_aware_input} predicted {self_aware_pred}")

            # put predictions back into the dicts and master
            self.put_pred(0, pred1)
            self.put_pred(1, pred2)
            self.put_pred(2, pred3)
            self.put_pred(3, pred4)
            self.put_pred(4, self_aware_pred)

            sleep(rhythm_rate)

    # function to get input value for net prediction from dictionary
    def get_in_val(self, which_dict):
        # get the current value and reshape ready for input for prediction
        input_val = getattr(self.datadict, self.netnames[which_dict])
        # print("input val", input_val)
        input_val = np.reshape(input_val, (1, 1, 1))
        input_val = tf.convert_to_tensor(input_val, np.float32)
        return input_val

    # function to put prediction value from net into dictionary
    def put_pred(self, which_dict, pred):
        # save full output list to master output field
        out_pred_val = pred[0]
        # setattr(self.datadict, 'master_output', out_pred_val)
        # print(f"master move output ==  {out_pred_val}")

        # get random variable and save to data dict
        individual_val = out_pred_val[randrange(4)]
        # setattr(self.datadict, self.netnames[which_dict], individual_val)
        this_dict = self.netnames[which_dict]
        self.datadict.this_dict = individual_val

    def quit(self):
        self.running = False

if __name__ == "__main__":
    test_data_dict = NebulaDataClass()
    test = AIFactory(test_data_dict)
    test.make_data()
