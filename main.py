# import python modules
import logging

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
        self.canvas = tk.Canvas(self.root, height=600, width=500)
        self.canvas.pack()

        # assign location points and colors for visuals
        self.centers = {
            'T3': [100, 250],
            'T4': [400, 250],
            'O1': [190, 350],
            'O2': [310, 350],
            'EDA': [250, 150]
        }
        self.label_centre = [250, 500]
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

        # stream label
        label_xys = [self.label_centre[0]-150,
                     self.label_centre[1]-50,
                     self.label_centre[0]+150,
                     self.label_centre[1]+50]
        self.frame = self.canvas.create_rectangle(*label_xys, width=3)
        self.label = self.canvas.create_text(
            self.label_centre, text='STREAM', font=('Helvetica', '15', 'bold'))
        self.stream_mapping = {
               'mic_in': 'Microphone',
               'rnd_poetry': 'Poetry',
               'eeg2flow': 'Brain',
               'flow2core': 'Brain groove',
               'core2flow': 'Self awareness',
               'audio2core': 'Audio groove',
               'audio2flow': 'Audio flow',
               'flow2audio': 'Brain audio',
               'eda2flow': 'EDA'
        }

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
        new_label = 'Unknown'
        if self.hivemind.thought_train_stream in self.stream_mapping:
            new_label = self.stream_mapping[self.hivemind.thought_train_stream]
        self.canvas.itemconfigure(
            self.label, text=new_label)

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
        logging.basicConfig(level=logging.INFO)

        # init Conducter & Gesture management (controls Drawbot)
        robot1 = Conducter(
            speed=config.speed,
        )

        # init the AI factory (inherits AIFactory, Listener)
        nebula = Nebula(
            speed=config.speed
        )

        # start Nebula AI Factory here after affect starts data moving
        self.hivemind.running = True
        robot1.main_loop()
        nebula.main_loop()

        # start visualiser
        self.make_viz()


if __name__ == "__main__":
    Main()
