# import python modules
import logging

# import project modules
from modules.conducter import Conducter
from nebula.nebula import Nebula
from nebula.hivemind import DataBorg

class Main:
    """
    The main script to start the robot arm drawing digital score work.
    Affect calls the local interpreter for project specific functions.
    This communicates directly to the pydobot library.
    Nebula kick-starts the AI Factory for generating NNet data and affect flows.
    This script also controls the live mic audio analyser.
    Args:
        duration_of_piece: the duration in seconds of the drawing
        continuous_line: Bool: True = will not jump between points
        speed: int the dynamic tempo of the all processes. 1 = slow, 10 = fast
        pen: bool - True for pen, false for pencil
    """
    def __init__(self,
                 continuous_line: bool = True,
                 speed: int = 5,
                 staves: int = 1,
                 pen: bool = True):

        # logging for all modules
        logging.basicConfig(level=logging.INFO)

        # build initial dataclass fill with random numbers
        self.hivemind = DataBorg()
        logging.debug(f'Data dict initial values are = {self.hivemind}')

        # init the AI factory (inherits AIFactory, Listener)
        nebula = Nebula(
            speed=speed
        )

        # init Conducter & Gesture management (controls Drawbot)
        robot1 = Conducter(
            continuous_line=continuous_line,
            speed=speed,
            staves=staves,
            pen=pen,
        )

        # start Nebula AI Factory here after affect starts data moving
        robot1.main_loop()
        nebula.main_loop()

    def terminate(self):
        """Smart collapse of all threads and comms"""
        print('TERMINATING')
        self.hivemind.running = False
        # self.digibot.home()
        # self.digibot.close()
        # self.eeg_board.terminate()
        # self.eda.close()


if __name__ == "__main__":
    Main(
        continuous_line=False,
        speed=5,
        staves=0,
        pen=True
    )
