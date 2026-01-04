from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import json
import os
from pathlib import Path

from analyzer import gap_for_role_from_text
from matcher import compute_jd_resume_match

# Optional: only import if you added these files/routes already
# If you DON'T have ai_suggester.py or upload utils yet, comment these out.
try:
    from ai_suggester import generate_ats_bullets
except Exception:
    generate_ats_bullets = None

try:
    from resume_parser import extract_text_from_file  # if you created this helper
except Exception:
    extract_text_from_file = None


app = Flask(__name__)
CORS(app)

# ---- PATHS (cross-platform) ----
BACKEND_DIR = Path(__file__).resolve().parent           # .../backend
PROJECT_DIR = BACKEND_DIR.parent                        # project root
DATA_DIR = PROJECT_DIR / "data"
FRONTEND_DIR = PROJECT_DIR / "frontend"

SKILLS_PATH = DATA_DIR / "skills_master.json"

# ---- LOAD SKILLS ----
if not SKILLS_PATH.exists():
    raise FileNotFoundError(
        f"skills_master.json not found at: {SKILLS_PATH}\n"
        f"Project dir: {PROJECT_DIR}\n"
        f"Files in data/: {list(DATA_DIR.glob('*')) if DATA_DIR.exists() else 'data/ folder missing'}"
    )

with open(SKILLS_PATH, "r", encoding="utf-8") as f:
    SKILLS_MASTER = json.load(f)


def skill_gap_by_role(role, resume_skills):
    job_skills = SKILLS_MASTER.get(role, [])
    matched = set(job_skills) & set(resume_skills)
    missing = set(job_skills) - set(resume_skills)
    return sorted(matched), sorted(missing)


@app.route("/")
def home():
    # Serve frontend UI
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})


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
        "extracted_skills": resume_found,
        "matched_skills": matched,
        "missing_skills": missing
    })


@app.route("/match_jd", methods=["POST"])
def match_jd():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    result = compute_jd_resume_match(role, resume_text, jd_text)
    return jsonify(result)


# ---- OPTIONAL: AI suggestions endpoint (rule-based; no OpenAI key needed) ----
@app.route("/ai_suggestions", methods=["POST"])
def ai_suggestions():
    if generate_ats_bullets is None:
        return jsonify({"error": "ai_suggester.py not available in backend."}), 500

    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    # use your matcher to compute missing keywords (JD-based)
    match = compute_jd_resume_match(role, resume_text, jd_text)
    missing_keywords = (match.get("keyword_coverage") or {}).get("missing", [])

    suggestions = generate_ats_bullets(
        resume_text=resume_text,
        missing_keywords=missing_keywords,
        target_role=role,
        top_n=5
    )

    return jsonify({
        "role": role,
        "match_score": match.get("match_score"),
        "missing_keywords": missing_keywords,
        "ai_suggestions": suggestions
    })


# ---- OPTIONAL: file upload endpoint (DOCX/PDF) ----
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if extract_text_from_file is None:
        return jsonify({"error": "resume_parser.py (extract_text_from_file) not available in backend."}), 500

    if "resume_file" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'resume_file'."}), 400

    f = request.files["resume_file"]
    if not f.filename:
        return jsonify({"error": "Empty filename."}), 400

    # Read bytes and extract text
    file_bytes = f.read()
    extracted_text = extract_text_from_file(f.filename, file_bytes)

    return jsonify({
        "filename": f.filename,
        "extracted_text": extracted_text
    })


if __name__ == "__main__":
    # Local only. Render uses gunicorn.
    app.run(debug=True)
