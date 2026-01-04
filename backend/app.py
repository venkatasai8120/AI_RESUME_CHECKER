from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import json

from analyzer import gap_for_role_from_text
from matcher import compute_jd_resume_match

# Optional: if you added upload feature
try:
    from resume_parser import extract_text_from_uploaded_file
except Exception:
    extract_text_from_uploaded_file = None

# Optional: if you added AI suggestions endpoint
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
    # Serves: /assets/background.jpg etc.
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


# -----------------------------
# Resume upload endpoint (if you added it)
# -----------------------------
@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    if extract_text_from_uploaded_file is None:
        return jsonify({"error": "resume_parser.py not available on server."}), 500

    if "resume_file" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'resume_file'."}), 400

    file = request.files["resume_file"]
    if not file or file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    extracted_text = extract_text_from_uploaded_file(file)
    return jsonify({
        "filename": file.filename,
        "extracted_text": extracted_text
    })


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

    # Use JD matcher to get missing keywords first
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
    app.run(debug=True)
