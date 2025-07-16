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
        "You must act like real human."
        "Make sure your reply sounds human-like and consistent with the emotion."
        "You don't need to say much in every answer. Sometimes, ask questions that make the user think deeply. "
        "You almost need to say 1~2 sentense in every answer. but If you need to answer in more detail, say 2~4 sentense in max"
        "Use simple English"
    ),
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


@app.route("/image", methods=["POST"])
def image_anaylze():
    data = request.get_json()
    images = data.get("images")
    description = data.get("description")

    param_content = []
    param_content.append({"type": "text", "text": description})
    for image in images:
        param_content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}",
                },
            }
        )

    stream = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[
            {
                "role": "user",
                "content": param_content,
            }
        ],
        stream=True,
    )
    result_text = ""

    for chunk in stream:
        result_text += chunk.choices[0].delta.content or "" if chunk.choices else ""
        print(
            chunk.choices[0].delta.content or "" if chunk.choices else "",
            end="",
            flush=True,
        )
    return jsonify({"reply": result_text})


@app.route("/")
def index():
    return "chatbot is running!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
