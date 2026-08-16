"""
Trip Currency Budgeter — Flask Server
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)


@app.route("/")
def index():
    """Serve the chat UI."""
    return send_from_directory("static", "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint."""
    return jsonify({"response": "Hello! I'm TripBudgetBuddy. Set up your trip to get started."})


if __name__ == "__main__":
    app.run(debug=True, port=5000)