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


# ====== 設定 ======
SAMPLING_RATE = 44100  # Hz
CHUNK_SIZE = 1024      # 一度に処理するサンプル数
DEVICE_INDEX = 0

# ====== グラフ初期化 ======
fig, ax = plt.subplots()
x = np.fft.rfftfreq(CHUNK_SIZE, 1 / SAMPLING_RATE)  # 周波数軸
line, = ax.plot(x, np.zeros_like(x))
ax.set_xlabel("Frequency [Hz]")
ax.set_ylabel("Amplitude")
ax.set_ylim(0, 100)
ax.set_xlim(0, 22050)  # Nyquist周波数まで

buffer = np.zeros(CHUNK_SIZE)  # 音声データのバッファ

# ====== オーディオコールバック関数 ======
def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    """
    # モノラルに変換（ステレオ対応）
    mono = np.mean(indata, axis=1)
    # FFT
    fft_data = np.abs(np.fft.rfft(mono)) / CHUNK_SIZE
    line.set_ydata(fft_data * 100)  # 倍率調整
    fig.canvas.draw()
    fig.canvas.flush_events()
    """
    buffer = np.mean(indata, axis=1)

def update(frame):
    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE
    line.set_ydata(fft_data * 100)
    return line,

# 入力ストリームを開始
stream = sd.InputStream(callback=audio_callback,
                        channels=2,
                        samplerate=SAMPLING_RATE,
                        blocksize=CHUNK_SIZE,
                        device=DEVICE_INDEX)
stream.start()

ani = FuncAnimation(fig, update, interval=30, blit=True)

plt.show()

stream.stop()

"""
# ====== メイン処理 ======
plt.ion()  # インタラクティブモード
stream = sd.InputStream(
    callback=audio_callback,
    channels=2,  # BlackHole は通常 2ch
    samplerate=SAMPLING_RATE,
    blocksize=CHUNK_SIZE,
    device=DEVICE_INDEX
)


with stream:
    print("録音中... Ctrl+C で停止")
    while True:
        plt.pause(0.01)
        """