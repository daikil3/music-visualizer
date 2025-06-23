from PIL import Image, ImageDraw, ImageTk
import requests
from io import BytesIO
import tkinter as tk

# 適当な画像URL（Apple MusicのAPIで取得したジャケット画像でもOK）
image_url = "https://is1-ssl.mzstatic.com/image/thumb/Music1/v4/97/88/1b/97881bb9-40d4-22e8-0a8b-b611a70eb501/dj.kcvgmwmy.jpg/600x600bb.jpg"
# 画像の読み込み
response = requests.get(image_url)
img = Image.open(BytesIO(response.content)).convert("RGBA")

# 正方形画像 → 円形マスク
size = img.size
mask = Image.new('L', size, 0)  # L = 8-bit grayscale (mask用)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, size[0], size[1]), fill=255)

# マスクを適用
result = Image.new("RGBA", size)
result.paste(img, (0, 0), mask=mask)

# 表示（Tkinter）
root = tk.Tk()
root.title("円形ジャケット画像")
tk_img = ImageTk.PhotoImage(result)
tk.Label(root, image=tk_img).pack()
root.mainloop()
