# install python modules
import logging
from random import random, randrange
import tensorflow as tf
import numpy as np
from time import sleep

# install Nebula modules
# from nebula.nebula_dataclass import DataBorg #NebulaDataClass
from nebula_dataclass import DataBorg


# todo JOHANN's script


class NNet:
    def __init__(self,
                 name: str,
                 model: str,
                 datadict: DataBorg,
                 nnet_feed: str,
                 live_feed: str = None,
                 ):
        """Makes an object with args for each neural net in AI factory.
        Args:
            name: name of NNet - must align to name of object
            model: location of ML model for this NNet
            datadict: the Borg data class used by this script
            nnet_feed: NNet output value from DataBorg to use as input value
            live_feed: Human input value from DataBorg to use as input value
            """

        self.name = name
        self.nnet_feed = nnet_feed
        self.live_feed = live_feed
        self.datadict = datadict
        self.which_feed = "net"

        self.model = tf.keras.models.load_model(model)
        print(f"{name} initialized")

    def predict(self, in_val):
        prediction = self.model.predict(in_val, verbose=0)
        setattr(self.datadict, self.name, prediction)
        logging.debug(f"NNet {self.name} in: {in_val} predicted {prediction}")

        return prediction


class AIFactory:
    """Builds a factory of neural networks and manages the data flows."""

    def __init__(self,
                 speed: float = 1,
                 # datadict=NebulaDataClass
                 ):
        print('Building the AI Factory')

        """Builds the individual neural nets that constitute the AI factory.
        This will need modifying if and when a new AI factory design is implemented.
        NB - the list of netnames will also need updating"""

        self.net_logging = False
        self.datadict = DataBorg()
        self.global_speed = speed
        self.running = True

        # instantiate nets as objects and make  models
        # print('MoveRNN initialization')
        # self.move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_skeleton_data.nose.x.h5')
        # print('AffectRNN initialization')
        # self.affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_bitalino.h5')
        # print('MoveAffectCONV2 initialization')
        # self.move_affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')
        # print('AffectMoveCONV2 initialization')
        # self.affect_move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_affect-move.h5')
        # print('MoveAffectCONV2 initialization')
        # self.affect_perception = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')

        print('MoveRNN initialization')
        self.move_net = NNet(name="move_net",
                             model='models/EMR-full-sept-2021_RNN_skeleton_data.nose.x.h5',
                             datadict=self.datadict,
                             nnet_feed='move_rnn',
                             live_feed=None,
                             )
        #
        #
        # print('AffectRNN initialization')
        # self.affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_RNN_bitalino.h5')
        # print('MoveAffectCONV2 initialization')
        # self.move_affect_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')
        # print('AffectMoveCONV2 initialization')
        # self.affect_move_net = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_affect-move.h5')
        # print('MoveAffectCONV2 initialization')
        # self.affect_perception = tf.keras.models.load_model('nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5')

        # tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

        # todo is this needed if we migrate all patching to the datadict/ borg
        # name list for nets that align to factory above
        self.netnames = ['move_rnn',
                         'affect_rnn',
                         'move_affect_conv2',
                         'affect_move_conv2',
                         'self_awareness',  # Net name for self-awareness
                         'master_output']  # input for self-awareness

        self.netlist = [self.move_net,
                        # self.affect_net,
                        # self.move_affect_net,
                        # self.affect_move_net,
                        # self.affect_perception
                        ]

        self.net_patch_board = 0

    def make_data(self):
        """Makes a prediction for a given net and defined input var.
        This spins in its own rhythm, making data and is dynamic
        to the "awareness" of interactivity.

        Do not disturb - it has its own life cycle"""

        # now spin the plate and do its own ting
        while self.running:
            # get the first rhythm rate from the datadict
            # todo CRAIG - need to sort our global speed/ stretch
            # rhythm_rate = getattr(self.datadict, 'rhythm_rate') # + self.global_speed
            rhythm_rate = self.datadict.rhythm_rate

            for net in self.netlist:
                which_feed = net.which_feed
                if which_feed == "net":
                    seed_source = net.nnet_feed
                    seed = getattr(self.datadict, seed_source)
                else:
                    seed_source = net.live_feed
                    seed = getattr(self.datadict, seed_source)
                print(f"which feed = {seed}")
                in_val = self.get_in_val(seed)
                print(f"in val = {in_val}")
                prediction = net.predict(in_val)

            #
            # # todo - Johann/ Craig - this should be made into a dictionary inside the datadict/ borg
            # # PATCH BOARD - CROSS PLUGS NET OUTPUTS TO INPUTS
            # # get input vars from dict (NB not always self)
            # in_val1 = self.get_in_val(0)  # move RNN as input
            # in_val2 = self.get_in_val(1)  # affect RNN as input
            # in_val3 = self.get_in_val(2)  # move - affect as input
            # in_val4 = self.get_in_val(1)  # affect RNN as input

            # # send in vals to net object for prediction
            # pred1 = self.move_net.predict(in_val1, verbose=0)
            # pred2 = self.affect_net.predict(in_val2, verbose=0)
            # pred3 = self.move_affect_net.predict(in_val3, verbose=0)
            # pred4 = self.affect_move_net.predict(in_val4, verbose=0)

            # # special case for self awareness stream
            # self_aware_input = self.get_in_val(5)  # main movement as input
            # self_aware_pred = self.affect_perception.predict(self_aware_input, verbose=0)

            # emits a stream of random poetry
            # setattr(self.datadict, 'rnd_poetry', random())
            self.datadict.rnd_poetry = random()
            #
            # logging.debug(f"  'move_rnn' in: {in_val1} predicted {pred1}")
            # logging.debug(f"  'affect_rnn' in: {in_val2} predicted {pred2}")
            # logging.debug(f"  move_affect_conv2' in: {in_val3} predicted {pred3}")
            # logging.debug(f"  'affect_move_conv2' in: {in_val4} predicted {pred4}")
            # logging.debug(f"  'self_awareness' in: {self_aware_input} predicted {self_aware_pred}")

            # todo - Johann/ Craig - this should be made into a dictionary inside the datadict/ borg
            # put predictions back into the dicts and master
            # self.put_pred(0, pred1)
            # self.put_pred(1, pred2)
            # self.put_pred(2, pred3)
            # self.put_pred(3, pred4)
            # self.put_pred(4, self_aware_pred)

            sleep(rhythm_rate)

    # function to get input value for net prediction from dictionary
    # def get_in_val(self, which_dict):
    #     # get the current value and reshape ready for input for prediction
    #     input_val = getattr(self.datadict, self.netnames[which_dict])
    #     # dict_name = self.netnames[which_dict]
    #     # input_val = self.datadict.dict_name
    #     # print("input val", input_val)
    #     input_val = np.reshape(input_val, (1, 1, 1))
    #     input_val = tf.convert_to_tensor(input_val, np.float32)
    #     return input_val
    def get_in_val(self, input_val):
        # get the current value and reshape ready for input for prediction
        # input_val = getattr(self.datadict, which_dict)
        # dict_name = self.netnames[which_dict]
        # input_val = self.datadict.dict_name
        # print("input val", input_val)
        input_val = np.reshape(input_val, (1, 1, 1))
        input_val = tf.convert_to_tensor(input_val, np.float32)
        return input_val


    # function to put prediction value from net into dictionary
    # def put_pred(self, which_dict, pred):
    #     # save full output list to master output field
    #     out_pred_val = pred[0]
    #     # setattr(self.datadict, 'master_output', out_pred_val)
    #     # print(f"master move output ==  {out_pred_val}")
    #
    #     # get random variable and save to data dict
    #     individual_val = out_pred_val[randrange(4)]
    #     setattr(self.datadict, self.netnames[which_dict], individual_val)
    #     # this_dict = self.netnames[which_dict]
    #     # self.datadict.this_dict = individual_val

    def quit(self):
        self.running = False

if __name__ == "__main__":
    from nebula_dataclass import DataBorg
    test = AIFactory()
    print(test.datadict.move_rnn)
    test.make_data()
    print(test.datadict.move_rnn)

