# 🖥️ Touchless TV Control - Desktop Application

This folder contains the standalone desktop application for the **Touchless TV Control** project.

The desktop application allows users to control their computer using **hand gestures** and **voice commands** through a webcam and microphone.

---

## ✨ Features

- Real-time hand gesture recognition
- Voice command recognition
- Mouse cursor control
- Pinch gesture for mouse click
- System volume control
- Media play / pause
- Browser navigation
- Open YouTube, Netflix and Amazon Prime
- Fullscreen control
- Live activity dashboard

---

## 📁 Files

| File | Description |
|------|-------------|
| `main.py` | Main desktop application |
| `requirements.txt` | Python dependencies |
| `touchless_dashboard.html` | Local dashboard interface |

---

## 📦 Requirements

- Python 3.11+
- Webcam
- Microphone

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run

```bash
python main.py
```

After launching the application:

1. Enable **Gesture Mode**
2. Enable **Voice Mode**
3. Allow camera and microphone access
4. Start controlling your system using gestures or voice commands.

---

## ✋ Supported Gestures

| Gesture | Action |
|----------|--------|
| ☝️ Index Finger | Move Cursor |
| 🤏 Pinch | Left Click |
| 👍 Thumbs Up | Volume Up |
| 👎 Thumbs Down | Volume Down |
| ✊ Fist | Play / Pause |
| ✌️ Two Fingers | Open YouTube |
| 🤟 Three Fingers | Open Netflix |
| 🖐️ Four Fingers | Open Amazon Prime |
| 🤘 Rock Gesture | Browser Back |
| ✋ Open Palm | Fullscreen |

---

## 🎤 Supported Voice Commands

Examples:

- Open YouTube
- Open Netflix
- Open Spotify
- Volume Up
- Volume Down
- Mute
- Play
- Pause
- Next
- Previous
- Fullscreen
- Scroll Up
- Scroll Down
- New Tab
- Close Tab
- Refresh
- Search <query>

---

## 📌 Note

This folder contains only the **desktop application**.

For the complete project architecture, backend services, frontend dashboard, and project documentation, refer to the **root README.md** located in the repository root.
