import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG    = os.getenv("DEBUG", "true").lower() == "true"
    PORT     = int(os.getenv("PORT", 5000))
    SECRET   = os.getenv("SECRET_KEY", "dev-secret")

    VALID_GESTURES = [
        "SWIPE_LEFT", "SWIPE_RIGHT",
        "SCROLL_UP",  "SCROLL_DOWN",
        "FIST", "OPEN_HAND", "PINCH",
        "THUMBS_UP", "THUMBS_DOWN",
        "TWO", "THREE", "FOUR",
    ]