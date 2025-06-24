import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import subprocess
import time
import threading
import numpy as np
import sounddevice as sd
import colorsys
import math

# ===== グローバル変数・定数 =====
angle = 0
current_track = ""
is_playing = False

canvas_size = 700
center = canvas_size // 2
radius_inner = 150
radius_outer = 300
N_BARS = 128

buffer = np.zeros(1024)
SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
DEVICE_INDEX = 0  # 環境に応じて変更
freqs = np.fft.rfftfreq(CHUNK_SIZE, 1 / SAMPLING_RATE)
FREQ_MIN = 40
FREQ_MAX = 15000
log_bins = np.logspace(np.log10(FREQ_MIN), np.log10(FREQ_MAX), N_BARS + 1)
angles = np.linspace(0, 2 * np.pi, N_BARS, endpoint=False)
hues = np.linspace(0, 1.0, N_BARS, endpoint=False)
colors = [colorsys.hsv_to_rgb(h, 1.0, 1.0) for h in hues]

# ===== Tkinter画面準備 =====
root = tk.Tk()
root.title("Jacket + Visualizer")
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, bg="black", highlightthickness=0)
canvas.pack()

# ===== あなたの元コードから関数をコピペ =====

def get_current_track_info():
    global is_playing
    script = '''
    tell application "Music"
        if it is running and player state is playing then
            set trackName to name of current track
            set artistName to artist of current track
            return "playing||" & trackName & "||" & artistName
        else
            return "stopped||"
        end if
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    parts = result.stdout.strip().split("||")

    if parts[0] == "playing":
        is_playing = True
        return parts[1], parts[2]
    else:
        is_playing = False
        return "", ""

def apply_circle_mask(img):
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

def fetch_album_art(track, artist):
    search_url = f"https://itunes.apple.com/search?term={track} {artist}&entity=song"
    try:
        response = requests.get(search_url, timeout=5)
        results = response.json().get("results", [])
        if results:
            img_url = results[0]["artworkUrl100"].replace("100x100", "600x600")
            img_data = requests.get(img_url).content
            img = Image.open(BytesIO(img_data)).resize((radius_inner*2, radius_inner*2), Image.LANCZOS).convert("RGBA")
            img = apply_circle_mask(img)
            return img
    except Exception as e:
        print("Artwork fetch error:", e)
    return None

def monitor_track():
    global current_track, img, tk_img
    while True:
        track, artist = get_current_track_info()
        if track and track != current_track:
            current_track = track
            new_img = fetch_album_art(track, artist)
            if new_img:
                img = new_img
        time.sleep(1)

def audio_callback(indata, frames, time, status):
    global buffer
    if status:
        print(status)
    buffer = np.mean(indata, axis=1)

# ===== 新たに波形＋回転ジャケット表示用update関数 =====
def update():
    global angle, tk_img, img

    canvas.delete("bars")  # 前回のバーを削除

    fft_data = np.abs(np.fft.rfft(buffer)) / CHUNK_SIZE
    seg_amps = []
    for i in range(N_BARS):
        idx = np.where((freqs >= log_bins[i]) & (freqs < log_bins[i+1]))[0]
        amp = np.mean(fft_data[idx]) if len(idx) > 0 else 1e-10
        log_amp = np.log10(amp + 1e-8)
        scaled = max(radius_inner, min(radius_outer, log_amp * 15 + radius_inner + 120))
        seg_amps.append(scaled)

    for theta, r, c in zip(angles, seg_amps, colors):
        x0 = center + radius_inner * math.cos(theta)
        y0 = center + radius_inner * math.sin(theta)
        x1 = center + r * math.cos(theta)
        y1 = center + r * math.sin(theta)
        rgb = tuple(int(255*x) for x in c)
        color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
        canvas.create_line(x0, y0, x1, y1, fill=color, width=3, tags="bars")

    if is_playing and img:
        angle = (angle - 1.5) % 360
        rotated = img.rotate(angle, resample=Image.BICUBIC)
        tk_img = ImageTk.PhotoImage(rotated)
        canvas.create_image(center, center, image=tk_img, tags="bars")
    else:
        if img:
            tk_img = ImageTk.PhotoImage(img)
            canvas.create_image(center, center, image=tk_img, tags="bars")

    root.after(30, update)

# ===== 初期画像設定 =====
img = Image.new("RGBA", (radius_inner*2, radius_inner*2), (0,0,0,255))
tk_img = ImageTk.PhotoImage(img)

# ===== サウンドデバイス開始 =====
stream = sd.InputStream(callback=audio_callback,
                channels=2,
                samplerate=SAMPLING_RATE,
                blocksize=CHUNK_SIZE,
                device=DEVICE_INDEX)
stream.start()

# ===== 監視スレッド開始 =====
threading.Thread(target=monitor_track, daemon=True).start()

# ===== メインループ開始 =====
update()
root.mainloop()

stream.stop()
