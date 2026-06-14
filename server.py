"""
server.py  —  serve the note graph and the 3D + hand-tracking viewer
Usage: python server.py   (then open http://localhost:5001)

Port 5001 by default: on macOS, port 5000 is grabbed by the AirPlay
Receiver (Control Center), which returns 403 and shadows Flask.
Override with the PORT env var if you like.
"""
import json
import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
STATIC_DIR = ROOT / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/static")


def _load(name):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/graph")
def graph():
    """Combined payload the front-end consumes.

    3d-force-graph wants `nodes` (with `id`) and `links` (with `source`/`target`).
    Our edges already use source/target ints matching node ids.
    """
    return jsonify({"nodes": _load("nodes.json"), "links": _load("edges.json")})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Serving note graph on http://localhost:{port}")
    app.run(debug=True, port=port)
