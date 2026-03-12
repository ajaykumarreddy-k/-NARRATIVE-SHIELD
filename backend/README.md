# NarrativeShield — Backend Setup

## YOUR FOLDER STRUCTURE

```
narrativeshield/
├── main.py                  ← FastAPI app  (YOU run this)
├── requirements.txt
├── .env                     ← GEMINI_API_KEY=... (teammate adds)
└── parser/
    ├── statistical_engine.py ← Layer 1  (YOU own this)
    ├── ollama_layer.py       ← Layer 2a (YOU own this)
    ├── pipeline.py           ← Master orchestrator (YOU own this)
    ├── gemini_layer.py       ← Layer 2b (TEAMMATE adds this)
    └── db_matcher.py         ← Layer 3  (TEAMMATE adds this)
```

---

## STEP 1 — Install dependencies

```bash
pip install fastapi uvicorn
```

---

## STEP 2 — Make sure Ollama is running

```bash
ollama serve
# In another terminal, check your models:
ollama list
```

If you have `llama3.2` or `llama3.1` or `mistral` — you're good.
The `ollama_layer.py` auto-detects whatever model you have.

---

## STEP 3 — Run the server

```bash
cd narrativeshield
python main.py
# OR
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs to see the Swagger UI.
Open http://localhost:8000/health to check all systems.

---

## STEP 4 — Test it

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "The shocking truth they dont want you to know: our people are being erased."}'
```

---

## WHAT YOUR TEAMMATE NEEDS TO BUILD

### gemini_layer.py
Must export: `analyze_with_gemini(text: str, pre_score: float) -> dict`
Return schema must be identical to `ollama_layer.analyze_with_ollama()`:
```python
{
  "ai_probability": int,
  "manipulation_score": int,
  "flagged_phrases": [{"phrase", "reason", "severity"}],
  "narrative_technique": str,
  "confidence": str,   # "low" | "medium" | "high"
  "summary": str,
}
```

### db_matcher.py
Must export: `match_patterns(text: str) -> list[dict]`
Each dict must have:
```python
{
  "phrase": str,
  "category": str,
  "catLabel": str,
  "catClass": str,    # "emo" | "uvt" | "fur" | "fau"
  "severity": str,    # "HIGH" | "MED" | "LOW"
  "char_start": int,
  "char_end": int,
  "source": "db",
  "reason": str,
}
```

---

## CONNECT TO REACT FRONTEND

In your React app, replace mock data calls with:
```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: inputText })
});
const result = await response.json();
```

The response shape is identical to the DEMOS mock data — no frontend changes needed.

---

## DEMO FLOW FOR JUDGES

1. Start Ollama: `ollama serve`
2. Start API:    `uvicorn main:app --reload`
3. Open React frontend
4. Paste HIGH RISK text → watch live results
5. Show http://localhost:8000/docs for technical credibility
