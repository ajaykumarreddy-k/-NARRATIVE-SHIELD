import re
from database import SessionLocal
from models import MalignPattern


def analyze_text(text):

    db = SessionLocal()

    patterns = db.query(MalignPattern).all()

    flagged = []

    for p in patterns:

        if p.is_regex:
            matches = re.findall(p.pattern_text, text, re.IGNORECASE)
        else:
            matches = [p.pattern_text] if p.pattern_text.lower() in text.lower() else []

        for m in matches:
            flagged.append({
                "phrase": m,
                "severity": p.severity,
                "reason": p.description,
                "pattern_id": p.id
            })

    flagged_count = len(flagged)

    # simple score
    score = min(flagged_count * 10, 100)

    if score > 70:
        verdict = "HIGH_RISK"
    elif score > 40:
        verdict = "MEDIUM_RISK"
    else:
        verdict = "LOW_RISK"

    db.close()

    return {
        "score": score,
        "verdict": verdict,
        "flagged": flagged
    }