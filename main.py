# import python modules
import logging
from tkinter import *
from PIL import Image, ImageTk

import config
# import project modules
from modules.conducter import Conducter
from nebula.nebula import Nebula
from nebula.hivemind import DataBorg


import tkinter as tk
import time


class Visualiser:

    def __init__(self):
        # build initial dataclass fill with random numbers
        self.hivemind = DataBorg()

        # build UI
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = tk.Canvas(self.root, height=500, width=500)
        self.canvas.pack()

        # assign location points and colors for visuals
        self.centers = {
            'T3': [100, 250],
            'T4': [400, 250],
            'O1': [190, 350],
            'O2': [310, 350],
            'EDA': [250, 150]
        }
        self.colors = {
            'T3': '#ff6600',
            'T4': '#ff6600',
            'O1': '#ff6600',
            'O2': '#ff6600',
            'EDA': '#0099ff'
        }

        # assign initial sizes of the circles (between 0 and 1)
        self.sizes = {
            'T3': 0.5,
            'T4': 0.5,
            'O1': 0.5,
            'O2': 0.5,
            'EDA': 0.5,
        }

        # build graphics
        self.items = {}
        for ch in self.centers:
            items_xys = [self.centers[ch][0]-100*self.sizes[ch],
                         self.centers[ch][1]-100*self.sizes[ch],
                         self.centers[ch][0]+100*self.sizes[ch],
                         self.centers[ch][1]+100*self.sizes[ch]]
            self.items[ch] = self.canvas.create_oval(
                *items_xys, fill=self.colors[ch], outline=self.colors[ch])

        # add labels
        for ch in self.centers:
            self.canvas.create_text(
                self.centers[ch], text=ch, font=('Helvetica', '15', 'bold'))

        self.window_closed = False

    def on_close(self):
        """
        Callback function for when the window is closed.
        """
        self.window_closed = True

    def callback(self):
        """
        Callback function for updating the circle sizes based on the
        hivemind data.
        """
        self.sizes['T3'] = self.hivemind.eeg_buffer[0][-10:].mean()
        self.sizes['T4'] = self.hivemind.eeg_buffer[1][-10:].mean()
        self.sizes['O1'] = self.hivemind.eeg_buffer[2][-10:].mean()
        self.sizes['O2'] = self.hivemind.eeg_buffer[3][-10:].mean()
        self.sizes['EDA'] = self.hivemind.eda_buffer[0][-10:].mean()
        for ch in self.centers:
            items_xys = [self.centers[ch][0]-100*self.sizes[ch],
                         self.centers[ch][1]-100*self.sizes[ch],
                         self.centers[ch][0]+100*self.sizes[ch],
                         self.centers[ch][1]+100*self.sizes[ch]]
            self.canvas.coords(self.items[ch], *items_xys)

    def make_viz(self):
        """
        Loop to update the window content at 10 Hz.
        """
        while self.hivemind.running:
            self.root.update_idletasks()
            self.root.update()
            if self.window_closed is True:
                self.root.destroy()
                break
            self.callback()

            # print(f'self.hivemind.eeg_buffer = {self.hivemind.eeg_buffer}')

            time.sleep(0.1)


class Main(Visualiser):
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
        Visualiser.__init__(self)
        # logging for all modules
        logging.basicConfig(level=logging.WARNING)

        # build initial dataclass fill with random numbers
        # self.hivemind = DataBorg()
        # logging.debug(f'Data dict initial values are = {self.hivemind}')

        # build UI
        self.root = Tk
        self.images = []
        self.canvas = Canvas(width=300, height=200)
        self.canvas.pack()

        # self.build_UI()

        # init the AI factory (inherits AIFactory, Listener)
        nebula = Nebula(
            speed=config.speed
        )

        # init Conducter & Gesture management (controls Drawbot)
        robot1 = Conducter(
            continuous_line=config.continuous_line,
            speed=config.speed,
            staves=config.staves,
        )

        # start Nebula AI Factory here after affect starts data moving
        robot1.main_loop()
        nebula.main_loop()
        print('here')
        # self.root.mainloop()

    # def build_UI(self):
    #     self.circleTL = self.make_circle(10, 10, 200, 100, fill='blue', alpha=0.5)
    #     self.circleTR = self.make_circle(60, 10, 200, 100, fill='blue', alpha=0.5)
    #     self.circleBL = self.make_circle(10, 60, 200, 100, fill='blue', alpha=0.5)
    #     self.circleBR = self.make_circle(60, 60, 200, 100, fill='blue', alpha=0.5)
    #
    # def make_circle(self, x1, y1, x2, y2, **kwargs):
    #     if 'alpha' in kwargs:
    #         alpha = int(kwargs.pop('alpha') * 255)
    #         fill = kwargs.pop('fill')
    #         fill = self.root.winfo_rgb(color=fill) + (alpha,)
    #         image = Image.new('RGBA', (x2-x1, y2-y1), fill)
    #         self.images.append(ImageTk.PhotoImage(image))
    #         self.canvas.create_image(x1, y1, image=self.images[-1], anchor='nw')
    #     self.canvas.create_oval(x1, y1, x2, y2, **kwargs)

        # v = Visualiser()
        self.make_viz()
        # v.make_viz()


if __name__ == "__main__":
    Main()
