import requests
from io import BytesIO
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

# 画像表示
#不採用
def show_artwork(img_url):
    img_data = requests.get(img_url).content
    img = Image.open(BytesIO(img_data)).resize((600, 600))
    root = tk.Tk()
    root.title("Album Art")
    tk_img = ImageTk.PhotoImage(img)
    tk.Label(root, image=tk_img).pack()
    root.mainloop()

#円形マスクを施した画像を生成
def show_maskedartwork(img_url):
    # 画像を取得して円形マスクを適用
    org_img_data = requests.get(img_url, stream=True)
    org_img_data.raw.decode_content = True
    org_img = Image.open(org_img_data.raw).convert("RGBA")
    #org_img = Image.open(BytesIO(org_img_data)).convert("RGBA")
    org_img.thumbnail((600, 600), Image.LANCZOS)

    mask = Image.new('L', org_img.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, org_img.size[0], org_img.size[1]), fill=255)

    circular_img = Image.new("RGBA", org_img.size)
    circular_img.paste(org_img, (0, 0), mask=mask)

    return(circular_img)

    #root = tk.Tk()
    #root.title("Album Art")
    #tk_img = ImageTk.PhotoImage(circular_img)
    #tk.Label(root, image=tk_img).pack()
    #root.mainloop()

# アニメーション関数
def rotate_image():
    global angle, tk_img, circular_img
    angle = (angle - 3.333) % 360  # 回転角度を更新
    rotated = circular_img.rotate(angle, resample=Image.BICUBIC)
    tk_img = ImageTk.PhotoImage(rotated)
    canvas.delete("all")  # 前の画像を消す
    canvas.create_image(400, 400, image=tk_img)
    root.after(16, rotate_image)  # 50ミリ秒後に再度呼び出す（約20fps）




# 適当な画像URL（Apple MusicのAPIで取得したジャケット画像でもOK）
image_url = "https://is1-ssl.mzstatic.com/image/thumb/Music1/v4/97/88/1b/97881bb9-40d4-22e8-0a8b-b611a70eb501/dj.kcvgmwmy.jpg/600x600bb.jpg"

#show_artwork(image_url)
circular_img = show_maskedartwork(image_url)

"""
root = tk.Tk()
root.title("Album Art")
tk_img = ImageTk.PhotoImage(circular_img)
tk.Label(root, image=tk_img).pack()
root.mainloop()
"""

# Tkinter画面の準備
root = tk.Tk()
root.title("回転するジャケット")
canvas = tk.Canvas(root, width=800, height=800, highlightthickness=0)
canvas.pack()

angle = 0  # 初期回転角度

rotate_image()
root.mainloop()