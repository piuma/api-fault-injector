from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Abilita CORS per permettere al frontend di comunicare con il backend

# Sample data
data = {"message": "Hello, World!"}


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path):
    if request.method == "POST":
        new_message = request.json.get("message")
        if new_message:
            data["message"] = new_message
            return jsonify(data), 200
        return jsonify({"error": "Invalid input"}), 200
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=False)
