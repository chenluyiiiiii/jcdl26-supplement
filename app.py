"""
app.py — MAon-DAExt Linked Art Toolkit  |  Flask web server

Endpoints:
    GET  /              → serves index.html
    POST /preview       → detect agents from TTL; returns JSON list
    POST /convert       → full conversion; returns JSON list of LA records
    POST /convert-file  → same, but accepts multipart TTL upload
"""

from flask import Flask, request, jsonify, send_from_directory
import json, os, traceback

from converter import convert_ttl, detect_agents

app = Flask(__name__, static_folder=".", static_url_path="")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/preview", methods=["POST"])
def preview():
    """Step 1 – parse TTL, return detected agents with auto-typed Person/Group."""
    data = request.get_json(force=True, silent=True) or {}
    ttl = data.get("ttl", "").strip()
    if not ttl:
        return jsonify({"success": False, "error": "No TTL content provided."}), 400
    try:
        agents = detect_agents(ttl)
        return jsonify({"success": True, "agents": agents})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc),
                        "detail": traceback.format_exc()}), 400


@app.route("/convert", methods=["POST"])
def convert():
    """Step 2 – full conversion with optional agent-type overrides."""
    data = request.get_json(force=True, silent=True) or {}
    ttl = data.get("ttl", "").strip()
    overrides = data.get("agent_overrides", {})   # {uri: "Person"|"Group"}
    if not ttl:
        return jsonify({"success": False, "error": "No TTL content provided."}), 400
    try:
        records = convert_ttl(ttl, overrides)
        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc),
                        "detail": traceback.format_exc()}), 400


@app.route("/convert-file", methods=["POST"])
def convert_file():
    """Alternative: accept a TTL file upload via multipart/form-data."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded."}), 400
    f = request.files["file"]
    ttl = f.read().decode("utf-8")
    overrides_raw = request.form.get("agent_overrides", "{}")
    try:
        overrides = json.loads(overrides_raw)
    except Exception:
        overrides = {}
    try:
        records = convert_ttl(ttl, overrides)
        return jsonify({"success": True, "records": records, "count": len(records)})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc),
                        "detail": traceback.format_exc()}), 400


if __name__ == "__main__":
    print("\n┌─────────────────────────────────────────────────┐")
    print("│  MAon-DAExt → Linked Art Converter  |  localhost:5050 │")
    print("└─────────────────────────────────────────────────┘")
    print("  Open http://localhost:5050 in your browser.\n")
    app.run(debug=False, port=5050)
