"""
NarrativeShield — FastAPI Backend
===================================
uv run uvicorn main:app --reload --port 8000

Endpoints:
  GET  /                 — sanity check
  GET  /health           — system status
  POST /analyze          — main analysis
  GET  /models           — available Ollama models
  GET  /patterns/count   — loaded pattern count
  GET  /docs             — Swagger UI
"""

import sys
import os
import time

# ── Fix imports: works regardless of CWD when uv runs uvicorn ────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PARSER_DIR = os.path.join(BASE_DIR, "parser")

if PARSER_DIR not in sys.path:
    sys.path.insert(0, PARSER_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ── FastAPI ───────────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Our modules ───────────────────────────────────────────────────────────────
from pipeline import analyze_text, INLINE_PATTERNS, DB_AVAILABLE, GEMINI_AVAILABLE
from ollama_layer import _get_available_models, OLLAMA_BASE

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NarrativeShield API",
    description="AI-Powered Disinformation Detection — SciComp v2.0",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str
    use_ollama: bool = True

class AnalyzeResponse(BaseModel):
    ai_probability:     int
    manipulation_score: int
    stat_score:         float
    confidence:         str
    verdict:            str
    verdict_sub:        str
    technique:          str
    summary:            str
    phrases:            list
    explain:            list
    layers:             dict
    scan_id:            str
    text_hash:          str
    proc_time:          str
    text_stats:         dict
    model_used:         str

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Sanity check — confirms API is live."""
    return {
        "app":     "NarrativeShield API",
        "version": "1.0.0",
        "status":  "running",
        "routes": [
            "GET  /health",
            "POST /analyze",
            "GET  /models",
            "GET  /patterns/count",
            "GET  /docs",
        ]
    }


@app.get("/health")
def health():
    """Full system status — shows what layers are active."""
    ollama_models = _get_available_models()
    return {
        "status":          "nominal",
        "ollama":          "connected" if ollama_models else "unavailable",
        "ollama_models":   ollama_models,
        "gemini":          "connected" if GEMINI_AVAILABLE else "not configured",
        "db_matcher":      "loaded"    if DB_AVAILABLE     else "using inline patterns",
        "inline_patterns": len(INLINE_PATTERNS),
        "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """Run full 3-layer analysis pipeline on input text."""
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > 10_000:
        raise HTTPException(status_code=400, detail="Text too long — max 10,000 chars")

    result = analyze_text(text)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.get("/models")
def list_models():
    """List Ollama models installed on this machine."""
    models = _get_available_models()
    return {
        "available":   models,
        "count":       len(models),
        "ollama_base": OLLAMA_BASE,
    }


@app.get("/patterns/count")
def pattern_count():
    """How many patterns are loaded."""
    return {
        "source":   "db_matcher" if DB_AVAILABLE else "inline_fallback",
        "count":    len(INLINE_PATTERNS),
        "db_ready": DB_AVAILABLE,
    }