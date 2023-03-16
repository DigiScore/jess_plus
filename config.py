# [HARDWARE]
robot = True
eeg_live = False
eda_live = False

robot1_port = "/usb1"
robot2_port = "/usb2"

# play params
duration_of_piece = 200
continuous_line = False
speed = 5
staves = 0

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

all_nets_predicting = True

# [DEV PARAMETERS]
temperature = 0

speed = 1