import json
from typing import List, Dict, Tuple
from extractor import load_skills_master, extract_skills_from_text

def load_master(path: str = r"..\data\skills_master.json") -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def gap_for_role_from_text(role: str, resume_text: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Returns: (resume_skills_found, matched, missing)
    """
    skills_master = load_skills_master()
    resume_skills_found = extract_skills_from_text(resume_text, skills_master)

    job_skills = skills_master.get(role, [])
    matched = sorted(list(set(job_skills) & set(resume_skills_found)))
    missing = sorted(list(set(job_skills) - set(resume_skills_found)))

    return resume_skills_found, matched, missing
