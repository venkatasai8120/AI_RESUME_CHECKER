import json
import re
from typing import List, Dict, Set

def load_skills_master(path: str = r"..\data\skills_master.json") -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(text: str) -> str:
    # Lowercase + collapse whitespace
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

def all_known_skills(skills_master: Dict[str, List[str]]) -> Set[str]:
    # Flatten unique skills across roles
    s = set()
    for role_skills in skills_master.values():
        for skill in role_skills:
            s.add(skill)
    return s

def extract_skills_from_text(text: str, skills_master: Dict[str, List[str]]) -> List[str]:
    """
    Simple exact/phrase match against the skills library (case-insensitive).
    Example matches: "power bi", "spring boot", "kubernetes"
    """
    text_n = normalize(text)

    skills = all_known_skills(skills_master)
    found = []

    for skill in skills:
        skill_n = normalize(skill)

        # word-boundary-ish match for phrases
        # e.g., matches "power bi" in "... Power BI dashboards ..."
        pattern = r"(?<!\w)" + re.escape(skill_n) + r"(?!\w)"
        if re.search(pattern, text_n):
            found.append(skill)

    # Sort for stable output (nice for debugging)
    return sorted(found)
