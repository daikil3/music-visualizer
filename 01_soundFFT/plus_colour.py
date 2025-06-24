import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import colorsys

SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # BlackHoleなどの仮想入力デバイス番号に合わせて変更
N_BARS = 64

# 極座標プロット準備
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_ylim(0, 100)
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)

angles = np.linspace(0, 2 * np.pi, N_BARS, endpoint=False)
width = (2 * np.pi) / N_BARS * 0.9
bars = ax.bar(angles, np.zeros(N_BARS), width=width, bottom=0.0)

# 各バーに色相ベースのカラーを割り当てる
hues = np.linspace(0, 1.0, N_BARS, endpoint=False)
colors = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
colors = [(r, g, b) for r, g, b in colors]  # 0-1 RGB（Matplotlib用）

for bar, color in zip(bars, colors):
    bar.set_facecolor(color)

buffer = np.zeros(CHUNK_SIZE)
freqs = np.fft.rfftfreq(CHUNK_SIZE, 1/SAMPLING_RATE)
log_min_freq = 20
log_max_freq = 20000
log_bins = np.logspace(np.log10(log_min_freq), np.log10(log_max_freq), N_BARS + 1)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.mean(indata, axis=1)

def update(frame):
    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE
    seg_amps = []

    for i in range(N_BARS):
        idx = np.where((freqs >= log_bins[i]) & (freqs < log_bins[i+1]))[0]
        amp = np.mean(fft_data[idx]) if len(idx) > 0 else 0
        seg_amps.append(amp)

    seg_amps = np.array(seg_amps) * 50000  # ゲイン調整
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
