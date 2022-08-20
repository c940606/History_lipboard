from pywebio import start_server

from pywebio.output import *
from pywebio.session import set_env
from functools import partial
from copy_tools import *
import asyncio
import pyperclip
import win32gui

def edit_row(choice, row):
    if choice["type"] == "text":
        pyperclip.copy(choice["content"])
    elif choice["type"] == "img":
        set_clipboard_img(choice["content"])

    # 按钮之后 隐藏
    active_window = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(active_window, win32con.SW_HIDE)

async def get_content():
    pre = None
    while 1:
        content = pyperclip.paste()
        await asyncio.sleep(0.5)
        if content and content != pre:
            yield content
            pre = content


def show_tab(show_content):
    head = [["Time", "type", 'Content', 'Actions']]
    all_data = []
    txt_data = []
    img_data = []
    file_data = []
    for idx, data in enumerate(show_content, 1):
        cur = [data["create_time"], data["type"],
               data["content"] if data["type"] == "text" else put_image(open(data["content"], 'rb').read()),
               put_buttons(
                   [
                       {
                           "label": "复制",
                           "value": data,
                       }
                   ], onclick=partial(edit_row, row=idx))]
        all_data.append(cur)
        if data["type"] == "text":
            txt_data.append(cur)
        elif data["type"] == "img":
            img_data.append(cur)
        elif data["type"] == "file":
            file_data.append(cur)

    with use_scope('content', clear=True):
        put_tabs([
            {'title': '全部', 'content': put_table(head + all_data)},
            {'title': '文本', 'content': put_table(head + txt_data)},
            {'title': '图片', 'content': put_table(head + img_data)},
            {'title': '文件', 'content': put_table(head + file_data)},

        ])


async def refresh_content(show_content):
    async for data in get_clipboard_contents():
        if show_content and show_content[0]["hash"] == data["hash"]: continue
        show_content.insert(0, data)
        show_tab(show_content)


async def main():
    """History Copyboard"""
    set_env(output_animation=False)
    put_markdown('## 历史剪切板')
    if not os.path.exists("history_data.json"):
        with open("history_data.json", "w+", encoding="utf-8") as f:
            f.write("[]")
    with open('history_data.json', 'r', encoding='utf8')as fp:
        show_content = json.load(fp)

    put_input("search_content", placeholder="搜索框")
    show_content = show_content[:100]
    show_tab(show_content)

    refresh_task = run_async(refresh_content(show_content))

    while 1:
        data = await pin_wait_change('search_content')
        show_tab([content for content in show_content if data["value"] in content["content"]])

    refresh_task.close()

if __name__ == '__main__':
    start_server(main, port=8080, debug=True)
