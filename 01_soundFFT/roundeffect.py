import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # BlackHoleの番号に変更してください

GAIN = 3000

fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_ylim(0, 50)  # 振幅の範囲調整

# 角度はFFTの周波数binに対応
theta = np.linspace(0, 2 * np.pi, CHUNK_SIZE//2 + 1)
line, = ax.plot(theta, np.zeros_like(theta), lw=2)

buffer = np.zeros(CHUNK_SIZE)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.mean(indata, axis=1)

def update(frame):
    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE
    line.set_ydata(fft_data * GAIN)  # スケール調整
    return line,

stream = sd.InputStream(callback=audio_callback,
                        channels=2,
                        samplerate=SAMPLING_RATE,
                        blocksize=CHUNK_SIZE,
                        device=DEVICE_INDEX)
stream.start()

ani = FuncAnimation(fig, update, interval=30, blit=True)
plt.show()

stream.stop()
