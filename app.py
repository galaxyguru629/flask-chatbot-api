# app.py
from flask import Flask, request, jsonify
from together import Together
from dotenv import load_dotenv
import os
from memory import get_memory, add_message, reset_memory

# Load API key
load_dotenv()
api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise Exception("Missing TOGETHER_API_KEY in .env")

client = Together(api_key=api_key)
app = Flask(__name__)

# Core chatbot personality
system_prompt = {
    "role": "system",
    "content": (
        "You are Nova, a witty and charming humanlike assistant. "
        "Speak like a real person: casual, warm, sometimes funny. "
        "Use contractions, ask questions back, and keep it light but thoughtful. "
        "Be playful about yourself (e.g. your age, name, etc.)"
    )
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    user_message = data.get("message")

    if not session_id or not user_message:
        return jsonify({"error": "Missing session_id or message"}), 400

    history = get_memory(session_id)

    if not history:  # first message
        history.append(system_prompt)

    add_message(session_id, "user", user_message)

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=history,
            temperature=0.8,
            max_tokens=512,
            top_p=0.9,
        )
        reply = response.choices[0].message.content.strip()
        add_message(session_id, "assistant", reply)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Nova chatbot is running!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
