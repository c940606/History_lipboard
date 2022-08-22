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
import requests
import base64
from ctypes import *

pre_hash = None


def add_data(new_data):
    with open("history_data.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)
        old_data.insert(0, new_data)

    with open("history_data.json", "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)


def get_text(cur):
    return cur

def get_img_word(cur):


    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    f = open(cur["img_path"], 'rb')
    img = base64.b64encode(f.read())

    params = {"image": img}


    with open("browse_config.json", 'r', encoding='utf8')as fp:
        p = json.load(fp)

    access_token = p["access_token"]
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers, proxies=p.get("proxies", {}))

    for item in response.json().get("words_result", []):
        cur["content"] += item.get("words") + "\n"

    return cur


def get_img(cur, data, nowTime):
    cur_hash = hashlib.md5(data.tobytes()).hexdigest()
    cur["hash"] = cur_hash
    cur["type"] = "img"

    img_dir = os.path.join(os.path.abspath("."), "img")
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if pre_hash == cur_hash:
        return cur
    data.save(os.path.join(img_dir, f"{nowTime}.png"))

    cur["img_path"] = os.path.join(img_dir, f"{nowTime}.png")

    cur = get_img_word(cur)
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
    cur["content"] = "\n".join(data)
    for item in data:
        cur["hash"] += file_hash(item, hashlib.md5)
    if pre_hash == cur["hash"]:
        return cur
    # for item in data:
    #     file_dir = os.path.join(os.path.dirname(__file__), "files")
    #     if not os.path.exists(file_dir):
    #         os.mkdir(file_dir)
    # shutil.copy(item, os.path.join(file_dir, f"{nowTime}_{os.path.basename(item)}"))

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


class DROPFILES(Structure):
    _fields_ = [
        ("pFiles", c_uint),
        ("x", c_long),
        ("y", c_long),
        ("fNC", c_int),
        ("fWide", c_bool),
    ]


pDropFiles = DROPFILES()
pDropFiles.pFiles = sizeof(DROPFILES)
pDropFiles.fWide = True
matedata = bytes(pDropFiles)


def setClipboardFiles(paths):
    # https://xxmdmst.blog.csdn.net/article/details/120631425
    files = ("\0".join(paths)).replace("/", "\\")
    data = files.encode("U16")[2:] + b"\0\0"
    clip.OpenClipboard()
    try:
        clip.EmptyClipboard()
        clip.SetClipboardData(
            clip.CF_HDROP, matedata + data)
    finally:
        clip.CloseClipboard()


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


if __name__ == '__main__':
    get_clipboard_contents()
