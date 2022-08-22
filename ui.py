import win32gui
from pywebio import start_server

from pywebio.output import *
from pywebio.input import *
from pywebio.pin import *
from pywebio.session import set_env, run_async, defer_call
from functools import partial
from copy_tools import *
import asyncio
import pyperclip


# https://blog.pakro.top/2019/python_implements_global_keyboard_shortcuts_and_reads_clipboard-supports_all_formats/
def edit_row(choice, data):
    if choice == "复制":
        if data["type"] == "text":
            pyperclip.copy(data["content"])
        elif data["type"] == "img":
            set_clipboard_img(data["img_path"])
        elif data["type"] == "file":
            setClipboardFiles(data["content"].split("\n"))
    elif choice == "复制文字":
        pyperclip.copy(data["content"])
    # 复制完窗口隐藏 
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

    # def get_content(data):
    #     if data["type"] == "text":
    #         return data["content"]
    #     elif data["type"] == "img":
    #         return put_image(open(data["content"], 'rb').read())
    #     return


    def get_buttons(data):
        if data["type"] == "text" or data["type"] == "file":
            return put_buttons([
                {
                    "label": "复制",
                    "value": "复制",
                    "color": "primary"
                }
            ], onclick=partial(edit_row, data=data))
        else:
            return put_buttons(
                [
                    {
                        "label": "复制",
                        "value": "复制",
                        "color": "primary"
                    },
                    {
                        "label": "复制文字",
                        "value": "复制文字",
                        "color": "secondary"
                    }
                ], onclick=partial(edit_row, data=data), group=True)

    for idx, data in enumerate(show_content, 1):
        cur = [data["create_time"], data["type"],
               data["content"] if data["type"] == "text" or data["type"] == "file" else put_image(
                   open(data["img_path"], 'rb').read()),
               get_buttons(data)
               ]
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

    @defer_call
    def on_close():
        for item in gw.getWindowsWithTitle("History Copyboard"):
            item.close()

    refresh_task = run_async(refresh_content(show_content))

    while 1:
        data = await pin_wait_change('search_content')
        show_tab([content for content in show_content if data["value"] in content["content"]])

    refresh_task.close()


if __name__ == '__main__':
    # https://blog.pakro.top/2019/python_implements_global_keyboard_shortcuts_and_reads_clipboard-supports_all_formats/

    from main import *
    import threading
    t1 = threading.Thread(target=keyboard_listener, daemon=True)
    t1.start()
    start_server(main, port=8080, debug=True)


