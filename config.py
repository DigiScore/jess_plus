# [HARDWARE]
robot = True
eeg_live = False
eda_live = False

"""
to check available ports run the following code:
from serial.tools import list_ports

available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')

may need 
sudo chmod 666 /dev/ttyACM0
"""

robot1_port = 'COM4' # '/dev/ttyACM0'
robot2_port = '/dev/ttyXXXX'

# play params
duration_of_piece = 3600
continuous_line = False
speed = 5
staves = 0
temperature = 0

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
