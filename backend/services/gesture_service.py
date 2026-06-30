from core.actions import execute_action
from gesture.gesture import GestureRecognizer
from core.logger import log_info

_rec = GestureRecognizer()

# Gesture → Action mapping
MAP = {
    "FIST":          "SELECT",
    "OPEN_HAND":     "PAUSE",
    "THUMBS_UP":     "VOLUME_UP",
    "THUMBS_DOWN":   "VOLUME_DOWN",
    "TWO_FINGERS":   "OPEN_YOUTUBE",
    "THREE_FINGERS": "OPEN_NETFLIX",
    "FOUR_FINGERS":  "OPEN_AMAZON",
    "POINTING":      "MOVE_CURSOR",
    "PINCH":         "CLICK",
    "ROCK":          "BACK",
    # string commands from quick buttons
    "VOLUME_UP":     "VOLUME_UP",
    "VOLUME_DOWN":   "VOLUME_DOWN",
    "MUTE":          "MUTE",
    "UNMUTE":        "UNMUTE",
    "VOLUME_MAX":    "VOLUME_MAX",
    "VOLUME_MIN":    "VOLUME_MIN",
    "CHANNEL_UP":    "CHANNEL_UP",
    "CHANNEL_DOWN":  "CHANNEL_DOWN",
    "CHANNEL_LAST":  "CHANNEL_LAST",
    "PLAY":          "PLAY",
    "PAUSE":         "PAUSE",
    "NEXT":          "NEXT",
    "PREVIOUS":      "PREVIOUS",
    "FAST_FORWARD":  "FAST_FORWARD",
    "REWIND":        "REWIND",
    "FULLSCREEN":    "FULLSCREEN",
    "SUBTITLE":      "SUBTITLE",
    "NAV_UP":        "NAV_UP",
    "NAV_DOWN":      "NAV_DOWN",
    "NAV_LEFT":      "NAV_LEFT",
    "NAV_RIGHT":     "NAV_RIGHT",
    "SELECT":        "SELECT",
    "BACK":          "BACK",
    "HOME":          "HOME",
    "MENU":          "MENU",
    "EXIT":          "EXIT",
    "CLICK":         "CLICK",
    "DOUBLE_CLICK":  "DOUBLE_CLICK",
    "RIGHT_CLICK":   "RIGHT_CLICK",
    "SCROLL_UP":     "SCROLL_UP",
    "SCROLL_DOWN":   "SCROLL_DOWN",
    "ZOOM_IN":       "ZOOM_IN",
    "ZOOM_OUT":      "ZOOM_OUT",
    "SEARCH":        "SEARCH",
    "SCREENSHOT":    "SCREENSHOT",
    "SCREEN_MIRROR": "SCREEN_MIRROR",
    "RECORD":        "RECORD",
    "PICTURE_MODE":  "PICTURE_MODE",
    "GAME_MODE":     "GAME_MODE",
    "CINEMA_MODE":   "CINEMA_MODE",
    "NIGHT_MODE":    "NIGHT_MODE",
    "BLUETOOTH":     "BLUETOOTH",
    "HDMI_1":        "HDMI_1",
    "HDMI_2":        "HDMI_2",
    "HDMI_3":        "HDMI_3",
    "SOURCE":        "SOURCE",
    "USB":           "USB",
    "OPEN_YOUTUBE":  "OPEN_YOUTUBE",
    "OPEN_NETFLIX":  "OPEN_NETFLIX",
    "OPEN_AMAZON":   "OPEN_AMAZON",
    "OPEN_SPOTIFY":  "OPEN_SPOTIFY",
    "OPEN_GOOGLE":   "OPEN_GOOGLE",
    "OPEN_DISNEY":   "OPEN_DISNEY",
    "OPEN_HOTSTAR":  "OPEN_HOTSTAR",
    "OPEN_HULU":     "OPEN_HULU",
    "OPEN_BROWSER":  "OPEN_BROWSER",
    "TV_POWER_OFF":  "TV_POWER_OFF",
    "TV_POWER_ON":   "TV_POWER_ON",
    "STANDBY":       "STANDBY",
    "SLEEP_TIMER":   "SLEEP_TIMER",
    "SHUTDOWN":      "SHUTDOWN",
}


def process_gesture(payload) -> str:
    # ── Cursor move dict ──────────────────────────────────────
    if isinstance(payload, dict):
        if payload.get("action") == "MOVE_CURSOR":
            return execute_action("MOVE_CURSOR", {
                "x": float(payload.get("x", 0.5)),
                "y": float(payload.get("y", 0.5))
            })
        return "Invalid payload"

    # ── Landmark list from MediaPipe ──────────────────────────
    if isinstance(payload, list) and len(payload) == 21:
        gesture = _rec.recognize(payload)
        if not gesture:
            return "No gesture detected"
        log_info(f"✋ Recognized: {gesture}")
        action = MAP.get(gesture)
        if not action:
            return f"Gesture not mapped: {gesture}"
        return execute_action(action)

    # ── String from quick buttons ─────────────────────────────
    if isinstance(payload, str):
        key = payload.strip().upper().replace("-","_").replace(" ","_")
        action = MAP.get(key, key)   # fall through to raw action name
        log_info(f"🖱 Button: {key} → {action}")
        return execute_action(action)

    return "Unknown payload type"