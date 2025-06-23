import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # BlackHoleのデバイス番号に合わせて変更してください
N_BARS = 64

fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_ylim(0, 100)

ax.set_theta_zero_location("N")  # 0°を上に
ax.set_theta_direction(-1)       # 時計回りに角度増加

angles = np.linspace(0, 2 * np.pi, N_BARS, endpoint=False)
width = (2 * np.pi) / N_BARS * 0.9
bars = ax.bar(angles, np.zeros(N_BARS), width=width, bottom=0.0)

buffer = np.zeros(CHUNK_SIZE)

# FFT周波数binの周波数配列
freqs = np.fft.rfftfreq(CHUNK_SIZE, 1/SAMPLING_RATE)

# 対数区間の境界をHzで定義（20Hz〜20kHzの範囲を想定）
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
        # 対数区間ごとのbinインデックスを取得
        idx = np.where((freqs >= log_bins[i]) & (freqs < log_bins[i+1]))[0]
        if len(idx) > 0:
            amp = np.mean(fft_data[idx])
        else:
            amp = 0
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
