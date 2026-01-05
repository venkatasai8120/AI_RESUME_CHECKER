# extractor.py
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Set


def load_skills_master(path: str | None = None) -> Dict[str, List[str]]:
    """
    Robust loader that works locally + on Render/Linux.

    If path is None, it loads:
      repo_root/data/skills_master.json
    """
    if path is None:
        base_dir = Path(__file__).resolve().parent      # backend/
        project_root = base_dir.parent                  # repo root
        skills_path = project_root / "data" / "skills_master.json"
    else:
        skills_path = Path(path)

    if not skills_path.exists():
        raise FileNotFoundError(f"skills_master.json not found at: {skills_path}")

    with open(skills_path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def all_known_skills(skills_master: Dict[str, List[str]]) -> Set[str]:
    s: Set[str] = set()
    for role_skills in skills_master.values():
        for skill in role_skills:
            s.add(skill)
    return s


def extract_skills_from_text(text: str, skills_master: Dict[str, List[str]]) -> List[str]:
    """
    Exact/phrase match against the skills library (case-insensitive).
    Example: "power bi", "spring boot", "kubernetes"
    """
    text_n = normalize(text)
    skills = all_known_skills(skills_master)

    found: List[str] = []
    for skill in skills:
        skill_n = normalize(skill)
        pattern = r"(?<!\w)" + re.escape(skill_n) + r"(?!\w)"
        if re.search(pattern, text_n):
            found.append(skill)

    return sorted(found, key=lambda x: x.lower())
