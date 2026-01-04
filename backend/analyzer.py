# analyzer.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import re
import json

def _load_skills_master() -> Dict[str, List[str]]:
    base_dir = Path(__file__).resolve().parent          # backend/
    project_root = base_dir.parent                       # repo root
    skills_path = project_root / "data" / "skills_master.json"
    if not skills_path.exists():
        raise FileNotFoundError(f"skills_master.json not found at: {skills_path}")
    with open(skills_path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s\+\#\/\-]", " ", text)  # keep + # / -
    text = re.sub(r"\s+", " ", text).strip()
    return text

def contains_skill(norm_text: str, skill: str) -> bool:
    s = normalize_text(skill)
    if not s:
        return False
    pattern = r"(?<!\w)" + re.escape(s) + r"(?!\w)"
    return re.search(pattern, norm_text) is not None

def extract_skills_from_text(text: str, skills_list: List[str]) -> List[str]:
    norm = normalize_text(text)
    found = [sk for sk in skills_list if contains_skill(norm, sk)]
    return sorted(set(found), key=lambda x: x.lower())

def gap_for_role_from_text(
    role: str,
    resume_text: str,
    skills_master: Dict[str, List[str]] | None = None
) -> Tuple[List[str], List[str], List[str]]:
    """
    Returns: (resume_found, matched, missing)
    """
    if skills_master is None:
        skills_master = _load_skills_master()

    role_skills = skills_master.get(role, [])
    resume_found = extract_skills_from_text(resume_text, role_skills)

    matched = sorted(set(role_skills) & set(resume_found), key=lambda x: x.lower())
    missing = sorted(set(role_skills) - set(resume_found), key=lambda x: x.lower())

    return resume_found, matched, missing
