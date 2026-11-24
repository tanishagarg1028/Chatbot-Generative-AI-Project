"""
app.py
------
Flask web interface for the chatbot.

Run:
    export OPENAI_API_KEY=sk-...
    python src/app.py
Then open http://localhost:5000
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from flask import Flask, request, jsonify, render_template, session
from chatbot import ChatBot

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# One bot instance per server process for simplicity. For multi-user
# production use, key a dict of ChatBot() instances by session id instead.
bot = ChatBot()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_message = (data or {}).get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        result = bot.reply(user_message)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    bot.reset()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
