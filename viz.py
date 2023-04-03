from threading import Thread
import tkinter as tk
import random
import time


CLOSE_WINDOW = False

class Visualiser():

    def __init__(self):
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.canvas = tk.Canvas(self.root, height=500, width=500)
        self.canvas.pack()
        self.centers = {
            'T3': [100, 250],
            'T4': [400, 250],
            'O1': [200, 350],
            'O2': [300, 350],
            'EDA': [250, 150]
        }
        self.colors = {
            'T3': '#ff6600',
            'T4': '#ff6600',
            'O1': '#ff6600',
            'O2': '#ff6600',
            'EDA': '#0099ff'
        }
        self.sizes = {
            'T3': 0.5,
            'T4': 0.5,
            'O1': 0.5,
            'O2': 0.5,
            'EDA': 0.5,
        }
        self.items = {}
        for ch in self.centers:
            items_xys = [self.centers[ch][0]-100*self.sizes[ch],
                         self.centers[ch][1]-100*self.sizes[ch],
                         self.centers[ch][0]+100*self.sizes[ch],
                         self.centers[ch][1]+100*self.sizes[ch]]
            self.items[ch] = self.canvas.create_oval(
                *items_xys, fill=self.colors[ch], outline=self.colors[ch])

        for ch in self.centers:
            self.canvas.create_text(
                self.centers[ch], text=ch, font=('Helvetica','15','bold'))
        self.window_closed = False

    def on_close(self):
        self.window_closed = True

    def callback(self):
        self.sizes = {
            'T3': random.random(),
            'T4': random.random(),
            'O1': random.random(),
            'O2': random.random(),
            'EDA': random.random(),
        }
        for ch in self.centers:
            items_xys = [self.centers[ch][0]-100*self.sizes[ch],
                         self.centers[ch][1]-100*self.sizes[ch],
                         self.centers[ch][0]+100*self.sizes[ch],
                         self.centers[ch][1]+100*self.sizes[ch]]
            self.canvas.coords(self.items[ch], *items_xys)

    def main_loop(self):
        print('Starting visualisation')
        t1 = Thread(target=self.make_viz)
        t1.start()

    def make_viz(self):
        # while self.hivemind.running:
        #     if time() >= self.endtime:
        #         break
        while True:
            self.root.update_idletasks()
            self.root.update()
            if self.window_closed is True:
                break
            self.callback()
            time.sleep(0.1)


if __name__ == "__main__":
    # from hivemind import DataBorg
    test = Visualiser()
    test.make_viz()
