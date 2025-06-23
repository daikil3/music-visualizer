import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import subprocess
import time
import threading

# === グローバル変数 ===
angle = 0
current_track = ""
is_playing = False

canvas_size = 600

# 曲情報取得
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

# 円形マスクを作成して画像に適用
def apply_circle_mask(img):
    size = img.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img.putalpha(mask)
    return img

# === ジャケット画像を取得 ===
def fetch_album_art(track, artist):
    search_url = f"https://itunes.apple.com/search?term={track} {artist}&entity=song"
    response = requests.get(search_url)
    results = response.json()["results"]
    if results:
        img_url = results[0]["artworkUrl100"].replace("100x100", "600x600")
        img_data = requests.get(img_url).content
        img = Image.open(BytesIO(img_data)).resize((canvas_size, canvas_size), Image.LANCZOS).convert("RGBA")
        img = apply_circle_mask(img)
        return img
    return None

# === 回転処理 ===
def rotate_image():
    global angle, img, tk_img
    if is_playing:
        angle = (angle - 1.5) % 360
    rotated = img.rotate(angle, resample=Image.BICUBIC)
    tk_img = ImageTk.PhotoImage(rotated)
    canvas.itemconfig(img_item, image=tk_img)
    root.after(10, rotate_image)

# 画像表示
def show_artwork(img_url):
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).resize((400, 400))
    root = tk.Tk()
    root.title("Album Art")
    tk_img = ImageTk.PhotoImage(img)
    tk.Label(root, image=tk_img).pack()
    root.mainloop()

# === 曲変更を監視して画像を更新 ===
def monitor_track():
    global current_track, img
    while True:
        track, artist = get_current_track_info()
        if track and track != current_track:
            current_track = track
            new_img = fetch_album_art(track, artist)
            if new_img:
                img = new_img  # グローバルのimgを更新
        time.sleep(1)


# Tkinter画面の準備
root = tk.Tk()
root.title("Jacket")
canvas = tk.Canvas(root, width=canvas_size, height=canvas_size, highlightthickness=0)
canvas.pack()

# 最初に仮画像を表示
img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 255))
tk_img = ImageTk.PhotoImage(img)
img_item = canvas.create_image(canvas_size // 2, canvas_size // 2, image=tk_img, anchor="center")

# スレッドで監視開始
threading.Thread(target=monitor_track, daemon=True).start()

rotate_image()
root.mainloop()