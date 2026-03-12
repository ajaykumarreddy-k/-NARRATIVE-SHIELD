# 🛡️ NarrativeShield
### AI-Powered Disinformation Forensics Platform

> **"Doesn't just detect — it explains EXACTLY which phrases are weaponized, which manipulation technique was used, and WHY the content is dangerous — in under 2 seconds."**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-4285F4?style=flat-square&logo=google)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 🎯 What is NarrativeShield?

NarrativeShield is a **real-time disinformation forensics platform** built for content moderation teams, journalists, and security analysts. While most tools return a single score, NarrativeShield tells you **what** is suspicious, **why** it's dangerous, and **which manipulation technique** was deployed — all in under 2 seconds.

Built in 5 hours at **SciComp v2.0 · SIMATS Engineering, Chennai** — Problem #06 Cybersecurity Track.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| ⚡ **Dual-Layer AI Pipeline** | Local statistical fingerprinting (50ms, offline) + Gemini 1.5 Flash structured JSON |
| 🎯 **Inline Phrase Highlights** | Every flagged phrase highlighted in red/orange/yellow with hover tooltips explaining WHY |
| 📊 **Live Manipulation Score Gauge** | Animated 0–100 gauge that fills red as risk rises — judges see the needle move live |
| 🗂️ **Provenance Report** | Structured breakdown: AI probability, manipulation technique, flagged phrase table, summary |
| 🔍 **Malign Pattern Database** | 50+ curated propaganda and manipulation markers across 7 categories |
| 📜 **Scan History** | Persistent sidebar showing last 10 scans with verdict badges |
| 📉 **Explainability Panel** | SHAP-style bar chart showing which statistical features drove the score |
| 🔌 **Offline Fallback** | Cached responses ensure demo works even when WiFi drops |

---

## 🏗️ Architecture — 3-Layer Detection Pipeline

```
INPUT TEXT
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 1 · Statistical Fingerprinting  (<50ms)      │
│  • Text entropy  • Sentence-length variance         │
│  • Lexical repetition ratio  • Punctuation unifor.  │
│  • Perplexity proxy  →  pre_score (0–100)           │
└─────────────────────┬───────────────────────────────┘
                      │ pre_score as context
                      ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 2 · Gemini 1.5 Flash  (structured JSON)      │
│  • ai_probability  • manipulation_score             │
│  • flagged_phrases[]  • narrative_technique         │
│  • confidence  • summary                            │
└─────────────────────┬───────────────────────────────┘
                      │ flagged phrases
                      ▼
┌─────────────────────────────────────────────────────┐
│  LAYER 3 · Malign Pattern DB Lookup  (SQLite)       │
│  • Match phrases against 50+ known propaganda markers│
│  • Enrich with category, severity, technique tags   │
│  → Final provenance report                          │
└─────────────────────────────────────────────────────┘
```

**Why dual-layer?** Most teams use LLM as a black box. Our statistical pre-score (1) runs offline with zero API cost, (2) catches coordination signals no LLM sees (repetition ratio, entropy drops), and (3) provides Gemini with grounding context that measurably improves its analysis quality.

---

## 🖥️ Screenshots

> *(Add your screenshots here — input panel, score gauge firing red, highlighted text, provenance report)*

| Analysis Dashboard | Phrase Highlights | Provenance Report |
|---|---|---|
| `[screenshot-dashboard.png]` | `[screenshot-highlights.png]` | `[screenshot-report.png]` |

---

## 📹 Demo Video

▶️ **[Watch the 2-minute demo](YOUR_VIDEO_LINK_HERE)**

Sample output on a HIGH RISK input:
```
ai_probability:    91 / 100
manipulation_score: 87 / 100
verdict:           ⛔ HIGH_RISK
technique:         fear_mongering + us_vs_them
flagged phrases:   6  (2 HIGH, 3 MED, 1 LOW)
confidence:        high
processing time:   1.4s
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A Gemini API key (free tier) → [Get one here](https://ai.google.dev/)

### 1. Clone & configure
```bash
git clone https://github.com/YOUR_USERNAME/narrative-shield.git
cd narrative-shield
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
python seed_patterns.py      # Populates the Malign Pattern DB (run once)
uvicorn main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

### 4. Verify everything works
```bash
# Health check
curl http://localhost:8000/health

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "The shocking truth they dont want you to know: our people are being erased by the elites."}'
```

Expected response shape:
```json
{
  "pre_score": 71.3,
  "ai_probability": 88,
  "manipulation_score": 83,
  "final_verdict": "HIGH_RISK",
  "narrative_technique": "fear_mongering",
  "confidence": "high",
  "flagged_phrases": [
    {"phrase": "shocking truth", "reason": "Emotional amplifier bypassing rational thinking", "severity": "HIGH"},
    {"phrase": "the elites", "reason": "Us-vs-them tribal framing", "severity": "HIGH"},
    {"phrase": "they dont want you to know", "reason": "Conspiracy frame — manufactured secrecy", "severity": "HIGH"}
  ],
  "summary": "Content employs coordinated fear-mongering and tribal framing. High probability of AI-assisted generation."
}
```

---

## 📁 Project Structure

```
narrative-shield/
├── README.md
├── requirements.txt
├── .env.example              ← GEMINI_API_KEY=your_key_here
├── .gitignore                ← .env and __pycache__ excluded
├── backend/
│   ├── main.py               ← FastAPI app · /analyze · /history · /health
│   ├── statistical_engine.py ← Layer 1: entropy, variance, perplexity proxy
│   ├── gemini_layer.py       ← Layer 2: Gemini 1.5 Flash structured JSON
│   ├── db_matcher.py         ← Layer 3: SQLite pattern matching + enrichment
│   ├── pipeline.py           ← Master orchestrator (calls all 3 layers)
│   ├── database.py           ← SQLite init, CRUD helpers
│   └── seed_patterns.py      ← Run once to seed 50+ malign patterns
├── src/                      ← React frontend (Vite + TypeScript)
│   ├── App.tsx
│   ├── Dashboard.jsx
│   ├── ScoreGauge.jsx        ← Recharts animated gauge
│   ├── HighlightText.jsx     ← react-highlight-words inline flags
│   └── ProvenanceReport.jsx  ← Structured report panel
├── data/
│   └── narrative_shield.db   ← SQLite DB (committed with seed data)
└── demo/
    └── demo.mp4
```

---

## 🧠 Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Async endpoints, auto-docs at `/docs`, minimal boilerplate |
| AI — LLM | Google Gemini 1.5 Flash | Free tier, sub-2s, enforces JSON schema output |
| AI — Stats | textstat + custom functions | Fully offline, zero API cost, catches coordination signals |
| Database | SQLite (built-in Python) | Zero setup, ships in the repo, instant queries |
| Frontend | React 18 + Vite + TypeScript | Component model ideal for real-time result updates |
| Styling | Tailwind CSS | Rapid polish — no separate CSS files |
| Charts | Recharts | Animated gauge, confidence bars |
| Highlights | react-highlight-words | One-line inline phrase highlighting |

---

## 🗄️ Database Schema

**`malign_patterns`** — 50+ curated propaganda markers across 7 categories:

| Category | Examples |
|---|---|
| `emotional_amplifier` | *shocking truth, wake up, outrageous* |
| `false_urgency` | *before it's deleted, share immediately* |
| `us_vs_them` | *real citizens, the elites, deep state* |
| `fake_authority` | *experts agree, studies show* (no citation) |
| `fear_trigger` | *imminent threat, danger to your family* |
| `conspiracy_frame` | *the real truth, what they hide, suppressed* |
| `coordinated_marker` | Identical phrasing across multiple documents |

**`analysis_results`** — Every scan persisted with SHA-256 hash for duplicate detection.

**`flagged_phrases`** — One row per flagged phrase, linked to scan and pattern, with character positions for inline highlighting.

---

## 📊 Performance Metrics

| Metric | Value |
|---|---|
| Layer 1 (statistical) latency | < 50ms |
| Full pipeline latency (incl. Gemini) | ~1.4s average |
| Malign pattern database | 50+ entries, 7 categories |
| Demo cases | 3 preloaded (human article / AI propaganda / subtle manipulation) |
| Gemini tier | Free — zero cost for judges to run |
| Offline fallback | ✅ Cached responses for WiFi-down scenarios |

---

## 🎬 3 Preloaded Demo Cases

| Case | Type | Expected Verdict |
|---|---|---|
| **Demo A** | Human-written news article | `LOW` — score ~15 |
| **Demo B** | AI-generated propaganda sample | `HIGH_RISK` — score ~87 |
| **Demo C** | Subtle AI-assisted manipulation | `MEDIUM` — score ~54 |

Click any demo button in the UI to load instantly — no copy-paste needed for the live pitch.

---

## 🔌 API Reference

Full interactive docs at **`http://localhost:8000/docs`**

| Endpoint | Method | Description |
|---|---|---|
| `/analyze` | POST | Submit text → full 3-layer analysis JSON |
| `/history` | GET | Last 10 scan results with verdicts |
| `/health` | GET | System status (DB, Gemini, stats engine) |

---

## 👥 Team

| Name | Role | Institution |
|---|---|---|
| **Ajay Kumar Reddy Krishnareddygari** | Backend · AI Pipeline · DB | SRMIST RMP |
| **Thanvarshini VR** | Frontend · UI/UX · Integration | SRMIST RMP |

**Hackathon:** SciComp v2.0 · National Level · SIMATS Engineering, Chennai · 12 March 2026  
**Problem:** #06 · Cybersecurity Sub-domain · 5-Hour Sprint

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>NarrativeShield</strong> · Built in 5 hours · SciComp v2.0 · 12 March 2026<br/>
  <em>Giving every content moderation team a forensics-grade AI analyst in their browser.</em>
</p>
