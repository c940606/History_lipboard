from PIL import ImageGrab, Image
import pyperclip
import win32clipboard as clip
import win32con
from io import BytesIO
import json
import hashlib
import asyncio
import datetime
import os
import shutil

pre_hash = None


def add_data(new_data):
    with open("history_data.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)
        old_data.insert(0, new_data)

    with open("history_data.json", "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)


def get_text(cur):
    return cur


def get_img(cur, data, nowTime):
    cur_hash = hashlib.md5(data.tobytes()).hexdigest()
    cur["hash"] = cur_hash
    cur["type"] = "img"
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if pre_hash == cur_hash:
        return cur
    data.save(os.path.join(img_dir, f"{nowTime}.png"))
    cur["content"] = os.path.join(img_dir, f"{nowTime}.png")
    return cur


def get_folders():
    pass


def file_hash(file_path: str, hash_method) -> str:
    if not os.path.isfile(file_path):
        print('文件不存在。')
        return ''
    h = hash_method()
    with open(file_path, 'rb') as f:
        while b := f.read(8192):
            h.update(b)
    return h.hexdigest()


def get_files(cur, data, nowTime):
    cur["type"] = "file"
    for item in data:
        cur["content"] = os.path.join(os.path.dirname(__file__), "files", f"{nowTime}_{os.path.basename(item)}")
        cur["hash"] = file_hash(cur["content"], hashlib.md5)
        file_dir = os.path.join(os.path.dirname(__file__), "img")
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        shutil.copy(item, os.path.join(file_dir, f"{nowTime}_{os.path.basename(item)}"))
    return cur


def setImage(data):
    clip.OpenClipboard()  # 打开剪贴板
    clip.EmptyClipboard()  # 先清空剪贴板
    clip.SetClipboardData(win32con.CF_DIB, data)  # 将图片放入剪贴板
    clip.CloseClipboard()


def set_clipboard_img(path):
    img = Image.open(path)
    output = BytesIO()
    img.save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    setImage(data)


async def get_clipboard_contents():
    global pre_hash

    while 1:
        await asyncio.sleep(0.5)
        content = pyperclip.paste()
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        cur = {
            "type": "text",
            "content": content,
            "create_time": nowTime,
            "hash": hashlib.md5(content.encode("utf8")).hexdigest()
        }

        if content:
            cur = get_text(cur)
        else:
            try:
                data = ImageGrab.grabclipboard()
            except:
                continue
            if isinstance(data, list):
                cur = get_files(cur, data, nowTime)
            elif isinstance(data, Image.Image):
                cur = get_img(cur, data, nowTime)

            else:
                continue

        if pre_hash == cur["hash"]: continue
        pre_hash = cur["hash"]
        add_data(cur)
        yield cur