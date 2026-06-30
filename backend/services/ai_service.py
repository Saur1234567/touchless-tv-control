def process_ai_command(text: str) -> str:
    if not text:
        return "UNKNOWN"
    text = text.lower().strip()

    # ── Power ─────────────────────────────────────────────────
    if any(w in text for w in ["turn off tv","power off","switch off tv","tv off"]):
        return "TV_POWER_OFF"
    if any(w in text for w in ["turn on tv","power on","switch on tv","tv on"]):
        return "TV_POWER_ON"
    if "sleep" in text and "timer" in text:
        return "SLEEP_TIMER"
    if "standby" in text:
        return "STANDBY"

    # ── Volume ────────────────────────────────────────────────
    if any(w in text for w in ["volume up","increase volume","louder","turn up"]):
        return "VOLUME_UP"
    if any(w in text for w in ["volume down","decrease volume","quieter","turn down","lower volume"]):
        return "VOLUME_DOWN"
    if any(w in text for w in ["mute","silence","quiet"]):
        return "MUTE"
    if "unmute" in text or "sound on" in text:
        return "UNMUTE"
    if "max volume" in text or "full volume" in text:
        return "VOLUME_MAX"
    if "min volume" in text or "minimum volume" in text:
        return "VOLUME_MIN"

    # ── Channels ──────────────────────────────────────────────
    if any(w in text for w in ["channel up","next channel","channel forward"]):
        return "CHANNEL_UP"
    if any(w in text for w in ["channel down","previous channel","channel back"]):
        return "CHANNEL_DOWN"
    if "last channel" in text or "previous channel" in text:
        return "CHANNEL_LAST"

    # ── Playback ──────────────────────────────────────────────
    if "fast forward" in text or "forward" in text:
        return "FAST_FORWARD"
    if "rewind" in text or "go back" in text:
        return "REWIND"
    if any(w in text for w in ["pause","stop playing"]):
        return "PAUSE"
    if any(w in text for w in ["play","resume","continue"]):
        return "PLAY"
    if "replay" in text or "restart" in text:
        return "REPLAY"
    if "next episode" in text or "next" in text:
        return "NEXT"
    if "previous episode" in text or "previous" in text:
        return "PREVIOUS"
    if "subtitle" in text or "caption" in text:
        return "SUBTITLE"
    if "language" in text or "audio track" in text:
        return "AUDIO_TRACK"

    # ── Navigation ────────────────────────────────────────────
    if "go up" in text or "arrow up" in text or "move up" in text:
        return "NAV_UP"
    if "go down" in text or "arrow down" in text or "move down" in text:
        return "NAV_DOWN"
    if "go left" in text or "arrow left" in text or "move left" in text:
        return "NAV_LEFT"
    if "go right" in text or "arrow right" in text or "move right" in text:
        return "NAV_RIGHT"
    if any(w in text for w in ["select","ok","confirm","enter","press ok"]):
        return "SELECT"
    if any(w in text for w in ["back","go back","return"]):
        return "BACK"
    if any(w in text for w in ["home","home screen","main menu"]):
        return "HOME"
    if any(w in text for w in ["menu","settings menu","open menu"]):
        return "MENU"
    if "exit" in text:
        return "EXIT"

    # ── Smart Features ────────────────────────────────────────
    if "search" in text or "find" in text:
        return "SEARCH"
    if "record" in text:
        return "RECORD"
    if "screenshot" in text or "capture" in text:
        return "SCREENSHOT"
    if "cast" in text or "screen mirror" in text:
        return "SCREEN_MIRROR"
    if "bluetooth" in text:
        return "BLUETOOTH"
    if "wifi" in text or "wi-fi" in text:
        return "WIFI_SETTINGS"
    if "picture mode" in text or "display mode" in text:
        return "PICTURE_MODE"
    if "game mode" in text:
        return "GAME_MODE"
    if "cinema mode" in text or "movie mode" in text:
        return "CINEMA_MODE"
    if "night mode" in text or "dark mode" in text:
        return "NIGHT_MODE"
    if "zoom in" in text or "zoom+" in text:
        return "ZOOM_IN"
    if "zoom out" in text or "zoom-" in text:
        return "ZOOM_OUT"

    # ── Input / Source ────────────────────────────────────────
    if "hdmi 1" in text:
        return "HDMI_1"
    if "hdmi 2" in text:
        return "HDMI_2"
    if "hdmi 3" in text:
        return "HDMI_3"
    if any(w in text for w in ["source","input","change input"]):
        return "SOURCE"
    if "usb" in text:
        return "USB"

    # ── Apps / Websites ───────────────────────────────────────
    if "youtube" in text:
        return "OPEN_YOUTUBE"
    if "netflix" in text:
        return "OPEN_NETFLIX"
    if "amazon" in text or "prime" in text:
        return "OPEN_AMAZON"
    if "spotify" in text:
        return "OPEN_SPOTIFY"
    if "google" in text:
        return "OPEN_GOOGLE"
    if "disney" in text:
        return "OPEN_DISNEY"
    if "hotstar" in text:
        return "OPEN_HOTSTAR"
    if "hulu" in text:
        return "OPEN_HULU"
    if "browser" in text or "internet" in text:
        return "OPEN_BROWSER"

    # ── Mouse (laptop control) ────────────────────────────────
    if "right click" in text:
        return "RIGHT_CLICK"
    if "click" in text:
        return "CLICK"
    if "scroll up" in text:
        return "SCROLL_UP"
    if "scroll down" in text:
        return "SCROLL_DOWN"
    if "shutdown" in text or "shut down" in text:
        return "SHUTDOWN"

    return "UNKNOWN"