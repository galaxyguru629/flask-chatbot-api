from flask import Flask, request, jsonify
from together import Together
import os
from memory import get_limited_memory, add_message, reset_memory

if os.environ.get("RAILWAY_STATIC_URL") is None:
    from dotenv import load_dotenv
    load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")
if not api_key:
    raise Exception("Missing TOGETHER_API_KEY")

client = Together(api_key=api_key)
app = Flask(__name__)

system_prompt = {
    "role": "system",
    "content": (
        "You are Morgan Wells, a 32-year-old AI consultant living in Seattle. "
        "You have a Master’s in Computer Science from University of Washington and 7 years of professional experience in AI and software engineering. "
        "You live an active, mindful lifestyle with interests in hiking, yoga, cooking, and reading sci-fi and philosophy. "
        "Speak naturally, warmly, and with curiosity. Be witty and insightful, often sharing little fun facts or puns. "
        "Remember personal details during conversations and use them naturally. "
        "You communicate like a real, thoughtful person with a deep passion for ethical technology and creativity. "
        "You don't need to say much every answer. Sometimes, ask questions that make the user think deeply. "
        "Use easy English and idioms."
    )
}

@app.route("/reset")
def reset_chat():
    reset_memory()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    user_message = data.get("message")

    if not session_id or not user_message:
        return jsonify({"error": "Missing session_id or message"}), 400

    add_message(session_id, "user", user_message)
    history = get_limited_memory(session_id, system_prompt)

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
    return "chatbot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
