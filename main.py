import win32gui, win32ui, win32con, win32api, time, win32com.client
import pygetwindow as gw
from pynput import keyboard
import subprocess
import pyautogui
import os
import json
from get_browser_path import *


def on_press(key):
    try:
        key_pressed = key.char  # single-char keys
    except:
        key_pressed = key.name  # other keys
    active_window = win32gui.GetForegroundWindow()
    active_window_title = win32gui.GetWindowText(active_window)
    if active_window_title == "History Copyboard" and key_pressed == "esc":
        win32gui.ShowWindow(active_window, win32con.SW_HIDE)


def on_activate_c():
    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
    # global cur_hWnd
    cur_hWnd = win32gui.FindWindow(None, "History Copyboard")
    cur_path = os.path.dirname(__file__)
    if not os.path.exists("browse_config.json"):
        with open("browse_config.json", "w+", encoding="utf-8") as f:
            f.write("{}")
    with open("browse_config.json", 'r', encoding='utf8')as fp:
        p = json.load(fp)
    if not p:
        p["path"] = get_browser_path('chrome')
        with open("browse_config.json", "w", encoding="utf-8") as f:
            json.dump(p, f, indent=2, ensure_ascii=False)



    if not cur_hWnd:
        cmd = fr'"{p["path"]}" --chrome-frame --user-data-dir="{cur_path}\tmp-chrome"  --app=http://127.0.0.1:8080 --window-size=1000,800 "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --chrome-frame --user-data-dir=".\tmp-chrome"  --app=http://127.0.0.1:8080 --window-size=1000,800"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --chrome-frame --user-data-dir=".\tmp-chrome"  --app=http://127.0.0.1:8080 --window-size=1000,800 '
        subprocess.Popen(cmd, shell=True)  # 后台运行
        while not cur_hWnd:
            cur_hWnd = win32gui.FindWindow(None, "History Copyboard")
    # 856， 270
    gw.Win32Window(cur_hWnd).moveTo(*[pyautogui.position()[0] - 856, pyautogui.position()[1] - 270])  # 移动窗口
    win32gui.ShowWindow(cur_hWnd, win32con.SW_SHOW)  # 显示窗口
    # https://stackoverflow.com/questions/14295337/win32gui-setactivewindow-error-the-specified-procedure-could-not-be-found?noredirect=1&lq=1
    # pythoncom.CoInitialize()
    # shell = win32com.client.Dispatch("WScript.Shell")
    win32gui.SendMessage(cur_hWnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)
    try:
        win32gui.SetForegroundWindow(cur_hWnd)  # 前置窗口
    except:
        pass
    win32gui.SetWindowPos(cur_hWnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOOWNERZORDER | win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)  # 置顶窗口
    # shell.SendKeys('%')


def keyboard_listener():
    h = keyboard.GlobalHotKeys({'<alt>+c': on_activate_c})
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    h.start()
    listener.join()
    h.join()


if __name__ == '__main__':
    keyboard_listener()
