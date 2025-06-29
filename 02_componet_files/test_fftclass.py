import sounddevice as sd
import numpy as np

# === 設定 ===
SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0

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
        """現在のFFT結果を取得"""
        fft = np.abs(np.fft.rfft(self.buffer)) / self.chunk_size
        return fft

    def start(self):
        self.stream.start()

    def stop(self):
        self.stream.stop()

# === 使用例（Matplotlibは後から好きに差し替え可） ===
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation

    fft_source = RealTimeFFT(SAMPLING_RATE, CHUNK_SIZE, DEVICE_INDEX)
    fft_source.start()

    fig, ax = plt.subplots()
    x = np.fft.rfftfreq(CHUNK_SIZE, 1 / SAMPLING_RATE)
    line, = ax.plot(x, np.zeros_like(x))
    ax.set_ylim(0, 100)
    ax.set_xlim(0, 22050)

    def update(frame):
        fft_data = fft_source.get_fft()
        line.set_ydata(fft_data * 100)
        return line,

    ani = FuncAnimation(fig, update, interval=30, blit=True)
    plt.show()

    fft_source.stop()