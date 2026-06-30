# 🖐️ Touchless TV Control

An AI-powered desktop application that allows users to control YouTube, Netflix, Spotify, system volume, brightness, mouse, and Windows applications using **real-time hand gestures** and **voice commands**.

The project uses **MediaPipe** for hand tracking, **OpenCV** for computer vision, **SpeechRecognition** for voice commands, and **PyAutoGUI** to control the operating system.

---

## 🚀 Features

- 🎯 Real-time hand gesture recognition
- 🎤 Voice command recognition
- 🖱️ Mouse movement using hand tracking
- 👆 Pinch gesture for mouse click
- 🔊 System volume control
- ⏯️ Play / Pause media
- 📺 Open YouTube, Netflix and Amazon Prime
- 🖥️ Fullscreen control
- 🌐 Browser navigation
- 📊 Live activity logging
- 🔌 Flask REST API
- 💻 Web dashboard for monitoring
- ⚡ Works across Windows applications

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- Flask-CORS

### Computer Vision
- OpenCV
- MediaPipe

### Voice Recognition
- SpeechRecognition
- PyAudio

### Automation
- PyAutoGUI
- PyWin32

### Frontend
- HTML
- CSS
- JavaScript

---

## 🏗️ Project Architecture

```
Webcam
   │
   ▼
OpenCV
   │
   ▼
MediaPipe Hands
   │
   ▼
Gesture Detection
   │
   ▼
Action Controller
   │
   ▼
Windows / Browser Control


Microphone
   │
   ▼
SpeechRecognition
   │
   ▼
Voice Command Parser
   │
   ▼
Action Controller
```

---

## 📂 Project Structure

```
touchless-tv-control/

├── backend/
│   ├── api/
│   ├── core/
│   ├── gesture/
│   ├── services/
│   ├── voice/
│   └── app.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   └── config.js
│
├── desktop/
│   ├── main.py
│   └── touchless_dashboard.html
│
├── .env
└── README.md
```

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
| 🤘 Rock Gesture | Back |
| ✋ Open Palm | Fullscreen |

---

## 🎤 Supported Voice Commands

Examples:

```
Open YouTube
Open Netflix
Open Spotify
Volume Up
Volume Down
Mute
Play
Pause
Next
Previous
Fullscreen
Scroll Up
Scroll Down
New Tab
Close Tab
Refresh
Search ChatGPT
Search Python Tutorial
Shutdown
Restart
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/Saur1234567/touchless-tv-control.git

cd touchless-tv-control
```

### Install Dependencies

```bash
pip install -r backend/requirements.txt
pip install -r desktop/requirements.txt
```

### Run Backend

```bash
cd backend

python run.py
```

### Run Desktop Application

```bash
cd desktop

python main.py
```

Open **frontend/index.html** in your browser to access the dashboard.

---

## 📸 Screenshots

Add screenshots inside a folder named **screenshots**.

Example:

```
screenshots/

dashboard.png

gesture.png

voice.png
```

Then include them like this:

```md
![Dashboard](screenshots/dashboard.png)

![Gesture Detection](screenshots/gesture.png)

![Voice Control](screenshots/voice.png)
```

---

## 🔮 Future Improvements

- AI-based custom gesture training
- Hindi voice command support
- Multi-hand gesture recognition
- Smart TV integration
- Mobile companion application
- Face authentication
- Gesture customization

---

## 👨‍💻 Author

**Saurav Kumar**

GitHub: https://github.com/Saur1234567

---

## ⭐ If you like this project

Please consider giving this repository a **Star ⭐**.
