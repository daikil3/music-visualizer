from PIL import Image, ImageDraw, ImageTk
import requests
from io import BytesIO
import tkinter as tk

# 適当な画像URL（Apple MusicのAPIで取得したジャケット画像でもOK）
image_url = "https://is1-ssl.mzstatic.com/image/thumb/Music1/v4/97/88/1b/97881bb9-40d4-22e8-0a8b-b611a70eb501/dj.kcvgmwmy.jpg/600x600bb.jpg"


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