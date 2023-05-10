# [PLAY PARAMS]
viz = False
silence_listener = True
duration_of_piece = 300  # in sec
continuous_line = False  # set to `True` to not jump between points
speed = 5  # dynamic tempo of the all processes: 1 = slow, 10 = fast
staves = 0
temperature = 0

# [HARDWARE]
dobot_connected = False
xarm_connected = True
eeg_live = True
eda_live = False

# [DOBOT]
dobot1_port = 'COM4'  # 'COM4' or 'COM10' (Windows), '/dev/ttyACM0' (Linux)
dobot_verbose = False
x_extents = [160, 350]
y_extents = [-150, 150]
z_extents = [0, 150]
irregular_shape_extents = 50

# [XARM]
xarm1_port = '192.168.1.222'
xarm2_port = '192.168.1.223'
xarm_x_extents = [350, 600]
xarm_y_extents = [-250, 250]
xarm_z_extents = [90, 600]
xarm_ballet_x_extents = [400, 400]
xarm_ballet_y_extents = [-250, 250]
xarm_ballet_z_extents = [150, 400]
xarm_irregular_shape_extents = 50
xarm_fenced = True
xarm_multi_pen = True

# [BITALINO]
baudrate = 10
channels = [0]
mac_address = "98:D3:B1:FD:3D:1F"  # '/dev/cu.BITalino-3F-AE' (Linux)

# [STREAMING]
stream_list = ['rnd_poetry',
               'eeg2flow',
               'flow2core',
               'core2flow',
               'audio2core',
               'audio2flow',
               'flow2audio',
               'eda2flow']

# [DEBUG]
# debug = logging.INFO


"""
Notes:
To check available ports, run the following code:
    from serial.tools import list_ports

    available_ports = list_ports.comports()
    print(f'available ports: {[x.device for x in available_ports]}')

May need `sudo chmod 666 /dev/ttyACM0`
"""
