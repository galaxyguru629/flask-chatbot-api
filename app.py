from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the API!"})

@app.route("/api/echo", methods=["POST"])
def echo():
    data = request.json
    return jsonify({"you_sent": data})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
