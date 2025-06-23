import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # BlackHoleの番号に変更してください

fig, ax = plt.subplots()
x = np.arange(CHUNK_SIZE)
line, = ax.plot(x, np.zeros(CHUNK_SIZE))
ax.set_ylim(-1, 1)
ax.set_title("BlackHole入力波形確認")

buffer = np.zeros(CHUNK_SIZE)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = indata[:, 0]  # 左チャンネルだけ使う

def update(frame):
    line.set_ydata(buffer)
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
