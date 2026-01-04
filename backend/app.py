from flask import Flask, request, jsonify, send_from_directory
import json
import os
import uuid

from flask_cors import CORS

from analyzer import gap_for_role_from_text
from matcher import compute_jd_resume_match
from ai_suggester import generate_ats_bullets
from resume_parser import extract_resume_text, validate_file

app = Flask(__name__)
CORS(app)

# temp upload folder (inside backend)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load skills master data
with open(r"..\data\skills_master.json", "r", encoding="utf-8") as f:
    SKILLS_MASTER = json.load(f)

def skill_gap_by_role(role, resume_skills):
    job_skills = SKILLS_MASTER.get(role, [])
    matched = set(job_skills) & set(resume_skills)
    missing = set(job_skills) - set(resume_skills)
    return list(matched), list(missing)

@app.route("/")
def home():
    return send_from_directory(r"..\frontend", "index.html")

@app.route("/roles", methods=["GET"])
def roles():
    return jsonify({
        "roles": sorted(SKILLS_MASTER.keys())
    })

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

@app.route("/ai_suggestions", methods=["POST"])
def ai_suggestions():
    data = request.json or {}
    role = data.get("role", "")
    resume_text = data.get("resume_text", "")
    jd_text = data.get("jd_text", "")

    match_result = compute_jd_resume_match(role, resume_text, jd_text)
    missing_keywords = match_result.get("keyword_coverage", {}).get("missing", [])

    suggestions = generate_ats_bullets(
        resume_text=resume_text,
        missing_keywords=missing_keywords,
        target_role=role
    )

    return jsonify({
        "role": role,
        "match_score": match_result.get("match_score"),
        "missing_keywords": missing_keywords,
        "ai_suggestions": suggestions
    })

@app.route("/upload_resume", methods=["POST"])
def upload_resume():
    """
    Accepts a PDF/DOCX file upload and returns extracted text.
    Frontend should send as multipart/form-data with field name: resume_file
    """
    if "resume_file" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'resume_file'."}), 400

    f = request.files["resume_file"]
    if not f or not f.filename:
        return jsonify({"error": "Empty file."}), 400

    # Validate by extension + size (size from content-length when available)
    file_bytes = f.read()
    f.seek(0)

    ok, msg = validate_file(f.filename, len(file_bytes))
    if not ok:
        return jsonify({"error": msg}), 400

    # Save to uploads with a random name to avoid collisions
    ext = os.path.splitext(f.filename)[1].lower()
    temp_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, temp_name)
    f.save(save_path)

    try:
        text = extract_resume_text(save_path)
        if not text.strip():
            return jsonify({"error": "Could not extract text from this file."}), 400
        return jsonify({"filename": f.filename, "extracted_text": text})
    finally:
        # cleanup
        try:
            os.remove(save_path)
        except Exception:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
