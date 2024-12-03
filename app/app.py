from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def catch_all(path):
    return jsonify({"message": "Hello, World!"}, 200)


if __name__ == "__main__":
    app.run(host="localhost", debug=False)
