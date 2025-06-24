import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
import colorsys

# === パラメータ ===
SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0
N_BARS = 128
GAIN = 15
MIN_RADIUS = 50

FREQ_MIN = 400
FREQ_MAX = 15000
log_bins = np.logspace(np.log10(FREQ_MIN), np.log10(FREQ_MAX), N_BARS + 1)


# === プロット設定 ===
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.set_ylim(0, 100)
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.grid(False)
ax.set_xticks([])
ax.set_yticks([])

# === 色と角度の設定 ===
angles = np.linspace(0, 2 * np.pi, N_BARS, endpoint=False)
hues = np.linspace(0, 1.0, N_BARS, endpoint=False)
colors = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]
colors = [(r, g, b) for r, g, b in colors]

# === 初期バー ===
segments = [[(theta, MIN_RADIUS), (theta, MIN_RADIUS)] for theta in angles]
lc = LineCollection(segments, linewidths=3, colors=colors)
ax.add_collection(lc)

# === 音声入力準備 ===
buffer = np.zeros(CHUNK_SIZE)
freqs = np.fft.rfftfreq(CHUNK_SIZE, 1 / SAMPLING_RATE)
#log_bins = np.logspace(np.log10(20), np.log10(20000), N_BARS + 1)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.mean(indata, axis=1)

# === フレーム更新 ===
def update(frame):
    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE

    seg_amps = []
    for i in range(N_BARS):
        idx = np.where((freqs >= log_bins[i]) & (freqs < log_bins[i + 1]))[0]
        amp = np.mean(fft_data[idx]) if len(idx) > 0 else 1e-10
        # 対数スケーリングで視認性を確保
        log_amp = np.log10(amp + 1e-8)  # 小さな値でゼロ除け
        scaled = np.clip(log_amp * GAIN + MIN_RADIUS + 70, MIN_RADIUS, 100)  # 補正値 +20 は見えやすさ調整
        seg_amps.append(scaled)

    updated_segments = [[(theta, MIN_RADIUS), (theta, r)] for theta, r in zip(angles, seg_amps)]
    lc.set_segments(updated_segments)
    return (lc,)

# === ストリーム開始 ===
stream = sd.InputStream(callback=audio_callback,
                        channels=2,
                        samplerate=SAMPLING_RATE,
                        blocksize=CHUNK_SIZE,
                        device=DEVICE_INDEX)
stream.start()

ani = FuncAnimation(fig, update, interval=30, blit=True)
plt.show()
stream.stop()
