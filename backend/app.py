from flask import Flask, jsonify
from flask_cors import CORS
from api.routes import api_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={
    r"/api/*":       {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]},
    r"/socket.io/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}
})

    app.register_blueprint(api_bp)

    @app.route("/")
    def home():
        return jsonify({"status": "Backend running 🚀"})

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)