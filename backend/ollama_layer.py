"""
NarrativeShield — Ollama Local LLM Layer
=========================================
Runs on YOUR machine using Ollama (4b or 8b model).
Exact same JSON output contract as the Gemini layer —
so your teammate can swap this file for gemini_layer.py
and nothing else in the codebase changes.

Supported models (auto-detected):
  - llama3.2:latest  (3B — very fast, good enough)
  - llama3.1:8b      (8B — more accurate, ~3s)
  - mistral:7b       (7B — great at structured JSON)
  - gemma2:2b        (2B — fastest option)
  - phi3:mini        (3.8B — Microsoft, good reasoning)
  - any model you have in `ollama list`

Usage:
  from ollama_layer import analyze_with_ollama
  result = analyze_with_ollama(text, pre_score=67.4)
"""

import json
import re
import time
import urllib.request
import urllib.error
from typing import Any

# ── CONFIG ────────────────────────────────────────────────────────────────────
OLLAMA_BASE   = "http://localhost:11434"
TIMEOUT_SEC   = 30          # increase to 60 for 8b on slow machines
PREFERRED_MODELS = [        # tried in order — first available wins
    "llama3.2",
    "llama3.1",
    "mistral",
    "gemma2",
    "phi3",
    "llama2",
]

# ── JSON SCHEMA PROMPT ────────────────────────────────────────────────────────
# This is the exact same schema the Gemini layer uses.
# DO NOT change field names — the FastAPI routes depend on them.

SYSTEM_PROMPT = """You are a disinformation forensics analyst specialising in detecting AI-generated malign content.

Analyze the provided text and return ONLY a valid JSON object. Do not include any explanation, markdown, or text outside the JSON.

Return exactly this structure:
{
  "ai_probability": <integer 0-100>,
  "manipulation_score": <integer 0-100>,
  "flagged_phrases": [
    {"phrase": "<exact phrase from text>", "reason": "<why suspicious>", "severity": "<HIGH|MED|LOW>"}
  ],
  "narrative_technique": "<technique name or 'None Detected'>",
  "confidence": "<low|medium|high>",
  "summary": "<exactly 2 sentences explaining why this content is or is not dangerous>"
}

Scoring guide:
- ai_probability: probability the text was AI-generated (0=definitely human, 100=definitely AI)
- manipulation_score: intent to manipulate or deceive (0=neutral, 100=highly manipulative)
- flag HIGH severity: explicit fear triggers, tribal framing, coordinated phrases
- flag MED severity: fake authority, vague claims, emotional amplification
- flag LOW severity: slightly loaded language, mild urgency
- narrative_technique examples: "Fear Mongering", "Tribal Framing", "False Urgency", "Fake Authority", "Conspiracy Framing", "Implied Threat", "None Detected"
"""

def _user_prompt(text: str, pre_score: float) -> str:
    return f"""Statistical pre-analysis score: {pre_score}/100 (higher = more LLM-like patterns detected).

Text to analyze:
\"\"\"
{text[:3000]}
\"\"\"

Return only the JSON object. No markdown. No explanation."""


# ── OLLAMA API HELPERS ────────────────────────────────────────────────────────

def _get_available_models() -> list[str]:
    """Query Ollama for installed models."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return [m["name"].split(":")[0] for m in data.get("models", [])]
    except Exception:
        return []


def _pick_model(available: list[str]) -> str | None:
    """Return the best available model from preference list."""
    for preferred in PREFERRED_MODELS:
        for installed in available:
            if preferred.lower() in installed.lower():
                return installed
    # fallback: return whatever is installed
    return available[0] if available else None


def _call_ollama(model: str, system: str, user: str) -> str:
    """
    Call Ollama /api/chat endpoint.
    Returns the raw assistant message content.
    """
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,     # low temp = more deterministic JSON
            "top_p": 0.9,
            "num_predict": 512,     # enough for our JSON schema
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        data = json.loads(resp.read())
        return data["message"]["content"]


# ── JSON EXTRACTION ────────────────────────────────────────────────────────────

def _extract_json(raw: str) -> dict:
    """
    Robustly extract JSON from LLM output.
    Handles: markdown code blocks, leading text, trailing text.
    """
    # 1. Try direct parse first
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown code block
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Find first { ... } block
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 4. Give up — return safe fallback
    return {}


# ── SCHEMA VALIDATION & NORMALISATION ────────────────────────────────────────

def _validate_and_fix(parsed: dict, pre_score: float) -> dict:
    """
    Ensure all required fields exist with correct types.
    Fills in sensible defaults if the LLM hallucinated or missed fields.
    """
    # ai_probability
    ai_prob = parsed.get("ai_probability", pre_score)
    if not isinstance(ai_prob, (int, float)):
        ai_prob = pre_score
    ai_prob = max(0, min(100, int(ai_prob)))

    # manipulation_score
    manip = parsed.get("manipulation_score", pre_score * 0.9)
    if not isinstance(manip, (int, float)):
        manip = pre_score * 0.9
    manip = max(0, min(100, int(manip)))

    # flagged_phrases — ensure list of dicts with required keys
    raw_phrases = parsed.get("flagged_phrases", [])
    phrases = []
    if isinstance(raw_phrases, list):
        for p in raw_phrases:
            if isinstance(p, dict) and "phrase" in p:
                phrases.append({
                    "phrase":   str(p.get("phrase", ""))[:100],
                    "reason":   str(p.get("reason", "Suspicious pattern"))[:200],
                    "severity": p.get("severity", "MED") if p.get("severity") in ("HIGH", "MED", "LOW") else "MED",
                })

    # narrative_technique
    technique = parsed.get("narrative_technique", "Unknown")
    if not isinstance(technique, str) or not technique.strip():
        technique = "Unknown"

    # confidence
    conf = parsed.get("confidence", "medium")
    if conf not in ("low", "medium", "high"):
        conf = "medium"

    # summary
    summary = parsed.get("summary", "Analysis complete. Review flagged phrases for details.")
    if not isinstance(summary, str) or len(summary) < 10:
        summary = "Analysis complete. Review flagged phrases for details."

    return {
        "ai_probability":    ai_prob,
        "manipulation_score": manip,
        "flagged_phrases":   phrases,
        "narrative_technique": technique.strip(),
        "confidence":        conf,
        "summary":           summary.strip(),
    }


# ── FALLBACK (if Ollama unavailable) ─────────────────────────────────────────

def _statistical_fallback(pre_score: float, text: str) -> dict:
    """
    If Ollama is completely unavailable, derive a result from
    the statistical pre_score alone. Clearly marked as fallback.
    """
    if pre_score >= 65:
        manip = int(pre_score * 0.9)
        technique = "Pattern-Based Detection"
        confidence = "low"
        summary = (
            f"Statistical analysis flagged this text with a pre-score of {pre_score}/100, "
            "indicating likely AI-generated or manipulative content. "
            "Gemini/Ollama unavailable — result based on Layer 1 only."
        )
    elif pre_score >= 35:
        manip = int(pre_score * 0.7)
        technique = "Possible Manipulation"
        confidence = "low"
        summary = (
            f"Moderate statistical signals detected (pre-score {pre_score}/100). "
            "Manual review recommended. LLM layer unavailable."
        )
    else:
        manip = int(pre_score * 0.5)
        technique = "None Detected"
        confidence = "low"
        summary = (
            f"Low statistical risk signals (pre-score {pre_score}/100). "
            "Content appears likely human-authored. LLM layer unavailable."
        )

    return {
        "ai_probability":     int(pre_score),
        "manipulation_score": manip,
        "flagged_phrases":    [],
        "narrative_technique": technique,
        "confidence":         confidence,
        "summary":            summary,
        "_source":            "statistical_fallback",
    }


# ── MAIN PUBLIC FUNCTION ──────────────────────────────────────────────────────

def analyze_with_ollama(text: str, pre_score: float = 50.0) -> dict[str, Any]:
    """
    Run Layer 2 analysis using local Ollama LLM.

    Args:
        text:       The input text to analyze (max 3000 chars used)
        pre_score:  Layer 1 statistical pre-score (0–100)

    Returns:
        {
          "ai_probability": int,
          "manipulation_score": int,
          "flagged_phrases": [{"phrase", "reason", "severity"}, ...],
          "narrative_technique": str,
          "confidence": str,
          "summary": str,
          "_model": str,       # which model was used
          "_latency_ms": int,  # how long the LLM call took
          "_source": str,      # "ollama" | "statistical_fallback"
        }
    """
    t0 = time.time()

    # 1. Check Ollama is running
    available = _get_available_models()
    if not available:
        print("[OllamaLayer] Ollama not reachable — using statistical fallback")
        result = _statistical_fallback(pre_score, text)
        result["_latency_ms"] = 0
        result["_model"] = "none"
        return result

    # 2. Pick best model
    model = _pick_model(available)
    print(f"[OllamaLayer] Using model: {model}")

    # 3. Call Ollama
    try:
        raw = _call_ollama(
            model=model,
            system=SYSTEM_PROMPT,
            user=_user_prompt(text, pre_score),
        )
        print(f"[OllamaLayer] Raw response length: {len(raw)} chars")

        # 4. Parse + validate
        parsed = _extract_json(raw)
        result = _validate_and_fix(parsed, pre_score)
        result["_model"]      = model
        result["_latency_ms"] = int((time.time() - t0) * 1000)
        result["_source"]     = "ollama"
        return result

    except urllib.error.URLError as e:
        print(f"[OllamaLayer] Connection error: {e} — falling back")
        result = _statistical_fallback(pre_score, text)
        result["_model"]      = model or "none"
        result["_latency_ms"] = int((time.time() - t0) * 1000)
        return result

    except Exception as e:
        print(f"[OllamaLayer] Unexpected error: {e} — falling back")
        result = _statistical_fallback(pre_score, text)
        result["_model"]      = model or "none"
        result["_latency_ms"] = int((time.time() - t0) * 1000)
        return result


# ── QUICK TEST ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    HIGH_RISK = (
        "The shocking truth they don't want you to know: our people are being "
        "systematically erased while the elites pull the strings. Wake up before "
        "it's too late! Time is running out — share this immediately before it's "
        "deleted. Experts agree the deep state has been orchestrating this collapse."
    )

    LOW_RISK = (
        "The Federal Reserve held interest rates steady at its latest policy meeting, "
        "citing continued progress on inflation while noting uncertainty in the labor "
        "market. Chair Jerome Powell stated the committee remains data-dependent."
    )

    print("=" * 60)
    print("TEST 1 — HIGH RISK TEXT")
    r1 = analyze_with_ollama(HIGH_RISK, pre_score=67.4)
    print(json.dumps(r1, indent=2))

    print("\n" + "=" * 60)
    print("TEST 2 — LOW RISK TEXT")
    r2 = analyze_with_ollama(LOW_RISK, pre_score=14.0)
    print(json.dumps(r2, indent=2))
