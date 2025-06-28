import requests
from io import BytesIO
from PIL import Image, ImageTk
import tkinter as tk
import subprocess

#再生中のトラックのタイトルと曲名を取得
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
"""
def fetch_artwork(title, artist):
    query = f"{artist} {title}".replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"
    res = requests.get(url).json()
    if res["resultCount"] > 0:
        artwork_url = res["results"][0]["artworkUrl100"].replace("100x100bb", "600x600bb")
        return artwork_url
    return None
    """

def fetch_artworkurl(title, artist):
    # クエリを生成
    query = f"{artist} {title}".replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={query}&entity=song&limit=1"

    try:
        res = requests.get(url, timeout=3)
        data = res.json()

        if data["resultCount"] > 0:
            artwork_url = data["results"][0]["artworkUrl100"]
            # 高解像度に置換（存在しない場合も多いが、軽量処理）
            return artwork_url.replace("100x100bb", "1200x1200bb")

    except Exception as e:
        print(f"エラー: {e}")

    return None

# 画像表示
def show_artwork(img_url):
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).resize((600, 600))
    root = tk.Tk()
    root.title("Album Art")
    tk_img = ImageTk.PhotoImage(img)
    tk.Label(root, image=tk_img).pack()
    root.mainloop()

#get_current_track_info()
title, artist = get_current_track_info()

#print(title)
#print(artist)

img_url = fetch_artworkurl(title, artist)

show_artwork(img_url)
