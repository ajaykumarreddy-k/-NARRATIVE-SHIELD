# 🛡️ NarrativeShield — Backend API

> **SciComp v2.0 · National Level Hackathon · SIMATS Engineering, Chennai**  
> Team: Ajay Kumar Reddy Krishnareddygari & Thanvarshini VR — SRMIST RMP  
> Problem #06 · Cybersecurity Sub-domain · 12 March 2026

---

## Overview

FastAPI-based backend powering the NarrativeShield 3-layer analysis pipeline:

| Layer | Module | What it does |
|---|---|---|
| **L1** | `statistical_engine.py` | Lexical repetition, entropy, sentence uniformity — offline, <50ms |
| **L2** | `gemini_layer.py` → `ollama_layer.py` | Gemini 2.0 Flash (primary) → Ollama (fallback) → stat-only |
| **L3** | `db_matcher.py` | SQLite pattern DB — 32+ malign phrase matches with severity |

---

## Folder Structure

```
backend/
├── main.py                    ← FastAPI server (run this)
├── pipeline.py                ← 3-layer orchestrator
├── statistical_engine.py      ← Layer 1: offline statistical fingerprinting
├── gemini_layer.py            ← Layer 2a: Google Gemini 2.0 Flash
├── ollama_layer.py            ← Layer 2b: Ollama local LLM fallback
├── db_matcher.py              ← Layer 3: SQLite pattern matching (auto-seeds)
├── pyproject.toml             ← uv project config
├── requirements.txt           ← pip-compatible dep list
├── llm_malign_detector/
│   ├── narrative_shield.db    ← SQLite DB (auto-created on first run)
│   ├── models.py
│   ├── schemas.py
│   └── parser_engine.py
└── .env.example               ← Copy → .env and add your Gemini API key
```

---

## Quick Start

### 1. Install dependencies (uv — recommended)

```bash
cd backend
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

### 2. Start server

```bash
uv run uvicorn main:app --reload --port 8000
```

```bash
# Verify it's running:
curl http://localhost:8000/api/health
```

### 3. (Optional) Start Ollama for local LLM fallback

```bash
ollama serve
ollama pull llama3.2   # or mistral, llama3.1 — engine auto-detects
```

> The server auto-starts Ollama if the binary is in PATH and it's not already running.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | System status — LLM mode, DB status, pattern count |
| `POST` | `/api/analyze` | **Main endpoint** — run full 3-layer analysis |
| `GET` | `/api/models` | List available Ollama models |
| `GET` | `/api/patterns/count` | Loaded malign pattern count |
| `GET` | `/docs` | Auto-generated Swagger UI |

### POST `/api/analyze` — Request

```json
{
  "text": "The elites don't want you to know...",
  "api_key": "AIzaSy..."
}
```

### POST `/api/analyze` — Response

```json
{
  "ai_probability": 87,
  "manipulation_score": 79,
  "stat_score": 61.3,
  "confidence": "high",
  "verdict": "HIGH_RISK",
  "verdict_sub": "Multiple manipulation techniques detected",
  "technique": "Fear Mongering / Emotional Manipulation",
  "summary": "Content uses tribal framing and false urgency tactics...",
  "phrases": [
    {
      "phrase": "the elites",
      "category": "us_vs_them",
      "catLabel": "Us vs Them",
      "severity": "HIGH",
      "char_start": 4,
      "char_end": 14,
      "reason": "Tribal framing — divides audience against an out-group",
      "source": "db_match"
    }
  ],
  "explain": [
    { "feat": "Repetition Ratio", "pct": 42, "color": "#7c3aed" }
  ],
  "layers": { "l1": 61, "l2": 79, "l3": 60 },
  "scan_id": "SCN-4821",
  "text_hash": "A3F9B2C1",
  "proc_time": "1.2s",
  "text_stats": { "word_count": 84, "sentence_count": 6 },
  "model_used": "gemini"
}
```

---

## Pipeline Fallback Chain

```
User submits text + API key
        │
        ▼
[L1] Statistical Engine ─────────────────────── always runs (<50ms)
        │
        ▼
[L2] Gemini 2.0 Flash ─── fails? ──► Ollama ─── fails? ──► Stat-only fallback
        │
        ▼
[L3] SQLite DB Matcher ─── not available? ──► 44-pattern inline fallback
        │
        ▼
Merged result → JSON response
```

---

## Database — Auto-Seeding

`db_matcher.py` auto-creates and seeds `narrative_shield.db` on first import.  
No manual setup required. Seeded with **32 patterns** across 7 categories:

| Category | Examples |
|---|---|
| `emotional_amplifier` | "shocking truth", "wake up people" |
| `us_vs_them` | "the elites", "deep state", "real citizens" |
| `false_urgency` | "before it's deleted", "share immediately" |
| `fake_authority` | "experts agree", "insiders confirm" |
| `conspiracy_frame` | "cover-up", "what they don't tell" |
| `fear_trigger` | "imminent threat", "blackout" |
| `coordinated_marker` | "spread the word", "share this before" |

---

## Environment Variables

```bash
# .env (copy from .env.example — never commit)
GEMINI_API_KEY=AIzaSy...   # Optional — can be passed per-request instead
```

> **Security:** The API key is passed per-request from the frontend — no server-side storage required. The `.env` file is for local development convenience only.

---

## Test with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Full analysis (replace API key)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Wake up people! The deep state is orchestrating a collapse. Share immediately before it gets deleted.",
    "api_key": "YOUR_GEMINI_KEY"
  }'

# Works without API key (uses statistical + DB pattern fallback)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Wake up people! The deep state...", "api_key": ""}'
```

---

## Performance Targets

| Metric | Target | Notes |
|---|---|---|
| Layer 1 (stats) | < 50ms | Pure Python, no API |
| Layer 2 (Gemini) | < 2s | Gemini 2.0 Flash free tier |
| Layer 2 (Ollama) | < 5s | Local model, hardware-dependent |
| Layer 3 (DB) | < 10ms | SQLite indexed lookup |
| **End-to-end** | **< 3s** | With Gemini |

---

## Demo Flow for Judges

```bash
# Terminal 1: Start backend
cd backend && uv sync && uv run uvicorn main:app --reload --port 8000

# Terminal 2: Start frontend
cd .. && npm run dev

# Open http://localhost:3000
# 1. Click the demo case "Deepfake Transcript"
# 2. Add your Gemini API key (click the status button)
# 3. Click ANALYZE NARRATIVE
# 4. Watch the gauge hit 80%+, phrases light up red
# 5. Show /docs for technical credibility
```
