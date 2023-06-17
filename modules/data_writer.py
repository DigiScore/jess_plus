import json
import logging
import numpy as np
import os
from datetime import datetime
from scipy import signal
from threading import Thread
from time import sleep

from nebula.hivemind import DataBorg


class DataWriter:

    def __init__(self):
        self.hivemind = DataBorg()
        self.data_file = open(f"data/{self.hivemind.session_date}.json", "a")
        self.data_file.write("[")

    def json_update(self):
        """
        Write a hiveming tic in the json file.
        """
        json_dict = {
            "date": datetime.now().isoformat(),
            "master_stream": self.hivemind.thought_train_stream,
            "mic_in": self.hivemind.mic_in,
            "rnd_poetry": self.hivemind.rnd_poetry,
            "eeg2flow": self.hivemind.eeg2flow,
            "flow2core": self.hivemind.flow2core,
            "core2flow": self.hivemind.core2flow,
            "audio2core": self.hivemind.audio2core,
            "audio2flow": self.hivemind.audio2flow,
            "flow2audio": self.hivemind.flow2audio,
            "eda2flow": self.hivemind.eda2flow,
            "current_robot_x_y_z": {
                "x": self.hivemind.current_robot_x_y_z[0],
                "y": self.hivemind.current_robot_x_y_z[1],
                "z": self.hivemind.current_robot_x_y_z[2]
            }

        }
        json_object = json.dumps(json_dict)
        self.data_file.write(json_object)
        self.data_file.write(',\n')

    def terminate_data_writter(self):
        """
        Terminate the json writer and close file.
        """
        self.data_file.seek(self.data_file.tell() - 3, os.SEEK_SET)
        self.data_file.truncate()  # remove ",\n"
        self.data_file.write("]")
        self.data_file.close()
        f, t, Sxx = signal.spectrogram(self.hivemind.audio_buffer_raw, 44100)
        np.savetxt(f'data/{self.hivemind.session_date}.csv',
                   Sxx.transpose(), delimiter=',')

    def main_loop(self):
        """
        Start the main thread for the writing manager.
        """
        writer_thread = Thread(target=self.writing_manager)
        writer_thread.start()

    def writing_manager(self):
        """
        Write realtime data from hivemind.
        """
        while self.hivemind.running:
            self.json_update()
            sleep(0.1)
        logging.info("quitting data writer thread")
        self.terminate_data_writter()
