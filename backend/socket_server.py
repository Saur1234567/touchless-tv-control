"""
WebSocket server for real-time gesture/voice streaming.
Run this file directly:  python socket_server.py
The REST API (app.py) is embedded here via create_app().
"""
from flask_socketio import SocketIO, emit
from services.gesture_service import process_gesture
from services.voice_service import process_voice
from app import create_app

flask_app = create_app()
socketio = SocketIO(flask_app, cors_allowed_origins=["http://127.0.0.1:5500", "http://localhost:5500"], async_mode="threading")


@socketio.on("connect")
def on_connect():
    print("✅ Client connected")
    emit("connected", {"msg": "Connected to Touchless TV Control"})


@socketio.on("disconnect")
def on_disconnect():
    print("❌ Client disconnected")


@socketio.on("voice_command")
def handle_voice(data):
    """data = { "text": "volume up" }"""
    text = data.get("text", "")
    result = process_voice(text)
    emit("response", {"type": "voice", "action": result})

    # ✅ YAHAN ADD KARO — sab connected clients ko broadcast
    socketio.emit("live_log", {
        "source": "voice",
        "action": text,        # jo bola gaya
        "result": result       # jo hua
    })


@socketio.on("gesture_command")
def handle_gesture(data):
    """
    data = { "gesture": "SWIPE_LEFT" }
         or { "gesture": [ {x,y,z}, ... ] }
    """
    gesture_payload = data.get("gesture")
    result = process_gesture(gesture_payload)
    emit("response", {"type": "gesture", "action": result})

    # ✅ YAHAN ADD KARO — sab connected clients ko broadcast
    gesture_name = gesture_payload if isinstance(gesture_payload, str) else "HAND"
    socketio.emit("live_log", {
        "source": "gesture",
        "action": gesture_name,   # kaun sa gesture
        "result": result          # jo hua
    })

@flask_app.route("/api/log", methods=["POST"])
def receive_log():
    from flask import request, jsonify
    data = request.get_json()
    socketio.emit("live_log", {
        "source": data.get("source", "gesture"),
        "action": data.get("action", ""),
        "result": data.get("result", "")
    })
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("🚀 SocketIO server on http://localhost:5000")
    socketio.run(flask_app, debug=True, port=5000, allow_unsafe_werkzeug=True)