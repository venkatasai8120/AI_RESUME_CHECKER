# matcher.py
from __future__ import annotations

from typing import Dict, List, Any
from extractor import load_skills_master, extract_skills_from_text


def _safe_ratio(a: int, b: int) -> float:
    return (a / b) if b else 0.0


def _ats_warnings(resume_text: str, jd_skill_targets_count: int, jd_coverage: float) -> List[str]:
    warnings: List[str] = []

    resume_words = len((resume_text or "").split())
    if resume_words < 150:
        warnings.append("Resume may be too short (under ~150 words).")

    bullet_lines = 0
    for line in (resume_text or "").splitlines():
        l = line.strip()
        if l.startswith(("-", "•", "*")):
            bullet_lines += 1
    if bullet_lines < 3:
        warnings.append("Low bullet usage — ATS resumes usually include more bullet points.")

    if jd_skill_targets_count >= 5 and jd_coverage < 0.35:
        warnings.append("Low keyword coverage for this job description (under ~35%).")

    return warnings


def compute_jd_resume_match(
    role: str,
    resume_text: str,
    jd_text: str,
    weight_jd: float = 0.7,
    weight_role: float = 0.3
) -> Dict[str, Any]:
    """
    JD vs Resume matching.
    Returns match_score as an int percent from 0 to 100.
    """
    skills_master = load_skills_master()

    role_skills: List[str] = skills_master.get(role, []) or []

    jd_skills_detected = extract_skills_from_text(jd_text or "", skills_master)
    resume_skills_detected = extract_skills_from_text(resume_text or "", skills_master)

    jd_set = set(jd_skills_detected)
    resume_set = set(resume_skills_detected)
    role_set = set(role_skills)

    jd_required = sorted(list(jd_set & role_set), key=lambda x: x.lower())

    if jd_required:
        jd_targets = jd_required
        jd_targets_source = "role∩jd"
    elif jd_skills_detected:
        jd_targets = jd_skills_detected
        jd_targets_source = "jd_global"
    else:
        jd_targets = role_skills
        jd_targets_source = "role_fallback"

    jd_targets_set = set(jd_targets)

    matched_jd = sorted(list(jd_targets_set & resume_set), key=lambda x: x.lower())
    missing_jd = sorted(list(jd_targets_set - resume_set), key=lambda x: x.lower())

    matched_role = sorted(list(role_set & resume_set), key=lambda x: x.lower())
    missing_role = sorted(list(role_set - resume_set), key=lambda x: x.lower())

    jd_score = _safe_ratio(len(matched_jd), len(jd_targets_set))
    role_score = _safe_ratio(len(matched_role), len(role_set))

    final = (weight_jd * jd_score) + (weight_role * role_score)
    match_score = int(round(final * 100))  # 0..100

    warnings = _ats_warnings(resume_text or "", len(jd_targets_set), jd_score)

    suggestions: List[str] = []
    if missing_jd:
        suggestions.append("Add missing JD keywords into relevant experience bullets (only if you truly have them).")
    if warnings:
        suggestions.append("Reformat to be more ATS-friendly: clear headings, stronger bullets, and role/JD keywords.")

    score_meta = (
        f"JD coverage: {round(jd_score * 100, 1)}% • "
        f"Role coverage: {round(role_score * 100, 1)}% • "
        f"Targets source: {jd_targets_source}"
    )

    return {
        "role": role,
        "match_score": match_score,
        "score_meta": score_meta,
        "weights": {"jd": weight_jd, "role": weight_role},
        "jd_targets_source": jd_targets_source,

        "jd_skills_detected": jd_skills_detected,
        "resume_skills_detected": resume_skills_detected,

        "keyword_coverage": {
            "targets": jd_targets,
            "matched": matched_jd,
            "missing": missing_jd,
            "coverage_percent": round(jd_score * 100, 2) if jd_targets_set else 0.0
        },

        "role_gap": {
            "role_skills": role_skills,
            "matched": matched_role,
            "missing": missing_role,
            "coverage_percent": round(role_score * 100, 2) if role_set else 0.0
        },

        "ats_checks": {"warnings": warnings},
        "suggestions": suggestions
    }
