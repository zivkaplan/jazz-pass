from flask import Flask, jsonify, request, send_file
from generate import generate_wav

app = Flask(__name__)


@app.route("/generate", methods=["GET"])
def get_new():
    path = generate_wav()
    return send_file(path)
