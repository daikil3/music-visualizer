import os
import glob
import time
from tkinter import Tk, Label
from PIL import Image, ImageTk

ART_DIR = "/tmp/shairport-sync"
CHECK_INTERVAL = 500  # 監視間隔（ミリ秒）

class CoverArtViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Now Playing Cover Art")
        self.root.attributes("-fullscreen", True)  # フルスクリーンにする
        self.root.configure(bg="black")

        self.label = Label(root, bg="black")
        self.label.place(relx=0.5, rely=0.5, anchor="center")

        self.current_image_path = None
        self.current_mtime = 0

        # 画面サイズ取得
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.check_update()

    def get_latest_image_path(self):
        image_files = glob.glob(os.path.join(ART_DIR, "*"))
        image_files = [f for f in image_files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not image_files:
            return None
        latest = max(image_files, key=os.path.getctime)
        return latest

    def update_image(self, image_path):
        img = Image.open(image_path)

        # アスペクト比を維持して画面に収まるようにリサイズ
        img_ratio = img.width / img.height
        screen_ratio = self.screen_width / self.screen_height

        if img_ratio > screen_ratio:
            new_width = self.screen_width
            new_height = int(self.screen_width / img_ratio)
        else:
            new_height = self.screen_height
            new_width = int(self.screen_height * img_ratio)

        img = img.resize((new_width, new_height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)

        self.label.configure(image=photo)
        self.label.image = photo  # 参照保持

    def check_update(self):
        path = self.get_latest_image_path()
        if path:
            mtime = os.path.getmtime(path)
            if path != self.current_image_path or mtime != self.current_mtime:
                print(f"画像更新: {path}")
                self.update_image(path)
                self.current_image_path = path
                self.current_mtime = mtime
        else:
            print("画像が見つかりません。")

        self.root.after(CHECK_INTERVAL, self.check_update)

if __name__ == "__main__":
    root = Tk()
    viewer = CoverArtViewer(root)
    root.mainloop()