import pyautogui
import subprocess
import webbrowser
import platform
import time
import threading
from core.logger import log_info, log_error

pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.0
SW, SH = pyautogui.size()

APPS = {
    "OPEN_YOUTUBE":  "https://www.youtube.com",
    "OPEN_NETFLIX":  "https://www.netflix.com",
    "OPEN_AMAZON":   "https://www.primevideo.com",
    "OPEN_SPOTIFY":  "https://open.spotify.com",
    "OPEN_GOOGLE":   "https://www.google.com",
    "OPEN_DISNEY":   "https://www.disneyplus.com",
    "OPEN_HOTSTAR":  "https://www.hotstar.com",
    "OPEN_HULU":     "https://www.hulu.com",
    "OPEN_BROWSER":  "https://www.google.com",
}

def _focus_media():
    try:
        if platform.system() == "Windows":
            import win32gui, win32con
            found = []
            kws = ["youtube","netflix","prime","spotify","disney","hotstar",
                   "hulu","chrome","firefox","edge","opera","brave","vlc"]
            def cb(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd): return
                t = win32gui.GetWindowText(hwnd).lower()
                if any(k in t for k in kws):
                    found.append(hwnd)
            win32gui.EnumWindows(cb, None)
            if found:
                win32gui.ShowWindow(found[0], win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(found[0])
                time.sleep(0.08)
                return
    except Exception as e:
        log_error(f"focus: {e}")
    pyautogui.keyDown("alt")
    time.sleep(0.05)
    pyautogui.press("tab")
    pyautogui.keyUp("alt")
    time.sleep(0.12)


def execute_action(action: str, meta: dict = None) -> str:
    meta = meta or {}
    log_info(f"▶ {action}")
    try:
        # ── Cursor move — directly moves OS mouse, works everywhere ──
        if action == "MOVE_CURSOR":
            x = max(0, min(SW-1, int(float(meta.get("x", 0.5)) * SW)))
            y = max(0, min(SH-1, int(float(meta.get("y", 0.5)) * SH)))
            pyautogui.moveTo(x, y, duration=0)  # instant, no lag
            return f"MOVE {x},{y}"

        # ── Click — clicks wherever cursor is on screen ──────────────
        if action == "CLICK":
            pyautogui.click()   # no focus change needed — clicks at current cursor pos
            return "Done: CLICK"

        if action == "DOUBLE_CLICK":
            pyautogui.doubleClick()
            return "Done: DOUBLE_CLICK"

        if action == "RIGHT_CLICK":
            pyautogui.rightClick()
            return "Done: RIGHT_CLICK"

        # ── Apps — instant open ───────────────────────────────────────
        if action in APPS:
            threading.Thread(target=lambda u: webbrowser.open_new_tab(u),
                           args=(APPS[action],), daemon=True).start()
            return f"Done: {action}"

        # ── All other keyboard actions need media window focus ────────
        _focus_media()

        if   action == "VOLUME_UP":
            for _ in range(5): pyautogui.press("volumeup")
        elif action == "VOLUME_DOWN":
            for _ in range(5): pyautogui.press("volumedown")
        elif action == "MUTE":           pyautogui.press("volumemute")
        elif action == "UNMUTE":         pyautogui.press("volumemute")
        elif action == "VOLUME_MAX":
            for _ in range(30): pyautogui.press("volumeup")
        elif action == "VOLUME_MIN":
            for _ in range(30): pyautogui.press("volumedown")
        elif action in ("PLAY","PAUSE","PLAY_PAUSE"):
            pyautogui.press("space")
        elif action == "NEXT":           pyautogui.press("nexttrack")
        elif action == "PREVIOUS":       pyautogui.press("prevtrack")
        elif action == "FAST_FORWARD":   pyautogui.press("right")
        elif action == "REWIND":         pyautogui.press("left")
        elif action == "FULLSCREEN":     pyautogui.press("f")
        elif action == "SUBTITLE":       pyautogui.press("c")
        elif action == "AUDIO_TRACK":    pyautogui.press("a")
        elif action == "REPLAY":         pyautogui.hotkey("ctrl","r")
        elif action == "CHANNEL_UP":     pyautogui.hotkey("ctrl","up")
        elif action == "CHANNEL_DOWN":   pyautogui.hotkey("ctrl","down")
        elif action == "CHANNEL_LAST":   pyautogui.hotkey("alt","left")
        elif action == "NAV_UP":         pyautogui.press("up")
        elif action == "NAV_DOWN":       pyautogui.press("down")
        elif action == "NAV_LEFT":       pyautogui.press("left")
        elif action == "NAV_RIGHT":      pyautogui.press("right")
        elif action == "SELECT":         pyautogui.press("enter")
        elif action == "BACK":           pyautogui.hotkey("alt","left")
        elif action == "HOME":           pyautogui.hotkey("win","d")
        elif action == "MENU":           pyautogui.press("escape")
        elif action == "EXIT":           pyautogui.hotkey("alt","f4")
        elif action == "SEARCH":         pyautogui.hotkey("ctrl","f")
        elif action == "SCROLL_UP":      pyautogui.scroll(5)
        elif action == "SCROLL_DOWN":    pyautogui.scroll(-5)
        elif action == "ZOOM_IN":        pyautogui.hotkey("ctrl","=")
        elif action == "ZOOM_OUT":       pyautogui.hotkey("ctrl","-")
        elif action == "SCREENSHOT":     pyautogui.hotkey("win","shift","s")
        elif action == "SCREEN_MIRROR":  pyautogui.hotkey("win","p")
        elif action in ("TV_POWER_OFF","SHUTDOWN"): _sys("shutdown")
        elif action == "RESTART":        _sys("restart")
        else:                            return f"Done: {action}"

        return f"Done: {action}"

    except Exception as e:
        log_error(f"Error ({action}): {e}")
        return f"Error: {e}"


def _sys(cmd):
    s = platform.system()
    if cmd == "shutdown":
        subprocess.run(["shutdown","/s","/t","5"] if s=="Windows" else ["shutdown","-h","+1"])
    elif cmd == "restart":
        subprocess.run(["shutdown","/r","/t","5"] if s=="Windows" else ["shutdown","-r","+1"])