
import base64
import re

#FIFO_PATH = "/tmp/testfifo"
FIFO_PATH = "/tmp/my-metadata-pipe"

def decode_base64(data):
    try:
        return base64.b64decode(data).decode("utf-8")
    except Exception:
        return ""

def parse_metadata_block(block):
    results = {}

    if "<code>706e616d</code>" in block:  # title
        m = re.search(r"<data encoding=\"base64\">(.*?)</data>", block, re.DOTALL)
        if m:
            results["title"] = decode_base64(m.group(1).strip())

    return results

def watch_fifo():
    print("🎵 メタデータ取得中（Ctrl+Cで終了）…")

    buffer = ""
    with open(FIFO_PATH, "r") as fifo:
        for line in fifo:
            buffer += line
            if "</item>" in line:
                parsed = parse_metadata_block(buffer)
                if parsed:
                    print(f"🎶 タイトル: {parsed.get('title')}")
                buffer = ""

if __name__ == "__main__":
    watch_fifo()
    

"""
FIFO_PATH = "/tmp/my-metadata-pipe"

def watch_fifo():
    print("🎵 FIFO読み取り中（Ctrl+Cで終了）…")
    with open(FIFO_PATH, "r") as fifo:
        for line in fifo:
            print(f"[受信] {line.strip()}")

if __name__ == "__main__":
    watch_fifo()"""