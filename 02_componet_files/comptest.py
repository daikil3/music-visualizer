from realtime_fft import RealTimeFFT
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

def main():
    SAMPLING_RATE = 44100
    CHUNK_SIZE = 1024
    DEVICE_INDEX = 0

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

if __name__ == "__main__":
    main()