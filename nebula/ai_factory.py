import logging
import numpy as np
import torch
from random import random
from time import sleep

from nebula.hivemind import DataBorg
from nebula.models.pt_models import Hourglass


class NNetRework:
    def __init__(self,
                 name: str,
                 model: str,
                 in_feature: str):
        """
        Make an object  for each neural net in AI factory.

        Parameters
        ----------
        name
            Name of the NNet, must align with the name of the object.

        model
            Location of the ML model for this NNet.

        in_feature
            NNet input from DataBorg to use.
        """
        self.hivemind = DataBorg()
        self.name = name
        self.in_feature = in_feature

        state_dict = torch.load(model)
        n_ch_in = list(state_dict.values())[0].size()[1]
        n_ch_out = list(state_dict.values())[-2].size()[1]
        pt_model = Hourglass(n_ch_in, n_ch_out).double()
        pt_model.load_state_dict(state_dict)
        pt_model.eval()
        self.model = pt_model
        logging.info(f"{name} initialized")

    def make_prediction(self, in_val):
        """
        Make a prediction for this NNet.

        Parameters
        ----------
        in_val
            2D input value for this NNet
        """
        # Make prediction
        prediction = self.model(torch.tensor(in_val[np.newaxis, :, :]))
        prediction = np.squeeze(prediction.detach().numpy(), axis=0)
        setattr(self.hivemind, f'{self.name}_2D', prediction)

        # Get average from prediction and save to data dict
        individual_val = np.mean(prediction)
        setattr(self.hivemind, self.name, individual_val)
        logging.debug(f"NNet {self.name} in: {in_val} predicted {individual_val}")


class AIFactoryRework:
    def __init__(self, speed: float = 1):
        """
        Builds the individual neural nets that constitute the AI factory.
        """
        print('Building the AI Factory...')

        self.net_logging = False
        self.hivemind = DataBorg()
        self.global_speed = speed

        # Instantiate nets as objects and make models
        logging.info('NNetRework1 - EEG to flow initialization')
        self.eeg2flow = NNetRework(name="eeg2flow",
                                   model='nebula/models/eeg2flow.pt',
                                   in_feature='eeg_buffer')
        logging.info('NNetRework2 - Flow to core initialization')
        self.flow2core = NNetRework(name="flow2core",
                                    model='nebula/models/flow2core.pt',
                                    in_feature='eeg2flow_2d')
        logging.info('NNetRework3 - Core to flow initialization')
        self.core2flow = NNetRework(name="core2flow",
                                    model='nebula/models/core2flow.pt',
                                    in_feature='current_robot_x_y')
        logging.info('NNetRework4 - Audio to core initialization')
        self.audio2core = NNetRework(name="audio2core",
                                     model='nebula/models/audio2core.pt',
                                     in_feature='audio_buffer')
        logging.info('NNetRework5 - Audio to flow initialization')
        self.audio2flow = NNetRework(name="audio2flow",
                                     model='nebula/models/audio2flow.pt',
                                     in_feature='audio_buffer')
        logging.info('NNetRework6 - Flow to audio initialization')
        self.flow2audio = NNetRework(name="flow2audio",
                                     model='nebula/models/flow2audio.pt',
                                     in_feature='eeg2flow_2d')
        logging.info('NNetRework7 - EDA to flow initialization')
        self.eda2flow = NNetRework(name="eda2flow",
                                   model='nebula/models/eda2flow.pt',
                                   in_feature='eda_buffer')

        self.netlist = [self.eeg2flow,
                        self.flow2core,
                        self.core2flow,
                        self.audio2core,
                        self.audio2flow,
                        self.flow2audio,
                        self.eda2flow]
        print("AI factory initialized")

    def make_data(self):
        """
        Makes a prediction for each NNet in the AI factory while hivemind is
        running.
        """
        while self.hivemind.running:
            for net in self.netlist:
                in_val = self.get_seed(net)
                net.make_prediction(in_val)

            # Create a stream of random poetry
            rnd = random()
            self.hivemind.rnd_poetry = rnd

            sleep(0.1)  # 10 Hz

    def get_seed(self, net_name):
        """
        Get the seed data for a given NNet.
        """
        seed_source = net_name.in_feature
        seed = getattr(self.hivemind, seed_source)
        return seed

    def quit(self):
        """
        Quit the loop like a grown up.
        """
        self.hivemind.running = False


if __name__ == "__main__":
    from hivemind import DataBorg
    test = AIFactoryRework()
    print(test.hivemind.eeg2flow)
    test.make_data()
    print(test.hivemind.eeg2flow)


# 1. Live EEG -> predicted flow

# 2. Predicted flow from EEG -> core (for current_nnet_x_y_z into current_robot_x_y_z)

# 3. Robot position (current_robot_x_y) -> predicted flow

# 4. Live sound (amplitude of envelope) -> core (for current_nnet_x_y_z into current_robot_x_y_z)

# 5. Live sound (amplitude of envelope) -> predicted flow

# 6. Predicted flow from EEG -> sound (amplitude of envelope)

# 7. Live EDA -> predicted flow
