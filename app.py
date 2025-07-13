from flask import Flask, request, jsonify
import json
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
        "You must act like real human."
        "Make sure your reply sounds human-like and consistent with the emotion."
        "You don't need to say much in every answer. Sometimes, ask questions that make the user think deeply. "
        "You almost need to say 1~2 sentense in every answer. but If you need to answer in more detail, say 2~4 sentense in max"
        "Use simple English"
    )
}

@app.route("/reset", methods=["POST"])
def reset_chat():
    data = request.get_json()
    session_id = data.get("session_id")
    reset_memory(session_id)
    return jsonify({"reply": "successfully reset"}) 

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id")
    user_message = data.get("message")

    if not session_id or not user_message:
        return jsonify({"error": "Missing session_id or message"}), 400

    add_message(session_id, "user", user_message)
    history = get_limited_memory(session_id, system_prompt)
    print(history)
    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=history,
            temperature=0.8,
            max_tokens=512,
            top_p=0.9,
        )
        raw_reply = response.choices[0].message.content.strip()
        
        add_message(session_id, "assistant", raw_reply)
        return jsonify({"reply": raw_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "chatbot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
