import logging
from random import random
import numpy as np
import pyaudio

#  import local methods
from nebula.hivemind import DataBorg


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
        while self.hivemind.running:

            # get amplitude from mic input
            data = np.frombuffer(self.stream.read(
                self.CHUNK,
                exception_on_overflow=False),
                dtype=np.int16)
            peak = np.average(np.abs(data)) * 2

            if peak > 1000:
                bars = "#" * int(50 * peak / 2 ** 16)
                logging.debug("MIC LISTENER: %05d %s" % (peak, bars))

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

        logging.info('quitting listener thread')

    def terminate(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()