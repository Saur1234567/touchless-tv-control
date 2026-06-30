# 🖐️ Touchless TV Control — AI Gesture & Voice Control System

> Control YouTube, Netflix, Spotify, your TV, and your entire laptop **without touching anything** — just hand gestures and voice commands, powered by computer vision and speech recognition.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange?logo=google)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📺 What Is This?

**Touchless TV Control** is a desktop application that turns your webcam and microphone into a universal remote control. Point your camera at your hand, make a gesture, or simply speak — and it controls whatever window is currently active: a browser tab playing YouTube/Netflix, your laptop's system volume, brightness, or any app on screen.

Unlike a typical browser extension, this is a **real desktop app** — it works system-wide, across any window, any application, any tab. Open it once, and gesture/voice control works everywhere on your screen.

---

## ✨ Key Features

- 🖐️ **Real-time hand tracking** with MediaPipe — see all 21 hand landmarks drawn live on your camera feed, color-coded per finger
- 🎤 **Voice control** in English with an animated waveform visualizer that shows exactly when the mic is listening
- 🖱️ **Gesture-based cursor control** — move your mouse with your index finger, pinch to click
- 📺 **Smart fullscreen logic** — fullscreens the active media window (YouTube/Netflix) if found, otherwise fullscreens the app itself
- 🔊 **System-level media keys** — volume, mute, play/pause work globally without stealing window focus
- 🌐 **Works system-wide** — not limited to a browser tab; controls whatever app/window is active
- 📋 **Live activity log** — every gesture and voice command is logged with a timestamp and result
- 📊 **Built-in stats dashboard** — tracks total gestures, voice commands, and actions executed
- 🔌 **Local Flask API** (`localhost:5000`) — logs every action so a companion web dashboard (`frontend/index.html`) can display them in real time

---

## 🧠 How It Works — Architecture

```
┌──────────────┐      ┌───────────────────┐       ┌───────────────────┐
│   Webcam     │ ───▶│  MediaPipe Hands  │ ───▶  │Gesture Classifier │
│  (OpenCV)    │      │  (21 landmarks)   │       │  (rule-based)     │
└──────────────┘      └───────────────────┘       └────────┬──────────┘
                                                            │
┌──────────────┐      ┌──────────────────┐        ┌─────────▼──────────┐
│  Microphone  │ ───▶ │ Google Speech API │ ───▶ │   Voice Parser     │
│ (SpeechRecog)│      │  (speech→text)    │       │  (keyword match)   │
└──────────────┘      └──────────────────┘        └────────┬───────────┘
                                                            │
                                            ┌───────────────▼────────────────┐
                                            │      execute(action)            │
                                            │  • GLOBAL_KEYS (no focus needed)│
                                            │  • focus_media() + KB (needs    │
                                            │    target window focused)       │
                                            └───────────────┬────────────────┘
                                                            │
                                            ┌───────────────▼────────────────┐
                                            │  pyautogui → system keystrokes  │
                                            │  win32gui → window focus/switch │
                                            └─────────────────────────────────┘
```

**Why this design matters:**
- Volume, mute, and media-track keys are routed through `GLOBAL_KEYS` — these are real hardware-style keys that work regardless of which window has focus, so they **never** accidentally minimize or switch your active window.
- Actions that need a specific app focused (like `FULLSCREEN`, `BACK`, navigation) go through `focus_media()`, which uses Windows' `AttachThreadInput` technique to reliably switch focus from a background thread — a documented workaround for a real Windows API quirk (`SetForegroundWindow` silently fails when called from background threads without it).
- If no matching media window (YouTube/Netflix/Chrome/etc.) is found, the app **never blindly Alt-Tabs** — it either skips the action with a clear log message, or (for `FULLSCREEN`) falls back to fullscreening its own window instead of leaking keystrokes into the wrong place.

---

## 📦 What You Need to Download / Install

### 1. Python

Install **Python 3.11+** from [python.org](https://www.python.org/downloads/) (check "Add Python to PATH" during install).

### 2. Required Python Packages

Open **PowerShell** or **Command Prompt** and run:

```bash
pip install opencv-python mediapipe pyautogui SpeechRecognition pyaudio pywin32 flask flask-cors requests
```

| Package | What it's for |
|---|---|
| `opencv-python` | Reads the webcam feed, draws hand landmarks on the frame |
| `mediapipe` | Google's hand-tracking model — detects all 21 hand landmarks |
| `pyautogui` | Sends keyboard/mouse events to control any app system-wide |
| `SpeechRecognition` | Converts your voice into text using Google's free Speech API |
| `pyaudio` | Lets `SpeechRecognition` access your microphone |
| `pywin32` | Windows API access — window detection, focus switching, fullscreen |
| `flask` + `flask-cors` | Runs a tiny local API server (`localhost:5000`) for activity logging |
| `requests` | Used internally to send logs to the local Flask server |

### If `pyaudio` fails to install on Windows

`pyaudio` sometimes fails with a build error on Windows because it needs a C++ compiler. Use this instead:

```bash
pip install pipwin
pipwin install pyaudio
```

---

## 🚀 How to Run

### Step 1 — Clone or Download

```bash
git clone https://github.com/<your-username>/touchless-tv-control.git
cd touchless-tv-control
```

*(Or download the ZIP from GitHub and extract it.)*

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

*(or run the manual `pip install` command from the section above)*

### Step 3 — Run the App

```bash
python touchless_tv_v2.py
```

A window titled **"Touchless TV Control"** will open in the top-left corner of your screen at full size.

### Step 4 — Turn It On

1. Click **✋ GESTURE** — your webcam turns on, and you'll see your hand with colored landmark dots drawn live
2. Click **🎤 VOICE** — the microphone activates, shown by an animated purple waveform
3. Switch to any browser tab (YouTube, Netflix, Spotify Web) or any other app
4. Start gesturing or speaking — actions apply to whatever window is currently active on your screen

---

## ✋ Gesture Reference

| Gesture | Icon | Action | Notes |
|---|---|---|---|
| Index finger only | ☝️ | Move mouse cursor | Cursor follows your fingertip |
| Pinch (thumb + index) | 🤏 | Click | Click happens at current cursor position |
| Thumbs up | 👍 | Volume Up | Works globally, no window focus needed |
| Thumbs down | 👎 | Volume Down | Works globally, no window focus needed |
| Closed fist | ✊ | Play / Pause | Sends global media play/pause key |
| Two fingers (✌) | ✌️ | Open YouTube | Opens a new tab |
| Three fingers | 🤟 | Open Netflix | Opens a new tab |
| Four fingers | 🖐️ | Open Amazon Prime Video | Opens a new tab |
| Rock sign (🤘) | 🤘 | Back | Browser back navigation |
| Open hand (all 5 fingers spread) | ✋ | Fullscreen | Fullscreens the media window if found, otherwise fullscreens the app itself |

> 💡 Gestures have a short cooldown (~2 seconds) after firing, to prevent accidental repeat triggers.

---

## 🎤 Voice Command Reference

Speak clearly in English. The mic listens continuously while Voice mode is ON.

| Say this | What happens |
|---|---|
| "open youtube" / "open netflix" / "open spotify" | Opens the corresponding site in a new tab |
| "volume up" / "louder" / "turn up" | Increases system volume |
| "volume down" / "quieter" / "turn down" | Decreases system volume |
| "mute" / "unmute" | Toggles system mute |
| "play" / "resume" | Resumes playback |
| "pause" | Pauses playback |
| "next" | Skips to next track |
| "previous" | Goes to previous track |
| "fast forward" | Skips forward in the video |
| "rewind" | Skips backward in the video |
| "fullscreen" / "full screen" | Toggles fullscreen |
| "click" | Clicks at the current cursor position |
| "double click" | Double-clicks |
| "right click" | Right-clicks |
| "scroll up" / "scroll down" | Scrolls the active page |
| "next tab" / "previous tab" | Switches browser tabs |
| "new tab" / "close tab" | Opens/closes a browser tab |
| "go up" / "go down" / "go left" / "go right" | Arrow-key navigation |
| "select" / "ok" / "confirm" / "enter" | Presses Enter |
| "back" | Browser back |
| "home" | Shows desktop |
| "menu" / "escape" | Presses Escape |
| "refresh" / "reload" | Reloads the page |
| "screenshot" | Opens Windows Snip & Sketch |
| "zoom in" / "zoom out" | Zooms the page in/out |
| "copy" / "paste" | Copy/paste clipboard |
| "search for `<query>`" / "search `<query>`" / "find `<query>`" | Searches your query on whatever site is currently active (YouTube, Netflix, Google, etc.) |
| "shutdown" / "shut down" / "power off" | Shuts down the PC (⚠️ use with caution) |
| "restart" | Restarts the PC (⚠️ use with caution) |

---

## 📂 Project Structure

```
touchless-tv-control/
│
├── touchless_tv_v2.py        # ⭐ Main desktop app — run this file
├── requirements.txt          # Python dependencies
│
├── backend/                  # Optional Flask backend (full server architecture)
│   ├── app.py                 # Flask app factory
│   ├── run.py                 # Server entry point
│   ├── config.py              # Environment-based configuration
│   ├── core/
│   │   ├── actions.py          # Cross-platform TV/laptop control functions
│   │   └── logger.py           # Rotating colored logger
│   ├── gesture/
│   │   ├── detector.py         # MediaPipe hand landmark detection
│   │   ├── classifier.py       # Rule-based gesture recognition
│   │   └── gesture_map.json    # Gesture → action mapping
│   ├── voice/
│   │   ├── recognizer.py       # Speech-to-text (Google/Whisper/Sphinx)
│   │   ├── nlp_parser.py       # Hindi + English voice intent parser
│   │   └── wake_word.py        # "Hey TV" wake-word listener
│   ├── services/
│   │   ├── gesture_service.py  # Camera capture + gesture processing loop
│   │   └── voice_service.py    # Combined wake-word + recognizer service
│   └── db/                    # SQLAlchemy models for action logging
│
└── frontend/                  # Optional browser dashboard
    ├── index.html              # Live dashboard UI
    ├── script.js                # SocketIO client logic
    └── assets/styles/main.css   # Dark theme styling
```

> **Note:** `touchless_tv_v2.py` is a fully self-contained desktop app — it does **not** require the `backend/` or `frontend/` folders to run. Those folders contain an alternate, more modular Flask-based architecture for anyone who wants to extend this into a full client-server system.

---

## ⚙️ Configuration & Customization

### Changing Gesture-to-Action Mapping

Edit the `GESTURE_MAP` dictionary near the top of `touchless_tv_v2.py`:

```python
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
```

Change the right-hand value to any action key defined in the `execute()` function to remap a gesture.

### Adding New Voice Commands

Edit the `parse_voice()` function — add a new `if` condition that returns your custom action name, then add a handler for that action inside `execute()`.

### Adjusting Gesture Sensitivity

```python
SMOOTHING    = 0.28   # Cursor movement smoothing (lower = smoother but slower)
GESTURE_HOLD = 15     # Frames a gesture must be held before firing (non-cursor mode)
GESTURE_COOL = 2.0    # Cooldown in seconds between repeated gesture triggers
```

---

## 🛠️ Troubleshooting

**Camera doesn't turn on**
- Make sure no other app (Zoom, Teams, etc.) is currently using your webcam
- Try changing the camera index in the code: `cv2.VideoCapture(0)` → try `1` or `2`

**Voice doesn't recognize anything**
- Check your microphone permissions in Windows Settings → Privacy → Microphone
- `SpeechRecognition` with Google's API requires an active internet connection
- Speak clearly and not too fast; background noise can interfere

**Fullscreen / Back / navigation gestures don't do anything**
- These actions require a **real browser/media window** to be open and matched by title keyword (`youtube`, `netflix`, `chrome`, `firefox`, etc.)
- If no matching window is found, the action is safely skipped — check the **Activity Log** panel in the app for the exact reason
- Make sure `pywin32` installed correctly: `pip show pywin32`

**Window minimizes unexpectedly when I gesture**
- This was a known issue in earlier versions caused by a blind `Alt+Tab` fallback — it's fixed in this version. Make sure you're running the latest `touchless_tv_v2.py`

**`pip install pyaudio` fails with a build error**
- Use the `pipwin` method described in the installation section above

---

## 🤝 Contributing

Pull requests are welcome! Some ideas for extending this project:
- Add more gestures (swipe left/right, two-hand gestures)
- Support Linux/macOS (currently Windows-only due to `pywin32` dependency)
- Add Hindi voice command support (already partially implemented in `backend/voice/nlp_parser.py`)
- Build out the `frontend/` dashboard for remote monitoring