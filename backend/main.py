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
  GET  /docs             — Swagger UI (auto-generated)

Ollama is auto-started on startup if not already running.
"""

import sys
import os
import time
import subprocess
import shutil
from contextlib import asynccontextmanager

# ── Fix imports: works regardless of CWD ─────────────────────────────────────
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
from pipeline import analyze_text, INLINE_PATTERNS, DB_AVAILABLE, GEMINI_AVAILABLE, _get_llm_mode
from ollama_layer import _get_available_models, OLLAMA_BASE


# ── Ollama auto-start helpers ─────────────────────────────────────────────────

def _ollama_is_running() -> bool:
    """Ping Ollama — True if already up."""
    import urllib.request, urllib.error
    try:
        urllib.request.urlopen(f"{OLLAMA_BASE}/api/tags", timeout=2)
        return True
    except Exception:
        return False


def _start_ollama() -> bool:
    """
    Launch `ollama serve` as a detached background process.
    Returns True once Ollama is reachable (max 10s wait).
    """
    if _ollama_is_running():
        print("[Ollama] Already running ✓")
        return True

    if not shutil.which("ollama"):
        print("[Ollama] ✗ ollama binary not in PATH — skipping auto-start")
        return False

    print("[Ollama] Not running — launching `ollama serve` in background...")
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,   # fully detach (works on Linux + Mac)
        )
    except Exception as e:
        print(f"[Ollama] Failed to launch: {e}")
        return False

    # Wait up to 10s for it to become reachable
    for i in range(10):
        time.sleep(1)
        if _ollama_is_running():
            print(f"[Ollama] Ready after {i + 1}s ✓")
            return True
        print(f"[Ollama] Waiting... ({i + 1}/10)")

    print("[Ollama] Timed out — running in offline/stat-only mode")
    return False


# ── Lifespan: startup + shutdown ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("\n" + "═" * 52)
    print("  NarrativeShield API — Starting up")
    print("═" * 52)

    _start_ollama()

    models = _get_available_models()
    if models:
        print(f"[Ollama]   Models: {', '.join(models)}")
    else:
        print("[Ollama]   No models — stat-only fallback mode")

    mode = _get_llm_mode()
    print(f"[Pipeline] LLM mode  : {mode.upper()}")
    print(f"[Pipeline] DB matcher: {'loaded ✓' if DB_AVAILABLE else 'inline fallback'}")
    print(f"[Pipeline] Gemini    : {'loaded ✓' if GEMINI_AVAILABLE else 'not configured'}")
    print("═" * 52 + "\n")

    yield  # app runs here

    # SHUTDOWN
    print("\n[NarrativeShield] Shut down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="NarrativeShield API",
    description="AI-Powered Disinformation Detection — SciComp v2.0",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response models ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str
    api_key: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Sanity check — API is live."""
    return {
        "app":     "NarrativeShield API",
        "version": "1.0.0",
        "status":  "running",
    }


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """Run full 3-layer analysis pipeline."""
    text = req.text.strip()
    api_key = req.api_key.strip()
    
    if not text or not api_key:
        raise HTTPException(status_code=400, detail="Text and API key are required")
        
    if len(text) > 10_000:
        raise HTTPException(status_code=400, detail="Text too long — max 10,000 chars")

    result = analyze_text(text, api_key=api_key)

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.get("/models")
def list_models():
    """List Ollama models on this machine."""
    models = _get_available_models()
    return {
        "available":   models,
        "count":       len(models),
        "ollama_base": OLLAMA_BASE,
    }


@app.get("/patterns/count")
def pattern_count():
    """How many malign patterns are loaded."""
    return {
        "source":   "db_matcher" if DB_AVAILABLE else "inline_fallback",
        "count":    len(INLINE_PATTERNS),
        "db_ready": DB_AVAILABLE,
    }
