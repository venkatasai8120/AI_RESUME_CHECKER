from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json

from analyzer import gap_for_role_from_text
from matcher import compute_jd_resume_match
from ai_suggester import generate_ats_bullets  # you already have this

app = Flask(__name__)
CORS(app)

# ---------- PATHS (Render-safe) ----------
BASE_DIR = Path(__file__).resolve().parent        # backend/
PROJECT_ROOT = BASE_DIR.parent                    # repo root
DATA_DIR = PROJECT_ROOT / "data"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

SKILLS_PATH = DATA_DIR / "skills_master.json"

if not SKILLS_PATH.exists():
    raise FileNotFoundError(f"skills_master.json not found at: {SKILLS_PATH}")

with open(SKILLS_PATH, "r", encoding="utf-8") as f:
    SKILLS_MASTER = json.load(f)


# ---------- FRONTEND ----------
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(FRONTEND_DIR / "assets", filename)


# ---------- API ----------
@app.route("/roles", methods=["GET"])
def roles():
    return jsonify({"roles": sorted(SKILLS_MASTER.keys())})


@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")

    resume_found, matched, missing = gap_for_role_from_text(role, resume_text, SKILLS_MASTER)

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

    role_skills = SKILLS_MASTER.get(role, [])

    # Support both matcher signatures (3 args or 4 args)
    try:
        result = compute_jd_resume_match(role, resume_text, jd_text, role_skills)
    except TypeError:
        result = compute_jd_resume_match(role, resume_text, jd_text)

    return jsonify(result)


@app.route("/ai_suggestions", methods=["POST"])
def ai_suggestions():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    role_skills = SKILLS_MASTER.get(role, [])

    # get match result (for missing keywords)
    try:
        match_result = compute_jd_resume_match(role, resume_text, jd_text, role_skills)
    except TypeError:
        match_result = compute_jd_resume_match(role, resume_text, jd_text)

    missing_keywords = []
    if match_result.get("keyword_coverage"):
        missing_keywords = match_result["keyword_coverage"].get("missing", [])

    suggestions = generate_ats_bullets(
        resume_text=resume_text,
        missing_keywords=missing_keywords,
        target_role=role,
        top_n=5
    )

    return jsonify({
        "role": role,
        "match_score": match_result.get("match_score", 0),
        "missing_keywords": missing_keywords,
        "ai_suggestions": suggestions
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
