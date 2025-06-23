import requests
from io import BytesIO
from PIL import Image, ImageTk
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
