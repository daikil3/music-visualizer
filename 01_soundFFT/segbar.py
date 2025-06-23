import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # BlackHoleの番号

N_BARS = 64  # セグメント数（棒の本数）

fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_ylim(0, 100)

# 各セグメントの角度幅
angles = np.linspace(0, 2 * np.pi, N_BARS, endpoint=False)

bars = ax.bar(angles, np.zeros(N_BARS), width=(2 * np.pi) / N_BARS * 0.8, bottom=0.0)

buffer = np.zeros(CHUNK_SIZE)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.mean(indata, axis=1)

def update(frame):
    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE
    # N_BARSに分割した振幅を計算（平均などで）
    seg_size = len(fft_data) // N_BARS
    seg_amps = [np.mean(fft_data[i*seg_size:(i+1)*seg_size]) for i in range(N_BARS)]
    seg_amps = np.array(seg_amps) * 500000  # ゲイン調整

    for bar, amp in zip(bars, seg_amps):
        bar.set_height(amp)

    return bars

stream = sd.InputStream(callback=audio_callback,
                    channels=2,
                    samplerate=SAMPLING_RATE,
                        blocksize=CHUNK_SIZE,
            device=DEVICE_INDEX)
stream.start()

ani = FuncAnimation(fig, update, interval=30, blit=True)
plt.show()

stream.stop()
