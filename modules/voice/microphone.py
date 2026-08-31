import queue

import numpy as np
import sounddevice as sd


class MicrophoneStream:

    def __init__(
        self,
        sample_rate=16000,
        block_size=8000,
        gain=1.0
    ):

        self.sample_rate = sample_rate
        self.block_size = block_size
        self.gain = gain

        self.audio_queue = queue.Queue()

        self.stream = None

    def _callback(
        self,
        indata,
        frames,
        time,
        status
    ):

        if status:
            print(
                f"Micrófono: {status}"
            )

        data = np.frombuffer(
            bytes(indata),
            dtype=np.int16
        ).astype(np.float32)

        data *= self.gain

        data = np.clip(
            data,
            -32768,
            32767
        ).astype(np.int16)

        self.audio_queue.put(
            data.tobytes()
        )

    def start(self):

        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            dtype="int16",
            channels=1,
            callback=self._callback
        )

        self.stream.start()

    def read(self, timeout=0.5):

        try:

            return self.audio_queue.get(
                timeout=timeout
            )

        except queue.Empty:

            return None

    def stop(self):

        if self.stream is not None:

            self.stream.stop()
            self.stream.close()

            self.stream = None