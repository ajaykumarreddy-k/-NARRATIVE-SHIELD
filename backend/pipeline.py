"""
NarrativeShield — Master Parser Pipeline
==========================================
Orchestrates all 3 layers and returns the final unified result
that the FastAPI /analyze endpoint serves to the frontend.

Pipeline:
  Layer 1 → statistical_engine.py  (offline, <50ms)
  Layer 2 → ollama_layer.py         (your local Ollama)
            OR gemini_layer.py      (your teammate's Gemini API)
  Layer 3 → db_matcher.py           (your teammate's SQLite DB)
             OR inline fallback patterns (if DB not ready)

This file is the ONLY import your FastAPI main.py needs:
  from parser.pipeline import analyze_text
"""

import time
import hashlib
import random
import string
from typing import Any

from statistical_engine import compute_statistical_score
from ollama_layer import analyze_with_ollama, _get_available_models

# ── Try to import teammate's modules — graceful fallback if not ready yet ──
try:
    from db_matcher import match_patterns
    DB_AVAILABLE = True
    print("[Pipeline] ✓ db_matcher loaded")
except ImportError:
    DB_AVAILABLE = False
    print("[Pipeline] db_matcher not found — using inline pattern fallback")

try:
    from gemini_layer import analyze_with_gemini
    GEMINI_AVAILABLE = True
    print("[Pipeline] ✓ gemini_layer loaded")
except ImportError:
    GEMINI_AVAILABLE = False
    print("[Pipeline] gemini_layer not found — using Ollama only")

# ── Detect what LLM is available right now ────────────────────────────────────
def _get_llm_mode() -> str:
    """
    Returns which LLM backend is available:
      'gemini'  — teammate's Gemini API is loaded and presumably has a key
      'ollama'  — local Ollama is running with at least one model
      'offline' — neither available, stat-only fallback
    """
    if GEMINI_AVAILABLE:
        return "gemini"
    models = _get_available_models()
    if models:
        return "ollama"
    return "offline"


# ── INLINE PATTERN FALLBACK (used if db_matcher.py not ready) ────────────────
# 50 patterns across 7 categories. Your teammate's DB will replace these.

INLINE_PATTERNS = [
    # EMOTIONAL AMPLIFIERS
    {"pattern": "shocking truth",         "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "HIGH"},
    {"pattern": "they don't want you",    "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "HIGH"},
    {"pattern": "wake up",                "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "HIGH"},
    {"pattern": "hidden dangers",         "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "MED"},
    {"pattern": "outrageous",             "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "MED"},
    {"pattern": "unbelievable",           "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "LOW"},
    {"pattern": "what they hide",         "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "HIGH"},
    {"pattern": "suppressed",             "category": "emotional_amplifier", "catLabel": "Emo Amplifier", "catClass": "emo", "severity": "MED"},
    # US VS THEM
    {"pattern": "our people",             "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "the elites",             "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "real citizens",          "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "deep state",             "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "mainstream media",       "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "MED"},
    {"pattern": "globalists",             "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "establishment",          "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "LOW"},
    {"pattern": "true patriots",          "category": "us_vs_them",          "catLabel": "Us vs Them",    "catClass": "uvt", "severity": "HIGH"},
    # FALSE URGENCY
    {"pattern": "time is running out",    "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "HIGH"},
    {"pattern": "before it's deleted",    "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "HIGH"},
    {"pattern": "share immediately",      "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "HIGH"},
    {"pattern": "share this now",         "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "HIGH"},
    {"pattern": "before they ban",        "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "HIGH"},
    {"pattern": "act now",                "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "MED"},
    {"pattern": "last chance",            "category": "false_urgency",       "catLabel": "False Urgency", "catClass": "fur", "severity": "MED"},
    # FAKE AUTHORITY
    {"pattern": "experts agree",          "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "MED"},
    {"pattern": "studies show",           "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "MED"},
    {"pattern": "scientists confirm",     "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "MED"},
    {"pattern": "sources say",            "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "MED"},
    {"pattern": "leading researchers",    "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "MED"},
    {"pattern": "insiders confirm",       "category": "fake_authority",      "catLabel": "Fake Authority","catClass": "fau", "severity": "HIGH"},
    # CONSPIRACY FRAME
    {"pattern": "the real truth",         "category": "conspiracy_frame",    "catLabel": "Conspiracy",    "catClass": "emo", "severity": "HIGH"},
    {"pattern": "what they don't tell",   "category": "conspiracy_frame",    "catLabel": "Conspiracy",    "catClass": "emo", "severity": "HIGH"},
    {"pattern": "orchestrating",          "category": "conspiracy_frame",    "catLabel": "Conspiracy",    "catClass": "emo", "severity": "MED"},
    {"pattern": "agenda",                 "category": "conspiracy_frame",    "catLabel": "Conspiracy",    "catClass": "emo", "severity": "LOW"},
    {"pattern": "cover-up",               "category": "conspiracy_frame",    "catLabel": "Conspiracy",    "catClass": "emo", "severity": "HIGH"},
    # FEAR TRIGGERS
    {"pattern": "imminent threat",        "category": "fear_trigger",        "catLabel": "Fear Trigger",  "catClass": "fur", "severity": "HIGH"},
    {"pattern": "danger to your family",  "category": "fear_trigger",        "catLabel": "Fear Trigger",  "catClass": "fur", "severity": "HIGH"},
    {"pattern": "collapse",               "category": "fear_trigger",        "catLabel": "Fear Trigger",  "catClass": "fur", "severity": "MED"},
    {"pattern": "systematically erased",  "category": "fear_trigger",        "catLabel": "Fear Trigger",  "catClass": "fur", "severity": "HIGH"},
    {"pattern": "in danger",              "category": "fear_trigger",        "catLabel": "Fear Trigger",  "catClass": "fur", "severity": "MED"},
    # COORDINATED MARKERS
    {"pattern": "join us or",             "category": "coordinated_marker",  "catLabel": "Coord. Marker", "catClass": "uvt", "severity": "HIGH"},
    {"pattern": "spread the word",        "category": "coordinated_marker",  "catLabel": "Coord. Marker", "catClass": "uvt", "severity": "MED"},
    {"pattern": "pass this on",           "category": "coordinated_marker",  "catLabel": "Coord. Marker", "catClass": "uvt", "severity": "MED"},
    {"pattern": "tell everyone",          "category": "coordinated_marker",  "catLabel": "Coord. Marker", "catClass": "uvt", "severity": "MED"},
]


def _inline_db_match(text: str) -> list[dict]:
    """
    Fallback pattern matching using INLINE_PATTERNS.
    Used when db_matcher.py (teammate's DB) is not available.
    Returns same schema as db_matcher.match_patterns().
    """
    text_lower = text.lower()
    matched = []
    for pat in INLINE_PATTERNS:
        idx = text_lower.find(pat["pattern"].lower())
        if idx != -1:
            # find actual casing in original text
            actual = text[idx: idx + len(pat["pattern"])]
            matched.append({
                "phrase":     actual,
                "category":   pat["category"],
                "catLabel":   pat["catLabel"],
                "catClass":   pat["catClass"],
                "severity":   pat["severity"],
                "char_start": idx,
                "char_end":   idx + len(pat["pattern"]),
                "source":     "db",
                "reason":     f"{pat['category'].replace('_', ' ').title()} — known manipulation marker",
            })
    return matched


def _merge_phrases(db_phrases: list[dict], llm_phrases: list[dict], text: str) -> list[dict]:
    """
    Merge DB-matched phrases with LLM-flagged phrases.
    DB matches take priority (they have char positions).
    LLM phrases that don't overlap with DB matches are added.
    Deduplication by lowercased phrase text.
    """
    seen = {p["phrase"].lower() for p in db_phrases}
    merged = list(db_phrases)

    text_lower = text.lower()
    for p in llm_phrases:
        phrase_lower = p.get("phrase", "").lower().strip()
        if not phrase_lower or phrase_lower in seen:
            continue
        # find position in text
        idx = text_lower.find(phrase_lower)
        if idx == -1:
            continue
        seen.add(phrase_lower)
        sev = p.get("severity", "MED")
        if sev not in ("HIGH", "MED", "LOW"):
            sev = "MED"
        merged.append({
            "phrase":     text[idx: idx + len(phrase_lower)],
            "category":   "llm_flagged",
            "catLabel":   "LLM Flagged",
            "catClass":   "emo",
            "severity":   sev,
            "char_start": idx,
            "char_end":   idx + len(phrase_lower),
            "source":     "gemini",
            "reason":     p.get("reason", "Flagged by AI analysis"),
        })
    return merged


def _derive_verdict(manip: int, ai_prob: int) -> tuple[str, str]:
    """Returns (verdict_key, verdict_subtitle)."""
    combined = (manip * 0.6) + (ai_prob * 0.4)
    if combined >= 60:
        return "HIGH_RISK", "Multiple manipulation techniques detected"
    elif combined >= 35:
        return "MEDIUM_RISK", "Subtle emotional manipulation detected"
    else:
        return "LOW_RISK", "Factual content, low manipulation signals"


def _generate_scan_id() -> str:
    return "SCN-" + "".join(random.choices(string.digits, k=4))


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:8].upper()


# ── MASTER PIPELINE ───────────────────────────────────────────────────────────

def analyze_text(text: str) -> dict[str, Any]:
    """
    Full 3-layer analysis pipeline.

    Args:
        text: Raw input text from the user (any length)

    Returns complete result dict ready to send to frontend:
        {
          # Core scores
          "ai_probability": int,
          "manipulation_score": int,
          "stat_score": float,
          "confidence": str,
          "verdict": str,
          "verdict_sub": str,
          "technique": str,
          "summary": str,

          # Phrase data
          "phrases": [ {phrase, catLabel, catClass, severity, source, reason, char_start, char_end} ],

          # Explainability bars
          "explain": [ {feat, pct, color} ],

          # Layer breakdown for right panel
          "layers": {"l1": int, "l2": int, "l3": int},

          # Metadata
          "scan_id": str,
          "text_hash": str,
          "proc_time": str,
          "text_stats": dict,
          "model_used": str,
        }
    """
    t_start = time.time()
    if not text or not text.strip():
        return {"error": "Empty text submitted"}

    # ── LAYER 1: Statistical Engine ───────────────────────────────────────
    print("[Pipeline] Layer 1: Statistical fingerprinting...")
    l1 = compute_statistical_score(text)
    pre_score = l1["pre_score"]
    print(f"[Pipeline] Layer 1 pre_score: {pre_score}")

    # ── LAYER 2: LLM Analysis ─────────────────────────────────────────────
    llm_mode = _get_llm_mode()
    print(f"[Pipeline] Layer 2: LLM mode = {llm_mode}")

    if llm_mode == "gemini":
        l2 = analyze_with_gemini(text, pre_score=pre_score)
        l2_source = "gemini"
    elif llm_mode == "ollama":
        l2 = analyze_with_ollama(text, pre_score=pre_score)
        l2_source = l2.get("_source", "ollama")
    else:
        # fully offline — stat fallback already inside ollama_layer
        from ollama_layer import _statistical_fallback
        l2 = _statistical_fallback(pre_score, text)
        l2_source = "offline"

    print(f"[Pipeline] Layer 2 done [{l2_source}] — AI:{l2['ai_probability']} Manip:{l2['manipulation_score']}")

    # ── LAYER 3: Pattern DB Matching ──────────────────────────────────────
    print("[Pipeline] Layer 3: Pattern matching...")
    if DB_AVAILABLE:
        db_phrases = match_patterns(text)
    else:
        db_phrases = _inline_db_match(text)
    print(f"[Pipeline] Layer 3 matched {len(db_phrases)} phrases")

    # ── MERGE phrases ─────────────────────────────────────────────────────
    llm_phrases = l2.get("flagged_phrases", [])
    all_phrases = _merge_phrases(db_phrases, llm_phrases, text)
    # Sort by char_start for correct rendering order
    all_phrases.sort(key=lambda p: p.get("char_start", 999))

    # ── DERIVE final scores ───────────────────────────────────────────────
    ai_prob = l2["ai_probability"]
    manip   = l2["manipulation_score"]

    # Boost scores if many DB patterns matched
    db_hit_count = len(db_phrases)
    if db_hit_count >= 4:
        manip   = min(manip + 10, 100)
        ai_prob = min(ai_prob + 8, 100)
    elif db_hit_count >= 2:
        manip   = min(manip + 5, 100)

    verdict, verdict_sub = _derive_verdict(manip, ai_prob)

    # Layer scores for the breakdown bars
    l3_score = min(db_hit_count * 12, 100)  # 0–100 based on matches

    # ── BUILD final result ────────────────────────────────────────────────
    proc_ms = int((time.time() - t_start) * 1000)

    return {
        # Core scores
        "ai_probability":    ai_prob,
        "manipulation_score": manip,
        "stat_score":        pre_score,
        "confidence":        l2["confidence"],
        "verdict":           verdict,
        "verdict_sub":       verdict_sub,
        "technique":         l2["narrative_technique"],
        "summary":           l2["summary"],

        # Phrase data (merged DB + LLM)
        "phrases": all_phrases,

        # Explainability bars (from Layer 1)
        "explain": l1["feature_display"],

        # Layer scores
        "layers": {
            "l1": int(pre_score),
            "l2": manip,
            "l3": l3_score,
        },

        # Metadata
        "scan_id":    _generate_scan_id(),
        "text_hash":  _text_hash(text),
        "proc_time":  f"{proc_ms / 1000:.1f}s",
        "text_stats": l1["text_stats"],
        "model_used": l2.get("_model", l2_source),
    }
