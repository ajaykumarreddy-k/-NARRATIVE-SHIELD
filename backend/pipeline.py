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
# NOTE: Do NOT add unconditional imports here — use the conditional
# DB_AVAILABLE / GEMINI_AVAILABLE flags set at the top of this file.

def analyze_text(text: str, api_key: str = None) -> dict[str, Any]:
    """
    Full 3-layer analysis pipeline.
    Uses conditional flags to gracefully degrade:
      - GEMINI_AVAILABLE → uses Gemini; else tries Ollama; else stat-only
      - DB_AVAILABLE     → uses db_matcher; else uses inline patterns
    """
    t_start = time.time()
    if not text or not text.strip():
        return {"error": "Empty text submitted"}

    # ── LAYER 1: Statistical Engine ───────────────────────────────────────
    l1 = compute_statistical_score(text)
    pre_score = l1["pre_score"]

    # ── LAYER 2: LLM Analysis (Gemini → Ollama → Statistical fallback) ───
    l2 = None
    l2_source = "offline"

    if GEMINI_AVAILABLE and api_key:
        try:
            l2 = analyze_with_gemini(text, api_key, pre_score)
            l2_source = "gemini"
            print("[Pipeline] Layer 2 → Gemini ✓")
        except Exception as e:
            print(f"[Pipeline] Gemini failed: {e} — trying Ollama fallback")

    if l2 is None:
        # Try Ollama as fallback
        try:
            l2 = analyze_with_ollama(text, pre_score)
            l2_source = "ollama"
            print("[Pipeline] Layer 2 → Ollama ✓")
        except Exception as e:
            print(f"[Pipeline] Ollama failed: {e} — using stat-only fallback")

    if l2 is None:
        # Final fallback: derive from statistical score only
        l2 = {
            "ai_probability": int(pre_score),
            "manipulation_score": int(pre_score * 0.8),
            "flagged_phrases": [],
            "narrative_technique": "Statistical Only",
            "confidence": "low",
            "summary": f"LLM unavailable. Statistical pre-score: {pre_score}/100.",
        }
        l2_source = "statistical_fallback"

    # ── LAYER 3: Pattern DB Matching ──────────────────────────────────────
    if DB_AVAILABLE:
        try:
            db_phrases = match_patterns(text)
            print(f"[Pipeline] Layer 3 → DB matcher: {len(db_phrases)} matches ✓")
        except Exception as e:
            print(f"[Pipeline] DB matcher error: {e} — using inline fallback")
            db_phrases = _inline_db_match(text)
    else:
        db_phrases = _inline_db_match(text)
        print(f"[Pipeline] Layer 3 → Inline fallback: {len(db_phrases)} matches")

    # ── MERGE phrases ─────────────────────────────────────────────────────
    gemini_phrases = l2.get("flagged_phrases", [])

    # Existing phrases from LLM to avoid duplicates
    existing_phrases = {p.get('phrase', '').lower() for p in gemini_phrases}

    all_phrases = []
    # Add LLM phrases first
    for p in gemini_phrases:
        phrase_text = p.get("phrase", "")
        idx = text.lower().find(phrase_text.lower())
        all_phrases.append({
            "phrase":     phrase_text,
            "category":   "llm_flagged",
            "catLabel":   "AI Flagged",
            "catClass":   "emo",
            "severity":   p.get("severity", "MED"),
            "char_start": idx if idx != -1 else 0,
            "char_end":   (idx + len(phrase_text)) if idx != -1 else 0,
            "source":     l2_source,
            "reason":     p.get("reason", "AI analysis flagged this narrative pattern"),
        })

    # Add DB matches if not already flagged
    for db_match in db_phrases:
        if db_match['phrase'].lower() not in existing_phrases:
            all_phrases.append({
                "phrase":     db_match['phrase'],
                "category":   "db_match",
                "catLabel":   "DB Match",
                "catClass":   "uvt",
                "severity":   db_match['severity'],
                "char_start": db_match['char_start'],
                "char_end":   db_match['char_end'],
                "source":     "db",
                "reason":     db_match['reason'],
            })

    # Sort by char_start
    all_phrases.sort(key=lambda p: p.get("char_start", 0))

    # ── DERIVE final scores ───────────────────────────────────────────────
    ai_prob = l2.get("ai_probability", 0)
    manip   = l2.get("manipulation_score", 0)
    verdict, verdict_sub = _derive_verdict(manip, ai_prob)

    proc_ms = int((time.time() - t_start) * 1000)

    return {
        "ai_probability":    ai_prob,
        "manipulation_score": manip,
        "stat_score":        pre_score,
        "confidence":        l2.get("confidence", "low"),
        "verdict":           verdict,
        "verdict_sub":       verdict_sub,
        "technique":         l2.get("narrative_technique", "Unknown"),
        "summary":           l2.get("summary", "Analysis completed."),
        "phrases":           all_phrases,
        "explain":           l1["feature_display"],
        "layers": {
            "l1": int(pre_score),
            "l2": manip,
            "l3": min(len(db_phrases) * 15, 100),
        },
        "scan_id":    _generate_scan_id(),
        "text_hash":  _text_hash(text),
        "proc_time":  f"{proc_ms / 1000:.1f}s",
        "text_stats": l1["text_stats"],
        "model_used": l2_source,
    }
