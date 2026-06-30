from flask import Blueprint, jsonify, request
from services.voice_service import process_voice
from services.gesture_service import process_gesture
from core.logger import log_info, log_error

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/voice", methods=["POST"])
def voice():
    try:
        # Accept ANY body — never crash
        raw  = request.get_data(as_text=True)
        log_info(f"[VOICE RAW] {raw[:200]}")
        data = request.get_json(force=True, silent=True) or {}
        text = str(data.get("text") or "").strip()
        log_info(f"[VOICE TEXT] '{text}'")
        if not text:
            return jsonify({"status": "ok", "action": "Nothing heard"})
        result = process_voice(text)
        return jsonify({"status": "ok", "action": result})
    except Exception as e:
        log_error(f"[VOICE ERROR] {e}")
        return jsonify({"status": "ok", "action": f"Error: {e}"})


@api_bp.route("/gesture", methods=["POST"])
def gesture():
    try:
        raw  = request.get_data(as_text=True)
        log_info(f"[GESTURE RAW] {raw[:100]}")
        data = request.get_json(force=True, silent=True)

        # Handle all payload shapes
        if isinstance(data, list):
            # Direct landmark array
            payload = data
        elif isinstance(data, dict):
            if data.get("action") == "MOVE_CURSOR":
                payload = data                    # cursor dict
            elif "gesture" in data:
                payload = data["gesture"]         # wrapped landmark or string
            else:
                payload = data
        else:
            payload = str(data or "")

        result = process_gesture(payload)
        return jsonify({"status": "ok", "action": result})
    except Exception as e:
        log_error(f"[GESTURE ERROR] {e}")
        return jsonify({"status": "ok", "action": f"Error: {e}"})