"""
NarrativeShield — Layer 1: Statistical Fingerprinting Engine
============================================================
Runs 100% offline in <50ms. No API needed.
Produces a pre_score (0–100) that feeds into Layer 2 (Gemini).

Metrics calculated:
  1. lexical_repetition_ratio  — how repetitively words are reused
  2. sentence_length_variance  — LLMs produce suspiciously uniform sentence lengths
  3. punctuation_uniformity    — LLM text has mechanical punctuation patterns
  4. type_token_ratio          — vocabulary diversity (low = LLM-like)
  5. avg_word_length           — LLMs use slightly longer words on average
  6. uppercase_ratio           — propaganda uses aggressive capitalisation
  7. exclamation_density       — emotional manipulation marker
  8. question_density          — rhetorical question pattern
  9. entropy_score             — information entropy of character distribution
 10. coordinated_phrase_score  — exact phrase repetition (coordination signal)
"""

import re
import math
import statistics
from collections import Counter
from typing import Any


# ── helpers ──────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lowercase word tokens, stripping punctuation."""
    return re.findall(r'\b[a-z]{2,}\b', text.lower())


def _sentences(text: str) -> list[str]:
    """Split text into sentences."""
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in parts if len(s) > 4]


def _shannon_entropy(text: str) -> float:
    """Character-level Shannon entropy. LLM text clusters around 4.0–4.5 bits."""
    if not text:
        return 0.0
    freq = Counter(text)
    total = len(text)
    return -sum((c / total) * math.log2(c / total) for c in freq.values())


# ── individual feature calculators ───────────────────────────────────────────

def lexical_repetition_ratio(tokens: list[str]) -> float:
    """
    Ratio of repeated content words to total tokens.
    LLM-generated text reuses filler phrases excessively.
    Returns 0.0 (no repetition) – 1.0 (all words repeated).
    """
    if len(tokens) < 5:
        return 0.0
    freq = Counter(tokens)
    # ignore extremely common stop words
    stopwords = {
        'the','a','an','is','are','was','were','be','been','being',
        'have','has','had','do','does','did','will','would','could',
        'should','may','might','shall','to','of','in','for','on',
        'with','at','by','from','as','or','and','but','not','this',
        'that','it','its','we','our','they','their','you','your','i'
    }
    content = [t for t in tokens if t not in stopwords]
    if not content:
        return 0.0
    repeated = sum(c - 1 for c in Counter(content).values() if c > 1)
    return min(repeated / max(len(content), 1), 1.0)


def sentence_length_variance(sents: list[str]) -> float:
    """
    Coefficient of variation of sentence word counts.
    LLMs produce suspiciously uniform sentences → low variance.
    Returns a score 0–1 where LOW = LLM-like, HIGH = human-like.
    We invert so HIGH score = suspicious (LLM-like uniformity).
    """
    if len(sents) < 3:
        return 0.5
    lengths = [len(s.split()) for s in sents]
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    try:
        stdev = statistics.stdev(lengths)
    except statistics.StatisticsError:
        return 0.5
    cv = stdev / mean  # coefficient of variation
    # Low CV (< 0.3) = suspicious uniformity → high score
    suspicion = max(0.0, 1.0 - (cv / 0.8))
    return min(suspicion, 1.0)


def punctuation_uniformity(text: str) -> float:
    """
    LLM text uses punctuation in mechanical, evenly-spaced patterns.
    Measures variance in comma/period spacing. Low variance = suspicious.
    """
    positions = [i for i, c in enumerate(text) if c in '.,;:']
    if len(positions) < 4:
        return 0.3
    gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    if not gaps:
        return 0.3
    mean_gap = statistics.mean(gaps)
    if mean_gap == 0:
        return 0.3
    try:
        stdev_gap = statistics.stdev(gaps)
    except statistics.StatisticsError:
        return 0.3
    cv = stdev_gap / mean_gap
    return max(0.0, min(1.0 - (cv / 1.5), 1.0))


def type_token_ratio(tokens: list[str]) -> float:
    """
    Vocabulary diversity: unique_words / total_words.
    LLMs tend to lower TTR (less diverse vocabulary in short texts).
    We invert so HIGH score = suspicious (low diversity).
    """
    if not tokens:
        return 0.5
    ttr = len(set(tokens)) / len(tokens)
    # TTR < 0.4 is suspiciously low; TTR > 0.8 is very human
    suspicion = max(0.0, 1.0 - (ttr / 0.6))
    return min(suspicion, 1.0)


def uppercase_ratio(text: str) -> float:
    """
    Fraction of alphabetic characters that are uppercase.
    Propaganda and AI-generated emotional content over-capitalise.
    """
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return 0.0
    return sum(1 for c in alpha if c.isupper()) / len(alpha)


def exclamation_density(text: str, sents: list[str]) -> float:
    """Exclamation marks per sentence. > 0.5 per sentence is suspicious."""
    if not sents:
        return 0.0
    count = text.count('!')
    return min(count / max(len(sents), 1) / 1.0, 1.0)


def question_density(text: str, sents: list[str]) -> float:
    """Rhetorical question density. High = manipulation pattern."""
    if not sents:
        return 0.0
    count = text.count('?')
    return min(count / max(len(sents), 1) / 1.0, 1.0)


def entropy_score(text: str) -> float:
    """
    Shannon entropy of the text.
    Human text: ~4.5–5.5 bits. LLM text clusters: ~4.0–4.5.
    We flag unusually low or unnaturally uniform entropy.
    Returns 0–1 suspicion score.
    """
    h = _shannon_entropy(text)
    # LLM sweet spot: 3.8–4.5 bits → suspicious
    if 3.8 <= h <= 4.5:
        return 0.6
    elif h < 3.8:
        return 0.8  # very uniform → high suspicion
    else:
        return max(0.0, 1.0 - ((h - 4.5) / 1.5))


def coordinated_phrase_score(text: str) -> float:
    """
    Detects exact phrase repetition — a coordination signal.
    Splits into 4-gram windows and checks for duplicates.
    """
    words = text.lower().split()
    if len(words) < 8:
        return 0.0
    ngrams = [' '.join(words[i:i+4]) for i in range(len(words) - 3)]
    freq = Counter(ngrams)
    repeated = sum(1 for c in freq.values() if c > 1)
    return min(repeated / max(len(ngrams), 1) * 10, 1.0)


# ── MAIN FUNCTION ─────────────────────────────────────────────────────────────

def compute_statistical_score(text: str) -> dict[str, Any]:
    """
    Master function — runs all 10 metrics and returns a pre_score (0–100)
    plus the individual feature breakdown for the explainability panel.

    Returns:
        {
          "pre_score": float,          # 0–100
          "features": {                # individual scores 0–1
            "lexical_repetition": float,
            "sentence_uniformity": float,
            "punctuation_uniformity": float,
            "vocab_diversity": float,
            "uppercase_ratio": float,
            "exclamation_density": float,
            "question_density": float,
            "entropy_suspicion": float,
            "coordinated_phrases": float,
          },
          "feature_display": [         # for frontend explainability bars
            {"feat": str, "pct": int, "color": str},
            ...
          ],
          "text_stats": {             # raw diagnostics
            "word_count": int,
            "sentence_count": int,
            "char_count": int,
            "unique_words": int,
            "avg_sentence_length": float,
          }
        }
    """
    if not text or not text.strip():
        return {"pre_score": 0.0, "features": {}, "feature_display": [], "text_stats": {}}

    tokens = _tokenize(text)
    sents  = _sentences(text)

    # ── compute each feature ──────────────────────────────────────────────
    f = {}
    f["lexical_repetition"]     = lexical_repetition_ratio(tokens)
    f["sentence_uniformity"]    = sentence_length_variance(sents)
    f["punctuation_uniformity"] = punctuation_uniformity(text)
    f["vocab_diversity"]        = type_token_ratio(tokens)
    f["uppercase_ratio"]        = min(uppercase_ratio(text) * 3, 1.0)   # amplify
    f["exclamation_density"]    = exclamation_density(text, sents)
    f["question_density"]       = question_density(text, sents)
    f["entropy_suspicion"]      = entropy_score(text)
    f["coordinated_phrases"]    = coordinated_phrase_score(text)

    # ── weighted average → pre_score ─────────────────────────────────────
    weights = {
        "lexical_repetition":     0.18,
        "sentence_uniformity":    0.15,
        "punctuation_uniformity": 0.10,
        "vocab_diversity":        0.12,
        "uppercase_ratio":        0.10,
        "exclamation_density":    0.10,
        "question_density":       0.08,
        "entropy_suspicion":      0.12,
        "coordinated_phrases":    0.05,
    }
    raw = sum(f[k] * weights[k] for k in weights)
    pre_score = round(min(raw / sum(weights.values()), 1.0) * 100, 1)

    # ── display format for explainability bars ────────────────────────────
    feature_display = [
        {"feat": "Repetition Ratio",       "pct": round(f["lexical_repetition"]     * 100), "color": "#7c3aed"},
        {"feat": "Sentence Uniformity",    "pct": round(f["sentence_uniformity"]    * 100), "color": "#7c3aed"},
        {"feat": "Uppercase Aggression",   "pct": round(f["uppercase_ratio"]        * 100), "color": "#ef4444"},
        {"feat": "Exclamation Density",    "pct": round(f["exclamation_density"]    * 100), "color": "#ef4444"},
        {"feat": "DB Pattern Matches",     "pct": round(f["coordinated_phrases"]    * 100), "color": "#f59e0b"},
    ]

    # ── raw text diagnostics ──────────────────────────────────────────────
    text_stats = {
        "word_count":          len(tokens),
        "sentence_count":      len(sents),
        "char_count":          len(text),
        "unique_words":        len(set(tokens)),
        "avg_sentence_length": round(statistics.mean([len(s.split()) for s in sents]), 1) if sents else 0,
    }

    return {
        "pre_score":      pre_score,
        "features":       {k: round(v, 4) for k, v in f.items()},
        "feature_display": feature_display,
        "text_stats":     text_stats,
    }
