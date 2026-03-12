import re
import hashlib
from database import SessionLocal
from models import MalignPattern, FlaggedPhrase, AnalysisResult


def analyze_text(input_text):

    db = SessionLocal()

    text_hash = hashlib.sha256(input_text.encode()).hexdigest()

    patterns = db.query(MalignPattern).all()

    flags = []

    for p in patterns:

        if p.is_regex:
            matches = re.finditer(p.pattern_text, input_text)
        else:
            matches = re.finditer(re.escape(p.pattern_text), input_text, re.IGNORECASE)

        for m in matches:
            flags.append({
                "pattern_id": p.id,
                "phrase": m.group(),
                "start": m.start(),
                "end": m.end(),
                "severity": p.severity
            })

    flagged_count = len(flags)

    pre_score = flagged_count * 10

    verdict = "LOW"
    if pre_score > 40:
        verdict = "HIGH_RISK"
    elif pre_score > 20:
        verdict = "MEDIUM"

    result = AnalysisResult(
        input_text=input_text,
        text_hash=text_hash,
        pre_score=pre_score,
        ai_probability=60.0,
        manipulation_score=pre_score,
        final_verdict=verdict,
        confidence="medium",
        flagged_count=flagged_count,
    )

    db.add(result)
    db.commit()

    result_id = result.id

    for f in flags:
        phrase = FlaggedPhrase(
            result_id=result_id,
            pattern_id=f["pattern_id"],
            phrase_text=f["phrase"],
            char_start=f["start"],
            char_end=f["end"],
            reason="pattern match",
            severity=f["severity"],
            source="db_match"
        )
        db.add(phrase)

    db.commit()
    db.close()

    return {
        "flags": flags,
        "score": pre_score,
        "verdict": verdict
    }