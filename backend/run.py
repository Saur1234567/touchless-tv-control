"""
Entry point.  Choose how to run:

  python run.py          →  plain REST (Flask dev server)
  python run.py socket   →  REST + WebSocket (SocketIO)
"""
import sys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "rest"

    if mode == "socket":
        from socket_server import socketio, flask_app
        print("🚀 Running with WebSocket support on :5000")
        socketio.run(flask_app, debug=True, port=5000, allow_unsafe_werkzeug=True)
    else:
        from app import app
        print("🚀 Running REST only on :5000")
        app.run(debug=True, port=5000)