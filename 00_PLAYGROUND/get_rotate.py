import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
import subprocess

# 曲情報取得
def get_current_track_info():
    script = '''
    tell application "Music"
        if it is running and player state is playing then
            set trackName to name of current track
            set artistName to artist of current track
            return trackName & "||" & artistName
        else
            return "||"
        end if
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip().split("||")

# ジャケットURL取得
def fetch_artwork(title, artist):
    query = f"{artist} {title}".replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
    res = requests.get(url).json()
    if res["resultCount"] > 0:
        artwork_url = res["results"][0]["artworkUrl100"].replace("100x100bb", "600x600bb")
        return artwork_url
    return None

# 画像表示
def show_artwork(img_url):
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).resize((400, 400))
    root = tk.Tk()
    root.title("Album Art")
    tk_img = ImageTk.PhotoImage(img)
    tk.Label(root, image=tk_img).pack()
    root.mainloop()

"""
# 実行
title, artist = get_current_track_info()
if title and artist:
    print(f"🎵 {title} - {artist}")
    art_url = fetch_artwork(title, artist)
    if art_url:
        show_artwork(art_url)
        print(art_url)
    else:
        print("アートワークが見つかりませんでした。")
else:
    print("Apple Musicは再生されていません。")
    """

# 実行
title, artist = get_current_track_info()

image_url = fetch_artwork(title, artist)

# 画像を取得して円形マスクを適用
response = requests.get(image_url)
original_img = Image.open(BytesIO(response.content)).convert("RGBA")

mask = Image.new('L', original_img.size, 0)
ImageDraw.Draw(mask).ellipse((0, 0, original_img.size[0], original_img.size[1]), fill=255)

circular_img = Image.new("RGBA", original_img.size)
circular_img.paste(original_img, (0, 0), mask=mask)

# Tkinter画面の準備
root = tk.Tk()
root.title("回転するジャケット")
canvas = tk.Canvas(root, width=800, height=800, highlightthickness=0)
canvas.pack()

angle = 0  # 初期回転角度

# アニメーション関数
def rotate_image():
    global angle, tk_img
    angle = (angle - 1.5) % 360  # 回転角度を更新
    rotated = circular_img.rotate(angle, resample=Image.BICUBIC)
    tk_img = ImageTk.PhotoImage(rotated)
    canvas.create_image(400, 400, image=tk_img)
    root.after(10, rotate_image)  # 50ミリ秒後に再度呼び出す（約20fps）

rotate_image()
root.mainloop()