# [HARDWARE]
robot = True
eeg = False
eeg_graph = False

# [BITALINO]
baudrate = 100
channels = [0]
mac_address = "/dev/cu.BITalino-3F-AE"

# [DEBUG]
# debug = logging.INFO

# [STAFF]
staff_width = 20

# [STREAMING]
stream_list = ['mic_in',
               'rnd_poetry',
               'move_rnn',
               'affect_rnn',
               'self_awareness']

# todo - CRAIG if this is false then the "feeding" NNets need to be operting too
all_nets_predicting = True
