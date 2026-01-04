# ai_suggester.py
from __future__ import annotations
from typing import List, Dict
import re

def _split_into_bullets(text: str) -> List[str]:
    """
    Extract bullet-like lines. If none, split into sentences as fallback.
    """
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    bullets = [ln for ln in lines if ln.startswith(("-", "•", "*"))]

    if bullets:
        # remove bullet markers
        return [re.sub(r"^[-•*]\s*", "", b).strip() for b in bullets if b.strip()]

    # fallback: sentence split
    s = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [x.strip() for x in s if x.strip()]

def _inject_keywords(bullet: str, keywords: List[str], max_add: int = 2) -> str:
    """
    Lightly inject up to max_add missing keywords into a bullet,
    only if they are not already present.
    """
    b_low = (bullet or "").lower()
    to_add = []
    for kw in (keywords or []):
        if kw.lower() not in b_low:
            to_add.append(kw)
        if len(to_add) >= max_add:
            break

    if not to_add:
        return bullet.rstrip(".") + "."

    addon = ", leveraging " + ", ".join(to_add)
    if len(bullet) + len(addon) > 180:
        addon = " (leveraged " + ", ".join(to_add) + ")"

    return bullet.rstrip(".") + addon + "."

def generate_ats_bullets(
    resume_text: str,
    missing_keywords: List[str],
    target_role: str,
    top_n: int = 5
) -> Dict:
    """
    Rule-based "AI-ready" suggestions:
    - Extract bullet-like lines from resume (or sentences)
    - Improve phrasing with action verbs
    - Inject missing JD keywords lightly
    """
    raw_bullets = _split_into_bullets(resume_text)

    # If resume is empty or too short, provide generic bullets
    if not raw_bullets:
        raw_bullets = [
            "Built and improved automation pipelines to reduce manual work and increase deployment reliability",
            "Implemented monitoring and alerting to improve system visibility and reduce incident response time",
            "Collaborated with cross-functional teams to deliver scalable solutions aligned with business needs"
        ]

    verbs = ["Built", "Implemented", "Automated", "Optimized", "Developed", "Designed", "Improved"]

    common_start_verbs = {
        "built", "implemented", "managed", "led", "developed", "designed",
        "optimized", "automated", "created", "improved", "delivered",
        "migrated", "deployed", "maintained", "configured"
    }

    rewritten: List[str] = []
    for i, b in enumerate(raw_bullets[:top_n]):
        verb = verbs[i % len(verbs)]

        b_clean = (b or "").strip()
        if not b_clean:
            continue

        first_word = b_clean.split(" ", 1)[0].lower()

        # If bullet already starts with a strong verb, don't prepend another verb
        if first_word in common_start_verbs:
            base = b_clean.rstrip(".") + "."
        else:
            # normalize first character to lowercase for smoother grammar
            tail = (b_clean[0].lower() + b_clean[1:]) if len(b_clean) > 1 else b_clean
            base = f"{verb} {tail}".rstrip(".") + "."

        base = _inject_keywords(base, missing_keywords, max_add=2)
        rewritten.append(base)

    tips: List[str] = []
    if missing_keywords:
        tips.append(
            "Try to incorporate these missing JD keywords naturally (only if truthful): "
            + ", ".join(missing_keywords[:12])
        )
    tips.append("Use strong action verbs + measurable impact (e.g., reduced build time by 30%, improved uptime to 99.9%).")
    tips.append(f"Align your top 3 bullets with the target role: {target_role}.")

    return {
        "target_role": target_role,
        "missing_keywords": missing_keywords,
        "rewritten_bullets": rewritten,
        "tips": tips
    }
