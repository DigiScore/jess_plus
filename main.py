# import python modules
import logging
from tkinter import *
from PIL import Image, ImageTk

import config
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
    def __init__(self):

        # logging for all modules
        logging.basicConfig(level=logging.INFO)

        # build initial dataclass fill with random numbers
        self.hivemind = DataBorg()
        logging.debug(f'Data dict initial values are = {self.hivemind}')

        # build UI
        self.root = Tk
        self.images = []
        self.canvas = Canvas(width=300, height=200)
        self.canvas.pack()

        self.build_UI()

        # init the AI factory (inherits AIFactory, Listener)
        nebula = Nebula(
            speed=config.speed
        )

        # init Conducter & Gesture management (controls Drawbot)
        robot1 = Conducter(
            port=config.robot1_port,
            continuous_line=config.continuous_line,
            speed=config.speed,
            staves=config.staves,
        )

        # start Nebula AI Factory here after affect starts data moving
        robot1.main_loop()
        nebula.main_loop()
        print('here')
        # self.root.mainloop()

    def build_UI(self):
        self.circleTL = self.make_circle(10, 10, 200, 100, fill='blue', alpha=0.5)
        self.circleTR = self.make_circle(60, 10, 200, 100, fill='blue', alpha=0.5)
        self.circleBL = self.make_circle(10, 60, 200, 100, fill='blue', alpha=0.5)
        self.circleBR = self.make_circle(60, 60, 200, 100, fill='blue', alpha=0.5)

    def make_circle(self, x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            fill = self.root.winfo_rgb(color=fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            self.images.append(ImageTk.PhotoImage(image))
            self.canvas.create_image(x1, y1, image=self.images[-1], anchor='nw')
        self.canvas.create_oval(x1, y1, x2, y2, **kwargs)


if __name__ == "__main__":
    Main()
