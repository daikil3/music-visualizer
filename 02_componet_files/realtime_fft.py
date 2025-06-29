import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

"""BlackHole情報
0 BlackHole 2ch, Core Audio (2 in, 2 out)
> 1 MacBook Airのマイク, Core Audio (1 in, 0 out)
  2 MacBook Airのスピーカー, Core Audio (0 in, 2 out)
  3　iPhone.dkのマイク, Core Audio (1 in, 0 out)
  4 Microsoft Teams Audio, Core Audio (2 in, 2 out)
< 5 複数出力装置, Core Audio (0 in, 2 out)

"""

# === 音声FFTクラス ===
class RealTimeFFT:
    def __init__(self, samplerate=44100, chunk_size=1024, device=0):
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self.device = device
        self.buffer = np.zeros(chunk_size)
        self.stream = sd.InputStream(callback=self.audio_callback,
                                     channels=2,
                                     samplerate=self.samplerate,
                                     blocksize=self.chunk_size,
                                     device=self.device)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.buffer = np.mean(indata, axis=1)  # モノラル変換

    def get_fft(self):
        return np.abs(np.fft.rfft(self.buffer)) / self.chunk_size

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()
