import logging
from random import random
import numpy as np
import pyaudio
from scipy import signal
from time import time

#  import local methods
from nebula.hivemind import DataBorg
import config


def buffer_scaler(in_feature, mins, maxs):
    in_feature = np.array(in_feature)
    mins = np.array(mins)[:, np.newaxis]
    maxs = np.array(maxs)[:, np.newaxis]
    in_feature = (in_feature - mins) / (maxs - mins)
    in_feature = in_feature.clip(0, 1)
    return in_feature


class Listener:
    def __init__(self):
        """
        controls audio listening by opening up a stream in Pyaudio.
        """
        print("starting listener")

        self.running = True
        self.connected = False
        self.logging = False

        # set up mic listening func
        self.CHUNK = 2**11
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        # plug into the hive mind data borg
        self.hivemind = DataBorg()

# set up mic listening funcs
        self.CHUNK = 2 ** 11
        self.RATE = 44100
        p = pyaudio.PyAudio()
        self.stream = p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  frames_per_buffer=self.CHUNK)


    def snd_listen(self):
        """Loop thread that listens to live sound and analyses amplitude.
        Normalises then stores this into the nebula dataclass for shared use."""

        print("Starting mic listening stream & thread")
        data_buffer = np.empty(0)

        # set silence listener to 10 seconds in future
        silence_timer = time() + 10
        first_minute = time() + 60

        # main loop
        while self.hivemind.running:

            # get amplitude from mic input
            data = np.frombuffer(self.stream.read(
                self.CHUNK,
                exception_on_overflow=False),
                dtype=np.int16)

            # make audio envelope buffer
            data_buffer = np.append(data_buffer, data)
            if len(data_buffer) > self.RATE*5:  # 5 sec buffer
                data_buffer = data_buffer[-(self.RATE*5):]
                hb_data = signal.hilbert(data_buffer)
                envolope = np.abs(hb_data)
                num = int(len(envolope)/self.RATE*10.0)
                envolope = signal.resample(envolope, num)[np.newaxis, :]
                envolope_norm = buffer_scaler(envolope,
                                              self.hivemind.audio_mins,
                                              self.hivemind.audio_maxs)
                self.hivemind.audio_buffer = envolope_norm

            peak = np.average(np.abs(data)) * 2

            if peak > 1000:
                bars = "#" * int(50 * peak / 2 ** 16)
                logging.info("MIC LISTENER: %05d %s" % (peak, bars))

                # reset the silence listener
                silence_timer = time() + 5   # 5 seconds ahead

            # normalise it for range 0.0 - 1.0
            normalised_peak = ((peak - 0) / (20000 - 0)) * (1 - 0) + 0
            if normalised_peak > 1.0:
                normalised_peak = 1.0

            # put normalised amplitude into Nebula's dictionary for use
            self.hivemind.mic_in = normalised_peak

            # if loud sound then 63% affect gesture manager
            if normalised_peak > 0.8:
                if random() > 0.63:
                    self.hivemind.interrupt_bang = False
                    self.hivemind.randomiser()
                    print("-----------------------------MICROPHONE INTERRUPT----------------------------")


            # check human musician induced ending (wait for 5 secs)
            if config.silence_listener:
                if time() > first_minute:
                    if time() >= silence_timer:
                        self.hivemind.running = False

        logging.info('quitting listener thread')
        self.terminate()

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
