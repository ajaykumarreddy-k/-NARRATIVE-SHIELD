"""
NarrativeShield — FastAPI Backend
===================================
Run: uvicorn main:app --reload --port 8000

Endpoints:
  POST /analyze          — main analysis endpoint
  GET  /health           — system health check
  GET  /models           — list available Ollama models
  GET  /patterns/count   — how many patterns are in DB

Your teammate's gemini_layer.py and db_matcher.py
drop into the same /parser folder — pipeline.py picks
them up automatically via try/except imports.
"""

import sys
import os
import time

# Add parser directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "parser"))

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
except ImportError:
    print("ERROR: FastAPI not installed. Run: pip install fastapi uvicorn")
    sys.exit(1)

from pipeline import analyze_text, INLINE_PATTERNS, DB_AVAILABLE, GEMINI_AVAILABLE
from ollama_layer import _get_available_models, OLLAMA_BASE
import urllib.request
import json

# ── APP ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NarrativeShield API",
    description="AI-Powered Disinformation Detection — SciComp v2.0",
    version="1.0.0",
)

# Allow React frontend on any port during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REQUEST / RESPONSE MODELS ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str
    use_ollama: bool = True   # set False to force statistical-only (fast demo)

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

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """System health check — shows what's available."""
    ollama_models = _get_available_models()
    ollama_ok = len(ollama_models) > 0

    return {
        "status":          "nominal",
        "ollama":          "connected" if ollama_ok else "unavailable",
        "ollama_models":   ollama_models,
        "gemini":          "connected" if GEMINI_AVAILABLE else "not configured",
        "db_matcher":      "loaded"    if DB_AVAILABLE     else "using inline patterns",
        "inline_patterns": len(INLINE_PATTERNS),
        "timestamp":       time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Main analysis endpoint.
    Runs full 3-layer pipeline and returns the result.
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > 10_000:
        raise HTTPException(status_code=400, detail="Text too long — max 10,000 characters")

    result = analyze_text(text)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.get("/models")
def list_models():
    """List all available Ollama models on this machine."""
    models = _get_available_models()
    return {
        "available": models,
        "count": len(models),
        "ollama_base": OLLAMA_BASE,
    }


@app.get("/patterns/count")
def pattern_count():
    """How many patterns are loaded (DB or inline)."""
    return {
        "source":  "db_matcher" if DB_AVAILABLE else "inline_fallback",
        "count":   len(INLINE_PATTERNS),
        "db_ready": DB_AVAILABLE,
    }


# ── DEV SERVER ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        import uvicorn
        print("\n" + "="*50)
        print("  NarrativeShield API starting...")
        print("  http://localhost:8000")
        print("  http://localhost:8000/docs  ← Swagger UI")
        print("  http://localhost:8000/health")
        print("="*50 + "\n")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        print("Install uvicorn: pip install uvicorn")
