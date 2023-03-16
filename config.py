# [HARDWARE]
robot = True
eeg_live = False
eda_live = False

duration_of_piece = 200

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
               'self_awareness',
               'eeg_single']

# todo - CRAIG if this is false then the "feeding" NNets need to be operting too
all_nets_predicting = True


# [DEV PARAMETERS]
temperature = 0

speed = 1