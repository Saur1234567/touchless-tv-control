"""
TOUCHLESS TV CONTROL SYSTEM v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Window 1: Main control UI  (Tkinter)
Window 2: Live camera feed with MediaPipe landmark overlay (OpenCV)

Features:
• Real camera feed with colored landmark dots + connection lines
• Voice animated waveform bars
• Gesture guide with active row highlight
• Stats counter, activity log
• Cursor control via index finger
"""

import cv2
import mediapipe as mp
import pyautogui
import threading
import time
import webbrowser
import platform
import subprocess
import queue
import urllib.parse
import tkinter as tk
from PIL import Image, ImageTk   # pip install pillow
import math, random

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    import speech_recognition as sr
    SPEECH_OK = True
except ImportError:
    SPEECH_OK = False

from flask import Flask, request, jsonify
from flask_cors import CORS

# ══════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════
pyautogui.FAILSAFE = False
pyautogui.PAUSE    = 0.0
SW, SH = pyautogui.size()

SMOOTHING    = 0.25
GESTURE_HOLD = 14
GESTURE_COOL = 2.0
CAM_W, CAM_H = 480, 360

# Palette
C_BG       = "#08080f"
C_BG2      = "#0d0d18"
C_BG3      = "#131320"
C_ACCENT   = "#00f5c4"
C_ACCENT2  = "#7c5cfc"
C_ACCENT3  = "#ff4d7d"
C_YELLOW   = "#ffd166"
C_GREEN    = "#00e676"
C_TEXT     = "#dde0f0"
C_TEXT2    = "#5a5a88"
C_TEXT3    = "#2a2a44"
C_BORDER   = "#1a1a30"

SOCKET_URL = "http://127.0.0.1:5000"

# Landmark colors per finger (BGR for OpenCV, hex for Tkinter)
FINGER_BGR = {
    "wrist":  (0, 245, 196),   # teal
    "thumb":  (80, 77, 255),   # red-pink
    "index":  (252, 92, 124),  # purple-blue
    "middle": (0, 180, 216),   # cyan
    "ring":   (0, 127, 247),   # orange
    "pinky":  (0, 214, 102),   # green
}
FINGER_HEX = {
    "wrist":  "#00f5c4",
    "thumb":  "#ff4d50",
    "index":  "#7c5cfc",
    "middle": "#00b4d8",
    "ring":   "#f77f00",
    "pinky":  "#06d6a0",
}
LM_FINGER = {
    0:"wrist",
    1:"thumb",2:"thumb",3:"thumb",4:"thumb",
    5:"index",6:"index",7:"index",8:"index",
    9:"middle",10:"middle",11:"middle",12:"middle",
    13:"ring",14:"ring",15:"ring",16:"ring",
    17:"pinky",18:"pinky",19:"pinky",20:"pinky",
}
MP_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (5,9),(9,10),(10,11),(11,12),
    (9,13),(13,14),(14,15),(15,16),
    (13,17),(17,18),(18,19),(19,20),
    (0,17)
]

APPS = {
    "OPEN_YOUTUBE":  "https://www.youtube.com",
    "OPEN_NETFLIX":  "https://www.netflix.com",
    "OPEN_AMAZON":   "https://www.primevideo.com",
    "OPEN_SPOTIFY":  "https://open.spotify.com",
    "OPEN_GOOGLE":   "https://www.google.com",
    "OPEN_DISNEY":   "https://www.disneyplus.com",
    "OPEN_HOTSTAR":  "https://www.hotstar.com",
    "OPEN_HULU":     "https://www.hulu.com",
}

GESTURE_MAP = {
    "THUMBS_UP":     "VOLUME_UP",
    "THUMBS_DOWN":   "VOLUME_DOWN",
    "FIST":          "PLAY_PAUSE",
    "TWO_FINGERS":   "OPEN_YOUTUBE",
    "THREE_FINGERS": "OPEN_NETFLIX",
    "FOUR_FINGERS":  "OPEN_AMAZON",
    "ROCK":          "BACK",
    "OPEN_HAND":     "FULLSCREEN",
}

GESTURE_ICONS = {
    "THUMBS_UP":     "👍",
    "THUMBS_DOWN":   "👎",
    "FIST":          "✊",
    "TWO_FINGERS":   "✌",
    "THREE_FINGERS": "🤟",
    "FOUR_FINGERS":  "🖐",
    "ROCK":          "🤘",
    "OPEN_HAND":     "✋",
    "PINCH":         "🤏",
    "POINTING":      "☝",
}

# ══════════════════════════════════════════════════════════
# FLASK SERVER
# ══════════════════════════════════════════════════════════
flask_app  = Flask(__name__)
CORS(flask_app)
log_events = []

@flask_app.route('/api/log', methods=['POST'])
def api_log():
    log_events.append(request.json)
    return jsonify({"ok": True})

@flask_app.route('/api/events')
def api_events():
    return jsonify(log_events[-50:])

def run_server():
    flask_app.run(port=5000, debug=False, use_reloader=False)

# ══════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════
def get_browser_wins():
    result = []
    try:
        if platform.system() == "Windows":
            import win32gui
            kws = ["youtube","netflix","prime","spotify","disney","hotstar","hulu","chrome","firefox","edge","brave","vlc"]
            def cb(hwnd, _):
                if not win32gui.IsWindowVisible(hwnd): return
                t = win32gui.GetWindowText(hwnd).lower()
                if any(k in t for k in kws):
                    result.append((hwnd, win32gui.GetWindowText(hwnd)))
            win32gui.EnumWindows(cb, None)
    except: pass
    return result

def focus_media():
    wins = get_browser_wins()
    if wins:
        try:
            import win32gui, win32con
            hwnd = wins[0][0]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.08)
            return True
        except: pass
    pyautogui.keyDown("alt"); time.sleep(0.05)
    pyautogui.press("tab"); pyautogui.keyUp("alt"); time.sleep(0.12)
    return True

def current_site():
    wins = get_browser_wins()
    if not wins: return "google"
    t = wins[0][1].lower()
    for s in ["youtube","netflix","prime","amazon","spotify","hotstar","disney","hulu"]:
        if s in t: return "amazon" if s=="prime" else s
    return "google"

def do_search(query):
    site = current_site()
    q = urllib.parse.quote_plus(query)
    urls = {
        "youtube": f"https://www.youtube.com/results?search_query={q}",
        "netflix": f"https://www.netflix.com/search?q={q}",
        "amazon":  f"https://www.primevideo.com/search/ref=atv_sr_sug_3?phrase={q}",
        "spotify": f"https://open.spotify.com/search/{q}",
        "hotstar": f"https://www.hotstar.com/in/search?q={q}",
        "disney":  f"https://www.disneyplus.com/search/{q}",
        "google":  f"https://www.google.com/search?q={q}",
    }
    url = urls.get(site, urls["google"])
    threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    return f"{site.title()} search: {query}"

# ══════════════════════════════════════════════════════════
# ACTIONS
# ══════════════════════════════════════════════════════════
def execute(action, meta=None):
    meta = meta or {}
    try:
        if action == "MOVE_CURSOR":
            x = max(0, min(SW-1, int(float(meta.get("x",0.5))*SW)))
            y = max(0, min(SH-1, int(float(meta.get("y",0.5))*SH)))
            pyautogui.moveTo(x, y, duration=0)
            return f"Cursor {x},{y}"
        if action == "CLICK":        pyautogui.click();        return "Click ✓"
        if action == "DOUBLE_CLICK": pyautogui.doubleClick();  return "Double Click ✓"
        if action == "RIGHT_CLICK":  pyautogui.rightClick();   return "Right Click ✓"
        if action == "SCROLL_UP":    pyautogui.scroll(5);      return "Scroll Up ✓"
        if action == "SCROLL_DOWN":  pyautogui.scroll(-5);     return "Scroll Down ✓"
        if action in APPS:
            url = APPS[action]
            threading.Thread(target=lambda: webbrowser.open_new_tab(url), daemon=True).start()
            return action.replace("OPEN_","").title()+" khul raha hai ✓"
        if action == "NEXT_TAB":   focus_media(); pyautogui.hotkey("ctrl","tab");         return "Agla tab ✓"
        if action == "PREV_TAB":   focus_media(); pyautogui.hotkey("ctrl","shift","tab"); return "Pichla tab ✓"
        if action == "NEW_TAB":    focus_media(); pyautogui.hotkey("ctrl","t");           return "Naya tab ✓"
        if action == "CLOSE_TAB":  focus_media(); pyautogui.hotkey("ctrl","w");           return "Tab band ✓"
        focus_media()
        KB = {
            "VOLUME_UP":    lambda: [pyautogui.press("volumeup")   for _ in range(5)],
            "VOLUME_DOWN":  lambda: [pyautogui.press("volumedown") for _ in range(5)],
            "VOLUME_MAX":   lambda: [pyautogui.press("volumeup")   for _ in range(30)],
            "VOLUME_MIN":   lambda: [pyautogui.press("volumedown") for _ in range(30)],
            "MUTE":         lambda: pyautogui.press("volumemute"),
            "UNMUTE":       lambda: pyautogui.press("volumemute"),
            "PLAY_PAUSE":   lambda: pyautogui.press("space"),
            "PLAY":         lambda: pyautogui.press("space"),
            "PAUSE":        lambda: pyautogui.press("space"),
            "NEXT":         lambda: pyautogui.press("nexttrack"),
            "PREVIOUS":     lambda: pyautogui.press("prevtrack"),
            "FAST_FORWARD": lambda: pyautogui.press("right"),
            "REWIND":       lambda: pyautogui.press("left"),
            "FULLSCREEN":   lambda: pyautogui.press("f"),
            "SUBTITLE":     lambda: pyautogui.press("c"),
            "NAV_UP":       lambda: pyautogui.press("up"),
            "NAV_DOWN":     lambda: pyautogui.press("down"),
            "NAV_LEFT":     lambda: pyautogui.press("left"),
            "NAV_RIGHT":    lambda: pyautogui.press("right"),
            "SELECT":       lambda: pyautogui.press("enter"),
            "BACK":         lambda: pyautogui.hotkey("alt","left"),
            "HOME":         lambda: pyautogui.hotkey("win","d"),
            "MENU":         lambda: pyautogui.press("escape"),
            "EXIT":         lambda: pyautogui.hotkey("alt","f4"),
            "SEARCH_BAR":   lambda: pyautogui.hotkey("ctrl","f"),
            "ZOOM_IN":      lambda: pyautogui.hotkey("ctrl","="),
            "ZOOM_OUT":     lambda: pyautogui.hotkey("ctrl","-"),
            "SCREENSHOT":   lambda: pyautogui.hotkey("win","shift","s"),
            "REFRESH":      lambda: pyautogui.hotkey("ctrl","r"),
            "COPY":         lambda: pyautogui.hotkey("ctrl","c"),
            "PASTE":        lambda: pyautogui.hotkey("ctrl","v"),
        }
        if action in KB:
            KB[action](); return action.replace("_"," ").title()+" ✓"
        if action in ("TV_POWER_OFF","SHUTDOWN"): _sys("shutdown"); return "Shutdown..."
        if action == "RESTART":                   _sys("restart");  return "Restart..."
        return f"Done: {action}"
    except Exception as e:
        return f"Error: {e}"

def broadcast_log(source, action, result):
    if not REQUESTS_OK: return
    try:
        requests.post(f"{SOCKET_URL}/api/log",
                      json={"source":source,"action":action,"result":result},
                      timeout=0.3)
    except: pass

def _sys(cmd):
    s = platform.system()
    if cmd == "shutdown":
        subprocess.run(["shutdown","/s","/t","5"] if s=="Windows" else ["shutdown","-h","+1"])
    elif cmd == "restart":
        subprocess.run(["shutdown","/r","/t","5"] if s=="Windows" else ["shutdown","-r","+1"])

# ══════════════════════════════════════════════════════════
# VOICE PARSER
# ══════════════════════════════════════════════════════════
def parse_voice(text):
    t = text.lower().strip()
    for pre in ["search for ","search ","find ","look for "]:
        if t.startswith(pre):
            q = t[len(pre):].strip()
            if q: return ("SEARCH", q)
    if any(w in t for w in ["next tab","agle tab"]):           return ("NEXT_TAB",  None)
    if any(w in t for w in ["previous tab","pichle tab"]):     return ("PREV_TAB",  None)
    if any(w in t for w in ["new tab","naya tab"]):             return ("NEW_TAB",   None)
    if any(w in t for w in ["close tab","tab band"]):           return ("CLOSE_TAB", None)
    if "double click" in t: return ("DOUBLE_CLICK", None)
    if "right click"  in t: return ("RIGHT_CLICK",  None)
    if t in ("click","click karo","click here") or t.endswith(" click"): return ("CLICK", None)
    if "scroll up"   in t: return ("SCROLL_UP",   None)
    if "scroll down" in t: return ("SCROLL_DOWN", None)
    if "youtube"  in t: return ("OPEN_YOUTUBE", None)
    if "netflix"  in t: return ("OPEN_NETFLIX", None)
    if "amazon"   in t or "prime" in t: return ("OPEN_AMAZON",  None)
    if "spotify"  in t: return ("OPEN_SPOTIFY", None)
    if "hotstar"  in t: return ("OPEN_HOTSTAR", None)
    if "disney"   in t: return ("OPEN_DISNEY",  None)
    if "google"   in t: return ("OPEN_GOOGLE",  None)
    if any(w in t for w in ["volume up","louder","turn up"]):      return ("VOLUME_UP",   None)
    if any(w in t for w in ["volume down","quieter","turn down"]): return ("VOLUME_DOWN", None)
    if "max volume" in t: return ("VOLUME_MAX", None)
    if "min volume" in t: return ("VOLUME_MIN", None)
    if "unmute" in t: return ("UNMUTE", None)
    if "mute"   in t: return ("MUTE",   None)
    if "fast forward" in t: return ("FAST_FORWARD", None)
    if "rewind"       in t: return ("REWIND",        None)
    if "fullscreen"   in t or "full screen" in t: return ("FULLSCREEN", None)
    if "subtitle"     in t: return ("SUBTITLE", None)
    if "next"    in t: return ("NEXT",     None)
    if "previous" in t or "prev" in t: return ("PREVIOUS", None)
    if "pause"   in t: return ("PAUSE",  None)
    if "play"    in t or "resume" in t: return ("PLAY", None)
    if "go up"    in t: return ("NAV_UP",    None)
    if "go down"  in t: return ("NAV_DOWN",  None)
    if "go left"  in t: return ("NAV_LEFT",  None)
    if "go right" in t: return ("NAV_RIGHT", None)
    if any(w in t for w in ["select","ok","confirm","enter"]): return ("SELECT", None)
    if "back"    in t: return ("BACK",  None)
    if "home"    in t: return ("HOME",  None)
    if "escape"  in t or "menu" in t: return ("MENU", None)
    if "refresh" in t or "reload" in t: return ("REFRESH", None)
    if "screenshot" in t: return ("SCREENSHOT", None)
    if "zoom in"    in t: return ("ZOOM_IN",    None)
    if "zoom out"   in t: return ("ZOOM_OUT",   None)
    if "copy"       in t: return ("COPY",       None)
    if "paste"      in t: return ("PASTE",      None)
    if any(w in t for w in ["shut down","shutdown","power off"]): return ("TV_POWER_OFF", None)
    if "restart" in t: return ("RESTART", None)
    return (None, None)

# ══════════════════════════════════════════════════════════
# GESTURE DETECTOR
# ══════════════════════════════════════════════════════════
def detect_gesture(lm):
    def up(tip, pip): return lm[tip].y < lm[pip].y
    i = up(8,6); m = up(12,10); r = up(16,14); p = up(20,18)
    cnt  = sum([i,m,r,p])
    W=lm[0]; T=lm[4]; TI=lm[3]; TM=lm[2]
    tOut = T.x < TM.x - 0.02
    if cnt==4 and tOut:  return "OPEN_HAND"
    if cnt==4:           return "FOUR_FINGERS"
    if cnt==0 and T.y < W.y-0.08 and T.y < TM.y-0.02: return "THUMBS_UP"
    if T.y>TM.y+0.02 and T.y>W.y and lm[8].y>W.y-0.05 and not tOut: return "THUMBS_DOWN"
    tf = abs(T.x-TM.x)<0.12 and abs(T.y-TM.y)<0.12
    if cnt==0 and tf: return "FIST"
    dx=abs(T.x-lm[8].x); dy=abs(T.y-lm[8].y)
    if dx<0.09 and dy<0.09 and not m and not r: return "PINCH"
    if i and not m and not r and not p: return "POINTING"
    if i and m and not r and not p:     return "TWO_FINGERS"
    if i and m and r and not p:         return "THREE_FINGERS"
    if i and not m and not r and p:     return "ROCK"
    return None

# ══════════════════════════════════════════════════════════
# OPENCV LANDMARK DRAWING ON REAL FRAME
# ══════════════════════════════════════════════════════════
def draw_landmarks_on_frame(frame, lm_list, gesture=None):
    """
    Draw colored landmark dots + glowing connection lines on real camera frame.
    lm_list: list of mediapipe NormalizedLandmark objects
    """
    h, w = frame.shape[:2]

    # Draw connections first (behind dots)
    for a, b in MP_CONNECTIONS:
        if a >= len(lm_list) or b >= len(lm_list): continue
        x1 = int(lm_list[a].x * w); y1 = int(lm_list[a].y * h)
        x2 = int(lm_list[b].x * w); y2 = int(lm_list[b].y * h)
        finger = LM_FINGER.get(a, "wrist")
        col    = FINGER_BGR[finger]
        # Glow: thick dim line
        cv2.line(frame, (x1,y1), (x2,y2),
                 tuple(int(c*0.25) for c in col), 6, cv2.LINE_AA)
        # Bright thin line
        cv2.line(frame, (x1,y1), (x2,y2), col, 2, cv2.LINE_AA)

    # Draw landmark dots
    for idx, lm in enumerate(lm_list):
        if idx >= 21: break
        cx = int(lm.x * w); cy = int(lm.y * h)
        finger = LM_FINGER.get(idx, "wrist")
        col    = FINGER_BGR[finger]
        is_tip = idx in (4, 8, 12, 16, 20)
        r      = 9 if is_tip else (7 if idx==0 else 5)
        # Outer glow
        cv2.circle(frame, (cx,cy), r+4,
                   tuple(int(c*0.2) for c in col), -1, cv2.LINE_AA)
        # Main dot
        cv2.circle(frame, (cx,cy), r, col, -1, cv2.LINE_AA)
        # White center highlight
        cv2.circle(frame, (cx,cy), max(1,r-3), (255,255,255), -1, cv2.LINE_AA)

    # Gesture label overlay (bottom bar)
    if gesture:
        icon = GESTURE_ICONS.get(gesture, "")
        label = f"  {icon}  {gesture.replace('_',' ')}  "
        bar_h = 36
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h-bar_h), (w, h), (8,8,20), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.putText(frame, label, (8, h-10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.75,
                    (0,245,196), 1, cv2.LINE_AA)
        # Thin accent line above bar
        cv2.line(frame, (0,h-bar_h), (w,h-bar_h), (0,245,196), 1)

    # FPS / info corner
    cv2.rectangle(frame, (0,0), (160,22), (8,8,20), -1)
    cv2.putText(frame, "HAND LANDMARKS", (6,15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0,180,140), 1, cv2.LINE_AA)
    return frame

# ══════════════════════════════════════════════════════════
# VOICE VISUALIZER CANVAS
# ══════════════════════════════════════════════════════════
class VoiceViz(tk.Canvas):
    BARS   = 22
    BAR_W  = 9
    GAP    = 3
    MAX_H  = 55
    MIN_H  = 3

    def __init__(self, parent, **kw):
        W = self.BARS*(self.BAR_W+self.GAP)+self.GAP
        super().__init__(parent, width=W, height=72,
                         bg=C_BG2, highlightthickness=0, **kw)
        self._active  = False
        self._heights = [self.MIN_H]*self.BARS
        self._targets = [self.MIN_H]*self.BARS
        self._phase   = 0.0
        self._label   = "Mic off"
        self._animate()

    def activate(self, label="🎤  Sun raha hun..."):
        self._active = True
        self._label  = label

    def deactivate(self, label="Mic off"):
        self._active = False
        self._label  = label
        self._targets = [self.MIN_H]*self.BARS

    def set_label(self, label):
        self._label = label

    def _animate(self):
        self._phase += 0.18
        if self._active:
            for i in range(self.BARS):
                wave  = math.sin(self._phase + i*0.45)*0.5 + 0.5
                noise = random.uniform(0.15, 1.0)
                self._targets[i] = int(self.MIN_H + (self.MAX_H-self.MIN_H)*wave*noise)
        for i in range(self.BARS):
            self._heights[i] += (self._targets[i]-self._heights[i])*0.22
        self._redraw()
        self.after(38, self._animate)

    def _redraw(self):
        self.delete("all")
        W  = int(self["width"])
        H  = int(self["height"])
        cy = H//2 - 6

        for i,h in enumerate(self._heights):
            x   = self.GAP + i*(self.BAR_W+self.GAP)
            h   = max(self.MIN_H, int(h))
            c   = abs(i - self.BARS//2)/(self.BARS//2)  # 0=center,1=edge
            if self._active:
                rv = int(124 + (200-124)*(1-c))
                gv = int(92  + (245-92) *(1-c))
                bv = int(252 + (196-252)*(1-c))
                col = f"#{rv:02x}{gv:02x}{bv:02x}"
            else:
                v = int(22 + 15*(1-c))
                col = f"#{v:02x}{v:02x}{v+8:02x}"
            self.create_rectangle(x, cy-h//2, x+self.BAR_W, cy+h//2,
                                  fill=col, outline="")
            if self._active and h > 12:
                self.create_rectangle(x, cy-h//2-2, x+self.BAR_W, cy-h//2+2,
                                      fill="#ffffff", outline="")

        # Label below bars
        self.create_text(W//2, H-10, text=self._label,
                         fill=C_ACCENT2 if self._active else C_TEXT2,
                         font=("Consolas",8,"bold"), anchor="center")

# ══════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════
class TouchlessApp:
    def __init__(self):
        self.gesture_on   = False
        self.voice_on     = False
        self.cursor_mode  = True
        self.sx=0.5; self.sy=0.5
        self.was_pinching = False
        self.last_g=""; self.g_frames=0
        self.g_cool=False
        self.sg_last=""; self.sg_frames=0
        self.log_q  = queue.Queue()
        self.cnt_g  = 0; self.cnt_v = 0; self.cnt_a = 0
        # Shared frame for camera display
        self._frame_lock  = threading.Lock()
        self._latest_frame = None
        self._build_ui()
        self._poll_log()
        self._poll_frame()

    # ─────────────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("Touchless TV Control")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        # Top accent stripe
        tk.Frame(self.root, bg=C_ACCENT, height=2).pack(fill="x", side="top")

        # ── HEADER ──────────────────────────────────────
        hdr = tk.Frame(self.root, bg=C_BG)
        hdr.pack(fill="x", padx=16, pady=(10,4))
        tk.Label(hdr, text="◈", bg=C_BG, fg=C_ACCENT,
                 font=("Consolas",20,"bold")).pack(side="left")
        tk.Label(hdr, text=" TOUCHLESS ", bg=C_BG, fg=C_TEXT,
                 font=("Consolas",15,"bold")).pack(side="left")
        tk.Label(hdr, text="TV", bg=C_BG, fg=C_ACCENT,
                 font=("Consolas",15,"bold")).pack(side="left")
        self.lbl_pill = tk.Label(hdr, text="● IDLE",
                                  bg=C_BG3, fg=C_TEXT2,
                                  font=("Consolas",8,"bold"), padx=10, pady=4)
        self.lbl_pill.pack(side="right")
        tk.Label(self.root,
                 text="Gesture + Voice se kisi bhi window ko control karo",
                 bg=C_BG, fg=C_TEXT2, font=("Consolas",8)
                 ).pack(anchor="w", padx=20)
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x", padx=14, pady=(8,0))

        # ── TOGGLE BUTTONS ───────────────────────────────
        btns = tk.Frame(self.root, bg=C_BG)
        btns.pack(fill="x", padx=14, pady=8)
        self.btn_g = self._tbtn(btns, "✋  GESTURE", False, self.toggle_gesture, 0)
        self.btn_v = self._tbtn(btns, "🎤  VOICE",   False, self.toggle_voice,   1)
        self.btn_c = self._tbtn(btns, "🖱  CURSOR",  True,  self.toggle_cursor,  2)
        for c in range(3): btns.columnconfigure(c, weight=1)

        # ── MAIN 2-COLUMN LAYOUT ─────────────────────────
        cols = tk.Frame(self.root, bg=C_BG)
        cols.pack(fill="both", padx=14, pady=0)
        left  = tk.Frame(cols, bg=C_BG)
        right = tk.Frame(cols, bg=C_BG)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        right.pack(side="right", fill="both", expand=True)

        # ── LEFT: CAMERA + LANDMARKS ─────────────────────
        self._slabel(left, "📷  LIVE CAMERA + HAND LANDMARKS")

        # Camera canvas — shows real frame from OpenCV
        self.cam_canvas = tk.Canvas(left,
                                     width=CAM_W//1, height=CAM_H//1,
                                     bg="#06060f",
                                     highlightthickness=1,
                                     highlightbackground=C_BORDER)
        self.cam_canvas.pack(pady=(4,0))
        # Placeholder text before camera starts
        self._cam_placeholder()

        # Gesture badge below camera
        gbadge = tk.Frame(left, bg=C_BG3)
        gbadge.pack(fill="x", pady=(5,0))
        tk.Label(gbadge, text="GESTURE", bg=C_BG3, fg=C_TEXT2,
                 font=("Consolas",7), padx=8, pady=5).pack(side="left")
        self.lbl_g = tk.Label(gbadge, text="—", bg=C_BG3, fg=C_ACCENT,
                               font=("Consolas",12,"bold"), padx=8)
        self.lbl_g.pack(side="left")
        self.lbl_cur = tk.Label(gbadge, text="", bg=C_BG3, fg=C_TEXT2,
                                 font=("Consolas",8), padx=8)
        self.lbl_cur.pack(side="right")

        # ── RIGHT: VOICE + GUIDE ─────────────────────────
        self._slabel(right, "🎤  VOICE CONTROL")
        self.voice_viz = VoiceViz(right)
        self.voice_viz.pack(fill="x", pady=(4,0))

        self.lbl_vs = tk.Label(right, text="Voice off — turn on karo",
                                bg=C_BG, fg=C_TEXT2,
                                font=("Consolas",9), wraplength=200, justify="center")
        self.lbl_vs.pack(pady=(4,0))
        self.lbl_vh = tk.Label(right, text="",
                                bg=C_BG, fg=C_ACCENT2,
                                font=("Consolas",8,"italic"), wraplength=200, justify="center")
        self.lbl_vh.pack()

        tk.Frame(right, bg=C_BORDER, height=1).pack(fill="x", pady=(8,6))
        self._slabel(right, "📖  GESTURE GUIDE")

        self.guide_rows = {}
        guide = [
            ("☝","POINTING",   "Cursor hilao"),
            ("🤏","PINCH",      "Click"),
            ("👍","THUMBS UP",  "Volume Up"),
            ("👎","THUMBS DN",  "Volume Down"),
            ("✊","FIST",       "Play / Pause"),
            ("✌","2 FINGERS",  "YouTube"),
            ("🤟","3 FINGERS",  "Netflix"),
            ("🖐","4 FINGERS",  "Amazon"),
            ("🤘","ROCK",       "Back"),
            ("✋","OPEN HAND",  "Fullscreen"),
        ]
        gf = tk.Frame(right, bg=C_BG)
        gf.pack(fill="x")
        for i,(icon,name,action) in enumerate(guide):
            even = i%2==0
            rb   = C_BG3 if even else C_BG
            row  = tk.Frame(gf, bg=rb)
            row.pack(fill="x")
            tk.Label(row, text=icon, bg=rb, fg=C_TEXT,
                     font=("Segoe UI Emoji",11), width=3, pady=3
                     ).pack(side="left", padx=(6,2))
            tk.Label(row, text=name, bg=rb, fg=C_TEXT,
                     font=("Consolas",8,"bold"), width=10, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=action, bg=rb, fg=C_TEXT2,
                     font=("Consolas",8), anchor="w"
                     ).pack(side="left", padx=4)
            self.guide_rows[name.replace(" ","")] = (row, rb, i)

        # ── STATS ────────────────────────────────────────
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x", padx=14, pady=(8,0))
        sf = tk.Frame(self.root, bg=C_BG2)
        sf.pack(fill="x")
        self.st_g = self._stat(sf, "GESTURES", 0)
        tk.Frame(sf, bg=C_BORDER, width=1).grid(row=0,column=1,sticky="ns",pady=4)
        self.st_v = self._stat(sf, "VOICE CMDS", 2)
        tk.Frame(sf, bg=C_BORDER, width=1).grid(row=0,column=3,sticky="ns",pady=4)
        self.st_a = self._stat(sf, "ACTIONS", 4)
        for c in (0,2,4): sf.columnconfigure(c, weight=1)

        # ── LAST ACTION ──────────────────────────────────
        af = tk.Frame(self.root, bg=C_BG3)
        af.pack(fill="x", padx=14, pady=(0,0))
        tk.Label(af, text="LAST ACTION", bg=C_BG3, fg=C_TEXT3,
                 font=("Consolas",7), padx=10, pady=6).pack(side="left")
        self.lbl_act = tk.Label(af, text="—", bg=C_BG3, fg=C_TEXT,
                                 font=("Consolas",11,"bold"), padx=8)
        self.lbl_act.pack(side="left")
        self.lbl_src = tk.Label(af, text="", bg=C_BG3, fg=C_TEXT2,
                                 font=("Consolas",8))
        self.lbl_src.pack(side="right", padx=10)

        # ── LOG ──────────────────────────────────────────
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x", padx=14)
        lf = tk.Frame(self.root, bg=C_BG)
        lf.pack(fill="both", expand=True, padx=14, pady=(4,10))
        self._slabel(lf, "📋  ACTIVITY LOG")
        self.log_txt = tk.Text(lf, height=5, bg=C_BG2, fg=C_TEXT2,
                                font=("Consolas",8), relief="flat",
                                state="disabled", wrap="word")
        self.log_txt.tag_config("g", foreground=C_ACCENT)
        self.log_txt.tag_config("v", foreground=C_ACCENT2)
        self.log_txt.tag_config("s", foreground=C_TEXT2)
        self.log_txt.tag_config("e", foreground=C_ACCENT3)
        self.log_txt.pack(fill="both", expand=True, pady=(4,0))

        tk.Frame(self.root, bg=C_ACCENT2, height=2).pack(fill="x", side="bottom")
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    # ─────────────────────────────────────────────────────
    # WIDGETS HELPERS
    # ─────────────────────────────────────────────────────
    def _slabel(self, parent, text):
        f = tk.Frame(parent, bg=C_BG)
        f.pack(fill="x")
        tk.Label(f, text=text, bg=C_BG, fg=C_TEXT3,
                 font=("Consolas",8,"bold")).pack(side="left", padx=0, pady=2)
        tk.Frame(f, bg=C_BORDER, height=1).pack(side="left",fill="x",expand=True,padx=6)

    def _tbtn(self, p, text, active, cmd, col):
        bg = "#0d2020" if active else C_BG3
        fg = C_ACCENT  if active else C_TEXT2
        b  = tk.Button(p, text=text, bg=bg, fg=fg,
                       font=("Consolas",9,"bold"), relief="flat", bd=0,
                       pady=8, cursor="hand2", command=cmd,
                       activebackground=C_BG3, activeforeground=C_ACCENT)
        b.grid(row=0, column=col, sticky="ew", padx=3)
        return b

    def _stat(self, parent, label, col):
        f = tk.Frame(parent, bg=C_BG2, pady=6)
        f.grid(row=0, column=col, sticky="ew")
        v = tk.Label(f, text="0", bg=C_BG2, fg=C_ACCENT,
                     font=("Consolas",18,"bold"))
        v.pack()
        tk.Label(f, text=label, bg=C_BG2, fg=C_TEXT3,
                 font=("Consolas",7)).pack()
        return v

    def _cam_placeholder(self):
        self.cam_canvas.delete("all")
        W = CAM_W; H = CAM_H//1
        cx = W//2; cy = H//2
        self.cam_canvas.create_rectangle(0,0,W,H, fill="#06060f", outline="")
        for r in (40,80,120):
            self.cam_canvas.create_oval(cx-r,cy-r,cx+r,cy+r,
                                        outline=C_BORDER, width=1, dash=(4,8))
        self.cam_canvas.create_line(cx-20,cy,cx+20,cy, fill=C_BORDER, width=1)
        self.cam_canvas.create_line(cx,cy-20,cx,cy+20, fill=C_BORDER, width=1)
        self.cam_canvas.create_text(cx,cy+130,
            text="📷  Gesture ON karo — camera chalu hoga",
            fill=C_TEXT3, font=("Consolas",9))

    # ─────────────────────────────────────────────────────
    # CAMERA FRAME POLL — Tkinter thread safe update
    # ─────────────────────────────────────────────────────
    def _poll_frame(self):
        with self._frame_lock:
            frame = self._latest_frame
        if frame is not None:
            try:
                rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img   = Image.fromarray(rgb)
                # Resize to fit canvas exactly
                img   = img.resize((CAM_W, CAM_H), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.cam_canvas.delete("all")
                self.cam_canvas.create_image(0, 0, anchor="nw", image=photo)
                self.cam_canvas._photo = photo   # keep reference!
            except Exception:
                pass
        self.root.after(33, self._poll_frame)   # 30fps poll

    # ─────────────────────────────────────────────────────
    # LOG POLL
    # ─────────────────────────────────────────────────────
    def _poll_log(self):
        while not self.log_q.empty():
            msg, tag = self.log_q.get_nowait()
            self.log_txt.configure(state="normal")
            self.log_txt.insert("1.0", msg+"\n", tag)
            lines = int(self.log_txt.index("end-1c").split(".")[0])
            if lines > 150:
                self.log_txt.delete(f"{lines-50}.0","end")
            self.log_txt.configure(state="disabled")
        self.root.after(80, self._poll_log)

    def _log(self, msg, tag="s"):
        t  = time.strftime("%H:%M:%S")
        px = {"g":"✋","v":"🎤","s":"●","e":"✗"}.get(tag,"•")
        self.log_q.put((f"[{t}] {px} {msg}", tag))

    def ui(self, fn): self.root.after(0, fn)

    # ─────────────────────────────────────────────────────
    # TOGGLES
    # ─────────────────────────────────────────────────────
    def toggle_gesture(self):
        if self.gesture_on:
            self.gesture_on = False
            self._bset(self.btn_g,"✋  GESTURE",False)
            self.ui(self._cam_placeholder)
            self.ui(lambda: self.lbl_g.configure(text="—",fg=C_TEXT2))
            self._log("Gesture band","s")
        else:
            self.gesture_on = True
            self._bset(self.btn_g,"✋  GESTURE",True)
            self._log("Gesture chalu — haath dikhao","g")
            threading.Thread(target=self._gesture_loop, daemon=True).start()

    def toggle_voice(self):
        if self.voice_on:
            self.voice_on = False
            self._bset(self.btn_v,"🎤  VOICE",False)
            self.ui(lambda: self.voice_viz.deactivate("Voice off"))
            self.ui(lambda: self.lbl_vs.configure(text="Voice off — turn on karo",fg=C_TEXT2))
            self._log("Voice band","s")
        else:
            if not SPEECH_OK:
                self._log("pip install SpeechRecognition pyaudio","e"); return
            self.voice_on = True
            self._bset(self.btn_v,"🎤  VOICE",True,C_ACCENT2,"#0a0020")
            self._log("Voice chalu — bolo command","v")
            threading.Thread(target=self._voice_loop, daemon=True).start()

    def toggle_cursor(self):
        self.cursor_mode = not self.cursor_mode
        self.was_pinching = False
        self._bset(self.btn_c,"🖱  CURSOR",self.cursor_mode)
        self._log(f"Cursor {'ON' if self.cursor_mode else 'OFF'}","s")

    def _bset(self, btn, text, on, fg_on=None, bg_on=None):
        btn.configure(text=text,
                      bg=bg_on or ("#0d2020" if on else C_BG3),
                      fg=fg_on or (C_ACCENT  if on else C_TEXT2))

    def _highlight_guide(self, key):
        for k,(row,def_bg,i) in self.guide_rows.items():
            if k == key:
                row.configure(bg="#0c1e14")
                for w in row.winfo_children():
                    try: w.configure(bg="#0c1e14", fg=C_ACCENT)
                    except: pass
            else:
                row.configure(bg=def_bg)
                for w in row.winfo_children():
                    try: w.configure(bg=def_bg)
                    except: pass

    # ─────────────────────────────────────────────────────
    # GESTURE LOOP
    # ─────────────────────────────────────────────────────
    def _gesture_loop(self):
        mp_h = mp.solutions.hands
        hnds = mp_h.Hands(max_num_hands=1, model_complexity=1,
                          min_detection_confidence=0.7,
                          min_tracking_confidence=0.65)
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)
        cap.set(cv2.CAP_PROP_FPS, 30)
        if not cap.isOpened():
            self._log("Camera nahi mila!","e")
            self.gesture_on = False
            return
        self._log("Camera chalu ✅","s")

        while self.gesture_on:
            ret, frame = cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res   = hnds.process(rgb)

            g = None
            if res.multi_hand_landmarks:
                lm_obj = res.multi_hand_landmarks[0].landmark

                # Cursor control via index tip
                if self.cursor_mode:
                    fx = lm_obj[8].x; fy = lm_obj[8].y
                    self.sx += (fx-self.sx)*SMOOTHING
                    self.sy += (fy-self.sy)*SMOOTHING
                    px = int(self.sx*SW); py = int(self.sy*SH)
                    pyautogui.moveTo(px,py,duration=0)
                    self.ui(lambda px=px,py=py:
                            self.lbl_cur.configure(text=f"({px},{py})"))

                g = detect_gesture(lm_obj)

                frame = draw_landmarks_on_frame(frame, lm_obj, g)

                gtext = f"{GESTURE_ICONS.get(g,'')}  {g.replace('_',' ')}" if g else "—"
                self.ui(lambda t=gtext,gg=g:
                        self.lbl_g.configure(text=t,
                        fg=C_ACCENT if gg else C_TEXT2))

                if g:
                    gkey = g.replace("_","")
                    self.ui(lambda k=gkey: self._highlight_guide(k))

                if self.cursor_mode:
                    is_p = (g=="PINCH")
                    if is_p and not self.was_pinching:
                        self.was_pinching = True
                        pyautogui.click()
                        self._fire_action("PINCH → Click","g")
                        self._log("Pinch → Click","g")
                    elif not is_p:
                        self.was_pinching = False
                    if g and g not in ("PINCH","POINTING","OPEN_HAND"):
                        self._steady(g)
                else:
                    if g:
                        if g==self.last_g: self.g_frames+=1
                        else: self.last_g=g; self.g_frames=1
                        if self.g_frames>=GESTURE_HOLD and not self.g_cool:
                            self.g_frames=0; self._fire(g)
                    else:
                        self.last_g=""; self.g_frames=0
            else:
                self.ui(lambda: self.lbl_g.configure(text="— haath nahi mila",fg=C_TEXT3))
                self.ui(lambda: self.lbl_cur.configure(text=""))
                self.was_pinching = False
                # Still show plain frame
                cv2.putText(frame,"No hand detected",(8,20),
                            cv2.FONT_HERSHEY_SIMPLEX,0.5,(40,40,60),1)

            with self._frame_lock:
                self._latest_frame = frame.copy()

        cap.release(); hnds.close()
        self._log("Camera band","s")
        with self._frame_lock:
            self._latest_frame = None
        self.ui(self._cam_placeholder)

    def _steady(self,g):
        if g==self.sg_last: self.sg_frames+=1
        else: self.sg_last=g; self.sg_frames=1
        if self.sg_frames>=20 and not self.g_cool:
            self.sg_frames=0; self._fire(g)

    def _fire(self,g):
        if self.g_cool: return
        action = GESTURE_MAP.get(g)
        if not action: return
        self.g_cool = True
        threading.Timer(GESTURE_COOL, lambda: setattr(self,"g_cool",False)).start()
        result = execute(action)
        threading.Thread(target=broadcast_log, args=("gesture",g,result), daemon=True).start()
        self.cnt_g+=1; self.cnt_a+=1
        self._fire_action(f"{GESTURE_ICONS.get(g,'')} {g} → {result}","g")
        self._log(f"{g} → {result}","g")
        self.ui(lambda: self.st_g.configure(text=str(self.cnt_g)))
        self.ui(lambda: self.st_a.configure(text=str(self.cnt_a)))

    def _fire_action(self,text,tag):
        col = {
            "g": C_ACCENT,
            "v": C_ACCENT2,
            "s": C_TEXT,
        }.get(tag, C_TEXT)
        src = {"g":"[gesture]","v":"[voice]","s":"[system]"}.get(tag,"")
        self.ui(lambda: self.lbl_act.configure(text=text, fg=col))
        self.ui(lambda: self.lbl_src.configure(text=src, fg=C_TEXT3))
        self.ui(lambda: self.lbl_pill.configure(
            text=f"● {tag.upper() if tag != 'g' else 'GESTURE'}",
            fg=col))
        self.root.after(2500, lambda: self.ui(
            lambda: self.lbl_pill.configure(text="● IDLE", fg=C_TEXT2)))

    # ─────────────────────────────────────────────────────
    # VOICE LOOP
    # ─────────────────────────────────────────────────────
    def _voice_loop(self):
        recognizer = sr.Recognizer()
        mic        = sr.Microphone()
        with mic as src:
            recognizer.adjust_for_ambient_noise(src, duration=0.6)
        recognizer.energy_threshold = 3500
        self._log("Mic ready — bolo command","v")

        while self.voice_on:
            try:
                with mic as src:
                    self.ui(lambda: self.voice_viz.activate("🎤  Sun raha hun..."))
                    self.ui(lambda: self.lbl_vs.configure(
                        text="🎤  Sun raha hun...", fg=C_ACCENT2))
                    audio = recognizer.listen(src, timeout=6, phrase_time_limit=6)

                self.ui(lambda: self.voice_viz.set_label("⏳  Samajh raha hun..."))
                self.ui(lambda: self.lbl_vs.configure(
                    text="⏳  Samajh raha hun...", fg=C_YELLOW))

                text   = recognizer.recognize_google(audio, language="en-IN").strip()
                self._log(f'Suna: "{text}"',"v")
                self.ui(lambda t=text: self.lbl_vh.configure(text=f'"{t}"'))

                action,extra = parse_voice(text)

                if action=="SEARCH" and extra:
                    result = do_search(extra)
                    self._finish_voice(f"🔍 {result}","v")
                elif action:
                    result = execute(action)
                    threading.Thread(target=broadcast_log,
                                     args=("voice",text,result), daemon=True).start()
                    self.cnt_v+=1; self.cnt_a+=1
                    self._finish_voice(result,"v")
                    self.ui(lambda: self.st_v.configure(text=str(self.cnt_v)))
                    self.ui(lambda: self.st_a.configure(text=str(self.cnt_a)))
                else:
                    self._finish_voice(f'❓ Samajh nahi aaya',"s")
                    self._log(f"Unknown: {text}","e")
                time.sleep(1.2)

            except sr.WaitTimeoutError:
                self.ui(lambda: self.voice_viz.activate("🎤  Bol do..."))
                self.ui(lambda: self.lbl_vs.configure(text="🎤  Bol do...",fg=C_TEXT2))
            except sr.UnknownValueError:
                self.ui(lambda: self.lbl_vs.configure(text="❓  Dobara bolo",fg=C_TEXT2))
                self.ui(lambda: self.voice_viz.deactivate("❓  Clear voice mein bolo"))
            except sr.RequestError:
                self.ui(lambda: self.lbl_vs.configure(text="❌  Network error",fg=C_ACCENT3))
                time.sleep(2)
            except Exception as e:
                self.ui(lambda e=e: self.lbl_vs.configure(text=f"❌ {e}",fg=C_ACCENT3))
                time.sleep(1)

        self.ui(lambda: self.voice_viz.deactivate("Voice off"))
        self.ui(lambda: self.lbl_vs.configure(text="Voice off — turn on karo",fg=C_TEXT2))

    def _finish_voice(self,result,tag):
        self._fire_action(result,tag)
        self._log(f"Voice → {result}",tag)
        self.ui(lambda: self.voice_viz.deactivate("✅  Done"))
        self.ui(lambda r=result: self.lbl_vs.configure(text=r, fg=C_GREEN))
        self.root.after(2000, lambda: self.ui(lambda: self.lbl_vs.configure(
            text="🎤  Ready — bolo" if self.voice_on else "Voice off",
            fg=C_ACCENT2 if self.voice_on else C_TEXT2)))

    def _close(self):
        self.gesture_on=False; self.voice_on=False
        time.sleep(0.35); self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    TouchlessApp().run()