import os
import re
import base64

FIFO_PATH = "/tmp/my-metadata-pipe"  # Shairport Sync の設定で指定したパイプ名

# Base64データをデコードしてUTF-8文字列に変換
def decode_base64(data):
    try:
        return base64.b64decode(data).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Base64 decode error: {e}")
        return ""

# メタデータブロックから必要な情報を抽出
def parse_metadata_block(block):
    results = {}

    # 曲名（pnam）
    if "<code>706e616d</code>" in block:
        m = re.search(r"<data encoding=\"base64\">(.*?)</data>", block, re.DOTALL)
        if m:
            results["title"] = decode_base64(m.group(1).strip())

    # アーティスト名（asar）
    if "<code>61736172</code>" in block:
        m = re.search(r"<data encoding=\"base64\">(.*?)</data>", block, re.DOTALL)
        if m:
            results["artist"] = decode_base64(m.group(1).strip())

    # アルバム名（aalb）
    if "<code>61616c62</code>" in block:
        m = re.search(r"<data encoding=\"base64\">(.*?)</data>", block, re.DOTALL)
        if m:
            results["album"] = decode_base64(m.group(1).strip())

    return results

# FIFOを監視してメタデータを取得・表示
def watch_fifo():
    print("🎵 FIFO読み取り中（Ctrl+Cで終了）…")
    current_info = {}
    buffer = ""

    with open(FIFO_PATH, "r") as fifo:
        for line in fifo:
            buffer += line

            if "</item>" in line:
                if "<code>50494354</code>" in buffer:
                    buffer = ""  # cover art のデータはスキップ
                    continue

                parsed = parse_metadata_block(buffer)
                buffer = ""  # バッファをリセット

                if parsed:
                    current_info.update(parsed)

                    # 1つでも情報が増えたら表示する
                    for key in ("title", "artist", "album"):
                        if key in parsed:
                            print(f"🎶 {key.title()}: {current_info.get(key)}")

def debug_info(info):
    print("🧩 DEBUG INFO:")
    for key, value in info.items():
        print(f"  - {key}: {value}")
    print("-" * 40)

if __name__ == "__main__":
    watch_fifo()