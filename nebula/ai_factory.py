# install python modules
import logging
from random import random, randrange
import tensorflow as tf
import numpy as np
from time import sleep

# install local modules
from nebula.nebula_dataclass import DataBorg
import config

# todo JOHANN's script


class NNet:
    def __init__(self,
                 name: str,
                 model: str,
                 nnet_feed: str,
                 live_feed: str = None,
                 ):
        """Makes an object  for each neural net in AI factory.
        Args:
            name: name of NNet - must align to name of object
            model: location of ML model for this NNet
            nnet_feed: NNet output value from DataBorg to use as input value
            live_feed: Human input value from DataBorg to use as input value
            """
        self.hivemind = DataBorg()
        self.name = name
        self.nnet_feed = nnet_feed
        self.live_feed = live_feed
        self.which_feed = "net"

        self.model = tf.keras.models.load_model(model)
        print(f"{name} initialized")

    def make_prediction(self, in_val):
        """Makes a prediction for this NNet.
        Args:
            in_val: 1D input value for this NNet might be feedback or live input"""
        # make prediction
        prediction = self.model.predict(in_val, verbose=0)

        # get random variable from prediction and save to data dict
        individual_val = prediction[0][randrange(4)]
        setattr(self.hivemind, self.name, individual_val)
        logging.debug(f"NNet {self.name} in: {in_val} predicted {individual_val}")

class AIFactory:
    def __init__(self,
                 speed: float = 1,
                 ):
        """Builds the individual neural nets that constitute the AI factory.
        This will need modifying if and when a new AI factory design is implemented.
        NB - the list of netnames will also need updating"""

        print('Building the AI Factory')

        self.net_logging = False
        self.hivemind = DataBorg()
        self.global_speed = speed
        self.running = True

        # instantiate nets as objects and make models
        print('NNet1 - MoveRNN initialization')
        self.move_rnn = NNet(name="move_rnn",
                             model='nebula/models/EMR-full-sept-2021_RNN_skeleton_data.nose.x.h5',
                             nnet_feed='move_rnn',
                             live_feed=None,
                             )

        print('NNet2 - AffectRNN initialization')
        self.affect_rnn = NNet(name="affect_rnn",
                             model='nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5',
                             nnet_feed='affect_rnn',
                             live_feed=None,
                             )

        print('NNet3- MoveAffectCONV2 initialization')
        self.move_affect_conv2 = NNet(name="move_affect_conv2",
                             model='nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5',
                             nnet_feed='move_affect_conv2',
                             live_feed=None,
                             )

        print('NNet4 - AffectMoveCONV2 initialization')
        self.affect_move_conv2 = NNet(name="affect_move_conv2",
                                      model='nebula/models/EMR-full-sept-2021_conv2D_affect-move.h5',
                                      nnet_feed='affect_rnn',
                                      live_feed=None,
                                      )

        print('NNet5 - self_awareness initialization')
        self.self_awareness = NNet(name="self_awareness",
                             model='nebula/models/EMR-full-sept-2021_conv2D_move-affect.h5',
                             nnet_feed='master_stream',
                             live_feed=None,
                             )

        self.netlist = [self.move_rnn,
                        self.affect_rnn,
                        self.move_affect_conv2,
                        self.affect_move_conv2,
                        self.self_awareness
                        ]

    def make_data(self):
        """Makes a prediction for each NNet in the AI factory.

        Do not disturb - it has its own life cycle"""

        while self.running:
            # get the first rhythm rate from the hivemind
            # todo CRAIG - need to sort our global speed/ stretch
            rhythm_rate = self.hivemind.rhythm_rate

            # make a prediction for each of the NNets in the factory
            if config.all_nets_predicting:
                for net in self.netlist:
                    in_val = self.get_seed(net)
                    net.make_prediction(in_val)

            # or just the current one
            else:
                current_stream = self.hivemind.thought_train_stream
                for net in self.netlist:
                    if net.name == current_stream:
                        in_val = self.get_seed(net)
                        net.make_prediction(in_val)

            # creates a stream of random poetry
            rnd = random()
            self.hivemind.rnd_poetry = rnd

            sleep(rhythm_rate/ 10)

    def get_seed(self, net_name):
        """gets the seed data for a given NNet"""
        which_feed = net_name.which_feed
        if which_feed == "net":
            seed_source = net_name.nnet_feed
            seed = getattr(self.hivemind, seed_source)
        else:
            seed_source = net_name.live_feed
            seed = getattr(self.hivemind, seed_source)
        return self.get_in_val(seed)

    def get_in_val(self, input_val):
        """get the current value and reshape ready for input for prediction"""
        input_val = np.reshape(input_val, (1, 1, 1))
        input_val = tf.convert_to_tensor(input_val, np.float32)
        return input_val

    def quit(self):
        """Quit the loop like a grown up"""
        self.running = False

if __name__ == "__main__":
    from nebula_dataclass import DataBorg
    test = AIFactory()
    print(test.hivemind.move_rnn)
    test.make_data()
    print(test.hivemind.move_rnn)

