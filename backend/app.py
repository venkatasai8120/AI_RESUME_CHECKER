from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from analyzer import gap_for_role_from_text
from matcher import compute_jd_resume_match

# Optional: resume upload feature
try:
    from resume_parser import extract_text_from_uploaded_file
except Exception:
    extract_text_from_uploaded_file = None

# Optional: AI suggestions endpoint
try:
    from ai_suggester import generate_ats_bullets
except Exception:
    generate_ats_bullets = None


app = Flask(__name__)
CORS(app)

# -----------------------------
# Robust paths (works on Render)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent          # .../backend
PROJECT_DIR = BASE_DIR.parent                      # .../ (repo root)
DATA_DIR = PROJECT_DIR / "data"
FRONTEND_DIR = PROJECT_DIR / "frontend"
ASSETS_DIR = FRONTEND_DIR / "assets"

SKILLS_MASTER_PATH = DATA_DIR / "skills_master.json"

# Load skills master data safely
if not SKILLS_MASTER_PATH.exists():
    raise FileNotFoundError(
        f"skills_master.json not found at: {SKILLS_MASTER_PATH}\n"
        f"Make sure your repo has /data/skills_master.json committed to GitHub."
    )

with open(SKILLS_MASTER_PATH, "r", encoding="utf-8") as f:
    SKILLS_MASTER = json.load(f)


# -----------------------------
# Frontend routes
# -----------------------------
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


# -----------------------------
# API routes
# -----------------------------
@app.route("/roles", methods=["GET"])
def roles():
    return jsonify({"roles": sorted(SKILLS_MASTER.keys())})


@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")

    resume_found, matched, missing = gap_for_role_from_text(role, resume_text)

    return jsonify({
        "role": role,
        "resume_found": resume_found,
        "matched": matched,
        "missing": missing
    })


@app.route("/match_jd", methods=["POST"])
def match_jd():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    result = compute_jd_resume_match(role, resume_text, jd_text)
    return jsonify(result)


# -----------------------------
# Resume upload endpoint (fixed)
# -----------------------------
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    """
    Expects multipart/form-data with field name: resume_file (or file)
    Returns resume_text extracted from uploaded PDF/DOCX.
    """
    if extract_text_from_uploaded_file is None:
        return jsonify({
            "error": "resume_parser.py failed to import extract_text_from_uploaded_file(). "
                     "Make sure resume_parser.py contains that function."
        }), 500

    # Accept both names to be robust with frontend code
    file = None
    if "resume_file" in request.files:
        file = request.files["resume_file"]
    elif "file" in request.files:
        file = request.files["file"]

    if file is None:
        return jsonify({"error": "No file provided. Use field name 'resume_file' (or 'file')."}), 400

    if not file or (file.filename or "").strip() == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        extracted_text = extract_text_from_uploaded_file(file)
        if not (extracted_text or "").strip():
            return jsonify({"error": "Could not extract text (file may be scanned or unsupported)."}), 422

        # IMPORTANT: return resume_text because your index.html expects it
        return jsonify({
            "filename": file.filename,
            "resume_text": extracted_text
        })
    except Exception as e:
        return jsonify({
            "error": "Upload processing failed",
            "details": str(e)
        }), 500


# -----------------------------
# AI suggestions endpoint (rule-based)
# -----------------------------
@app.route("/ai_suggestions", methods=["POST"])
def ai_suggestions():
    if generate_ats_bullets is None:
        return jsonify({"error": "ai_suggester.py not available on server."}), 500

    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    match = compute_jd_resume_match(role, resume_text, jd_text)
    missing_keywords = match.get("keyword_coverage", {}).get("missing", [])

    suggestions = generate_ats_bullets(
        resume_text=resume_text,
        missing_keywords=missing_keywords,
        target_role=role,
        top_n=5
    )

    return jsonify({
        "role": role,
        "match_score": match.get("match_score", 0),
        "missing_keywords": missing_keywords,
        "ai_suggestions": suggestions
    })


if __name__ == "__main__":
    # Render sets PORT env var. Locally this still works.
    import os
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
