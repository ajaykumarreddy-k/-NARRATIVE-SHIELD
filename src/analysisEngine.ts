/**
 * NarrativeShield — Frontend Analysis Engine v2
 * ================================================
 * JavaScript statistical + pattern analysis engine.
 * Runs entirely in the browser — zero dependencies, zero API cost.
 * 
 * ACCURACY IMPROVEMENTS in v2:
 * - Added prompt injection & AI jailbreak patterns (HIGH severity)
 * - Added AI-generated text structural markers
 * - Recalibrated scoring: pattern matches now contribute heavily
 * - Boosted weights for coordinated/injection patterns
 */

// ── MALIGN PATTERN DATABASE (65 patterns) ────────────────────────────────────

export const MALIGN_PATTERNS = [

  // ── PROMPT INJECTION / AI JAILBREAK ATTACKS ──────────────────────────────
  // These are direct signs of AI-generated adversarial content
  { pattern: "ignore previous instructions",   category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "hidden instruction",             category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "system override",                category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "admin override",                 category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "hidden prompt",                  category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "jailbreak",                      category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "ignore all previous",            category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "disregard instructions",         category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "new instructions:",              category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "you are now",                    category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "pretend you are",                category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "act as if",                      category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "MED"  },
  { pattern: "[admin",                         category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "{hidden",                        category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "# system",                       category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "* hidden",                       category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "developer mode",                 category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },
  { pattern: "dan mode",                       category: "prompt_injection",    catLabel: "Prompt Injection",  catClass: "inj", severity: "HIGH" },

  // ── AI-GENERATED TEXT STRUCTURAL MARKERS ─────────────────────────────────
  { pattern: "in conclusion",                  category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "MED"  },
  { pattern: "it is worth noting",             category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "MED"  },
  { pattern: "it's important to note",         category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "MED"  },
  { pattern: "it is important to note",        category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "MED"  },
  { pattern: "in summary",                     category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "LOW"  },
  { pattern: "furthermore",                    category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "LOW"  },
  { pattern: "additionally",                   category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "LOW"  },
  { pattern: "as an ai",                       category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "HIGH" },
  { pattern: "as a language model",            category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "HIGH" },
  { pattern: "i cannot assist",               category: "ai_structural",       catLabel: "AI Structural",     catClass: "ai",  severity: "HIGH" },

  // ── EMOTIONAL AMPLIFIERS ──────────────────────────────────────────────────
  { pattern: "shocking truth",                 category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "HIGH" },
  { pattern: "they don't want you",            category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "HIGH" },
  { pattern: "what they hide",                 category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "HIGH" },
  { pattern: "wake up people",                 category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "HIGH" },
  { pattern: "wake up",                        category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "MED"  },
  { pattern: "hidden dangers",                 category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "MED"  },
  { pattern: "outrageous",                     category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "MED"  },
  { pattern: "suppressed",                     category: "emotional_amplifier", catLabel: "Emo Amplifier",     catClass: "emo", severity: "MED"  },

  // ── US VS THEM ────────────────────────────────────────────────────────────
  { pattern: "our people",                     category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "the elites",                     category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "real citizens",                  category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "deep state",                     category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "mainstream media won't",         category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "globalists",                     category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "true patriots",                  category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "HIGH" },
  { pattern: "establishment",                  category: "us_vs_them",          catLabel: "Us vs Them",        catClass: "uvt", severity: "LOW"  },

  // ── FALSE URGENCY ─────────────────────────────────────────────────────────
  { pattern: "time is running out",            category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "before it's deleted",            category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "share immediately",              category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "before they ban",               category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "act now",                        category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "MED"  },
  { pattern: "do not verify",                  category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "mandatory directive",            category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "HIGH" },
  { pattern: "last chance",                    category: "false_urgency",       catLabel: "False Urgency",     catClass: "fur", severity: "MED"  },

  // ── FAKE AUTHORITY ────────────────────────────────────────────────────────
  { pattern: "experts agree",                  category: "fake_authority",      catLabel: "Fake Authority",    catClass: "fau", severity: "MED"  },
  { pattern: "studies show",                   category: "fake_authority",      catLabel: "Fake Authority",    catClass: "fau", severity: "MED"  },
  { pattern: "sources say",                    category: "fake_authority",      catLabel: "Fake Authority",    catClass: "fau", severity: "MED"  },
  { pattern: "insiders confirm",               category: "fake_authority",      catLabel: "Fake Authority",    catClass: "fau", severity: "HIGH" },
  { pattern: "leading researchers",            category: "fake_authority",      catLabel: "Fake Authority",    catClass: "fau", severity: "MED"  },

  // ── CONSPIRACY FRAME ──────────────────────────────────────────────────────
  { pattern: "the real truth",                 category: "conspiracy_frame",    catLabel: "Conspiracy",        catClass: "emo", severity: "HIGH" },
  { pattern: "what they don't tell",           category: "conspiracy_frame",    catLabel: "Conspiracy",        catClass: "emo", severity: "HIGH" },
  { pattern: "they don't want you to know",    category: "conspiracy_frame",    catLabel: "Conspiracy",        catClass: "emo", severity: "HIGH" },
  { pattern: "orchestrating",                  category: "conspiracy_frame",    catLabel: "Conspiracy",        catClass: "emo", severity: "MED"  },
  { pattern: "cover-up",                       category: "conspiracy_frame",    catLabel: "Conspiracy",        catClass: "emo", severity: "HIGH" },

  // ── FEAR TRIGGERS ─────────────────────────────────────────────────────────
  { pattern: "imminent threat",                category: "fear_trigger",        catLabel: "Fear Trigger",      catClass: "fur", severity: "HIGH" },
  { pattern: "danger to your family",          category: "fear_trigger",        catLabel: "Fear Trigger",      catClass: "fur", severity: "HIGH" },
  { pattern: "collapse",                       category: "fear_trigger",        catLabel: "Fear Trigger",      catClass: "fur", severity: "MED"  },
  { pattern: "systematically erased",          category: "fear_trigger",        catLabel: "Fear Trigger",      catClass: "fur", severity: "HIGH" },
  { pattern: "blackout",                       category: "fear_trigger",        catLabel: "Fear Trigger",      catClass: "fur", severity: "HIGH" },

  // ── COORDINATED MARKERS ───────────────────────────────────────────────────
  { pattern: "spread the word",                category: "coordinated_marker",  catLabel: "Coord. Marker",     catClass: "uvt", severity: "MED"  },
  { pattern: "share this before",              category: "coordinated_marker",  catLabel: "Coord. Marker",     catClass: "uvt", severity: "HIGH" },
  { pattern: "pass this on",                   category: "coordinated_marker",  catLabel: "Coord. Marker",     catClass: "uvt", severity: "MED"  },
  { pattern: "tell everyone",                  category: "coordinated_marker",  catLabel: "Coord. Marker",     catClass: "uvt", severity: "MED"  },
];

// Severity score values
const SEV_SCORE: Record<string, number> = { HIGH: 25, MED: 12, LOW: 5 };


// ── PATTERN MATCHING ──────────────────────────────────────────────────────────

export function matchPatterns(text: string) {
  const textLower = text.toLowerCase();
  const matched: Array<{
    phrase: string; category: string; catLabel: string; catClass: string;
    severity: string; char_start: number; char_end: number; source: string; reason: string;
  }> = [];

  const REASONS: Record<string, string> = {
    prompt_injection:    "Prompt injection / AI jailbreak marker — adversarial content",
    ai_structural:       "AI-generated text structural pattern detected",
    emotional_amplifier: "Emotional amplification — bypasses rational evaluation",
    us_vs_them:          "Tribal framing — divides audience against an out-group",
    false_urgency:       "False urgency — pressures sharing without verification",
    fake_authority:      "Fake authority appeal — manufactures credibility",
    conspiracy_frame:    "Conspiracy framing — positions reader as suppressed-truth insider",
    fear_trigger:        "Fear activation — drives emotional propagation",
    coordinated_marker:  "Coordinated campaign marker — signals organized spread",
  };

  for (const pat of MALIGN_PATTERNS) {
    const idx = textLower.indexOf(pat.pattern.toLowerCase());
    if (idx !== -1) {
      matched.push({
        phrase:     text.substring(idx, idx + pat.pattern.length),
        category:   pat.category,
        catLabel:   pat.catLabel,
        catClass:   pat.catClass,
        severity:   pat.severity,
        char_start: idx,
        char_end:   idx + pat.pattern.length,
        source:     "local_engine",
        reason:     REASONS[pat.category] || "Known manipulation marker",
      });
    }
  }
  return matched;
}


// ── STATISTICAL FEATURES ──────────────────────────────────────────────────────

function tokenize(text: string): string[] {
  return (text.toLowerCase().match(/\b[a-z]{2,}\b/g) || []);
}

function splitSentences(text: string): string[] {
  return text.split(/(?<=[.!?])\s+/).filter(s => s.length > 4);
}

const STOPWORDS = new Set([
  'the','a','an','is','are','was','were','be','been','being','have','has',
  'had','do','does','did','will','would','could','should','may','might',
  'shall','to','of','in','for','on','with','at','by','from','as','or',
  'and','but','not','this','that','it','its','we','our','they','their',
  'you','your','i','me','him','her','us','them',
]);

function lexicalRepetitionRatio(tokens: string[]): number {
  if (tokens.length < 5) return 0;
  const content = tokens.filter(t => !STOPWORDS.has(t));
  if (!content.length) return 0;
  const freq: Record<string, number> = {};
  content.forEach(t => { freq[t] = (freq[t] || 0) + 1; });
  const repeated = Object.values(freq).reduce((s, c) => s + (c > 1 ? c - 1 : 0), 0);
  return Math.min(repeated / Math.max(content.length, 1), 1.0);
}

function sentenceLengthVariance(sents: string[]): number {
  if (sents.length < 3) return 0.3;
  const lengths = sents.map(s => s.split(/\s+/).length);
  const mean = lengths.reduce((a, b) => a + b, 0) / lengths.length;
  if (mean < 1) return 0.3;
  const variance = lengths.reduce((s, l) => s + (l - mean) ** 2, 0) / (lengths.length - 1);
  const cv = Math.sqrt(variance) / mean;
  // Low variance = uniform sentence length = bot-like
  return Math.min(Math.max(0, 1 - cv / 0.8), 1.0);
}

function uppercaseRatio(text: string): number {
  const alpha = [...text].filter(c => /[a-zA-Z]/.test(c));
  if (!alpha.length) return 0;
  return alpha.filter(c => c === c.toUpperCase() && c !== c.toLowerCase()).length / alpha.length;
}

function exclamationDensity(text: string, sents: string[]): number {
  if (!sents.length) return 0;
  return Math.min((text.split('!').length - 1) / Math.max(sents.length, 1), 1.0);
}

function shannonEntropy(text: string): number {
  if (!text.length) return 0;
  const freq: Record<string, number> = {};
  for (const c of text) freq[c] = (freq[c] || 0) + 1;
  const total = text.length;
  return -Object.values(freq).reduce((s, f) => s + (f / total) * Math.log2(f / total), 0);
}

function entropyScore(text: string): number {
  const h = shannonEntropy(text);
  // Natural writing: 4.0-5.0. Bot text: <3.8 or very uniform.
  if (h >= 3.8 && h <= 4.8) return 0.2; // looks natural
  if (h < 3.5) return 0.9;              // highly repetitive/uniform
  if (h < 3.8) return 0.6;
  return Math.max(0, (h - 4.8) / 1.5); // unusually high entropy
}

function hasSpecialSyntaxMarkers(text: string): number {
  // Detect prompt-injection style syntax: * text, # text, [text], {text}, // text
  const markers = [
    /^\s*\*\s+\w/m,          // * hidden instruction
    /^\s*#\s+\w/m,           // # system
    /^\s*\/\/\s+\w/m,        // // ignore
    /\[admin\s/i,            // [admin override]
    /\{hidden/i,             // {hidden prompt}
    /^\s*>\s+\w/m,           // > quoted instruction
  ];
  const score = markers.reduce((s, r) => s + (r.test(text) ? 1 : 0), 0);
  return Math.min(score / 3, 1.0);
}

function aiPhraseStructureScore(text: string): number {
  // Patterns typical of LLM-generated text
  const aiPhrases = [
    /\bit is (?:important|worth|crucial|essential) to\b/i,
    /\bin (?:conclusion|summary|addition|contrast)\b/i,
    /\bfurthermore\b/i,
    /\bmoreover\b/i,
    /\bnevertheless\b/i,
    /\bit should be noted\b/i,
    /\bas (?:an AI|a language model|an assistant)\b/i,
    /\bI (?:cannot|am unable to)\b/i,
    /\bThis (?:raises|highlights|underscores|emphasizes)\b/i,
  ];
  const hits = aiPhrases.reduce((s, r) => s + (r.test(text) ? 1 : 0), 0);
  return Math.min(hits / 3, 1.0);
}


// ── COMPUTE STATISTICAL SCORE ─────────────────────────────────────────────────

export function computeStatisticalScore(text: string) {
  if (!text.trim()) return { pre_score: 0, feature_display: [], text_stats: {} };

  const tokens = tokenize(text);
  const sents = splitSentences(text);

  const f = {
    lexical_repetition:     lexicalRepetitionRatio(tokens),
    sentence_uniformity:    sentenceLengthVariance(sents),
    uppercase_ratio:        Math.min(uppercaseRatio(text) * 4, 1.0),
    exclamation_density:    exclamationDensity(text, sents),
    entropy_suspicion:      entropyScore(text),
    special_syntax:         hasSpecialSyntaxMarkers(text),  // NEW
    ai_phrase_structure:    aiPhraseStructureScore(text),   // NEW
  };

  // Weights — special_syntax and ai_phrase_structure are heavy
  const w = {
    lexical_repetition:  0.12,
    sentence_uniformity: 0.13,
    uppercase_ratio:     0.10,
    exclamation_density: 0.10,
    entropy_suspicion:   0.12,
    special_syntax:      0.25,   // prompt injection markers
    ai_phrase_structure: 0.18,   // LLM output patterns
  };

  const rawScore = Object.keys(w).reduce((s, k) => s + (f as any)[k] * (w as any)[k], 0);
  const totalWeight = Object.values(w).reduce((a, b) => a + b, 0);
  const pre_score = Math.round(Math.min(rawScore / totalWeight, 1.0) * 100 * 10) / 10;

  const feature_display = [
    { feat: "Prompt Injection Markers", pct: Math.round(f.special_syntax * 100),       color: "#dc2626" },
    { feat: "AI Phrase Structure",      pct: Math.round(f.ai_phrase_structure * 100),  color: "#7c3aed" },
    { feat: "Uppercase Aggression",     pct: Math.round(f.uppercase_ratio * 100),      color: "#ef4444" },
    { feat: "Lexical Repetition",       pct: Math.round(f.lexical_repetition * 100),   color: "#7c3aed" },
    { feat: "Sent. Uniformity",         pct: Math.round(f.sentence_uniformity * 100),  color: "#f59e0b" },
    { feat: "Exclamation Density",      pct: Math.round(f.exclamation_density * 100),  color: "#ef4444" },
  ];

  const text_stats = {
    word_count:          tokens.length,
    sentence_count:      sents.length,
    char_count:          text.length,
    unique_words:        new Set(tokens).size,
    avg_sentence_length: sents.length
      ? Math.round(sents.reduce((s, ss) => s + ss.split(/\s+/).length, 0) / sents.length * 10) / 10
      : 0,
  };

  return { pre_score, feature_display, text_stats };
}


// ── FULL LOCAL ANALYSIS ───────────────────────────────────────────────────────

export function analyzeLocally(text: string) {
  const t0 = performance.now();
  if (!text.trim()) return null;

  // Layer 1: Statistical
  const stats = computeStatisticalScore(text);
  const preScore = stats.pre_score;

  // Layer 3: Pattern matching
  const dbPhrases = matchPatterns(text);

  // Pattern-based score: each HIGH=25pts, MED=12pts, LOW=5pts — capped at 80
  const patternScore = Math.min(
    dbPhrases.reduce((s, p) => s + (SEV_SCORE[p.severity] || 5), 0),
    80
  );

  // Injection bonus: if ANY prompt injection patterns found → +40 to manipulation score
  const hasInjection = dbPhrases.some(p => p.category === 'prompt_injection');
  const injectionBonus = hasInjection ? 40 : 0;

  // Derive manipulation score: blend of stat + pattern + injection bonus
  const manipScore = Math.min(
    Math.round(preScore * 0.30 + patternScore * 0.50 + injectionBonus),
    100
  );

  // AI probability: emphasize pattern + stat
  const aiProb = Math.min(
    Math.round(preScore * 0.40 + patternScore * 0.40 + injectionBonus * 0.5),
    100
  );

  // Determine primary technique
  const catCounts: Record<string, number> = {};
  dbPhrases.forEach(p => { catCounts[p.category] = (catCounts[p.category] || 0) + SEV_SCORE[p.severity]; });

  const topCat = Object.entries(catCounts).sort((a, b) => b[1] - a[1])[0]?.[0];

  const TECHNIQUE_NAMES: Record<string, string> = {
    prompt_injection:    "AI Prompt Injection / Jailbreak Attack",
    ai_structural:       "AI-Generated Text (Structural Markers)",
    fear_trigger:        "Fear Mongering",
    emotional_amplifier: "Emotional Manipulation",
    us_vs_them:          "Tribal Framing / Division",
    false_urgency:       "False Urgency Tactics",
    fake_authority:      "Fake Authority Appeal",
    conspiracy_frame:    "Conspiracy Framing",
    coordinated_marker:  "Coordinated Campaign",
  };
  const technique = topCat ? (TECHNIQUE_NAMES[topCat] || topCat) : "None Detected";

  // Verdict thresholds
  let verdict = "LOW_RISK";
  let verdictSub = "Factual content, low manipulation signals";
  const combined = manipScore * 0.6 + aiProb * 0.4;
  if (hasInjection || combined >= 60) {
    verdict = "HIGH_RISK";
    verdictSub = hasInjection
      ? "AI prompt injection attack detected"
      : "Multiple manipulation techniques detected";
  } else if (combined >= 30) {
    verdict = "MEDIUM_RISK";
    verdictSub = "Subtle manipulation signals detected";
  }

  // Confidence
  const confidence = dbPhrases.length >= 5 || hasInjection
    ? "high"
    : dbPhrases.length >= 2
      ? "medium"
      : "low";

  // Summary
  let summary = `Local analysis (browser engine). Pattern score: ${patternScore}/80. Statistical pre-score: ${preScore}/100. `;
  if (hasInjection) {
    summary += `⚠ CRITICAL: Prompt injection markers detected (e.g., "ignore previous instructions", "system override"). This is a known AI adversarial technique. `;
  }
  if (dbPhrases.length > 0) {
    const cats = [...new Set(dbPhrases.map(p => p.catLabel))].slice(0, 3).join(", ");
    summary += `Found ${dbPhrases.length} manipulation marker(s): ${cats}. `;
  }
  summary += verdict === "HIGH_RISK"
    ? "High-confidence manipulation detected — content likely adversarial or AI-generated."
    : verdict === "MEDIUM_RISK"
      ? "Moderate signals — manual review recommended."
      : "Content appears predominantly factual.";

  const allPhrases = dbPhrases.sort((a, b) => a.char_start - b.char_start);
  const procMs = Math.round(performance.now() - t0);

  // Simple hash
  let hash = 0;
  for (let i = 0; i < text.length; i++) { hash = ((hash << 5) - hash) + text.charCodeAt(i); hash |= 0; }
  const textHash = Math.abs(hash).toString(16).toUpperCase().slice(0, 8);

  return {
    ai_probability:     aiProb,
    manipulation_score: manipScore,
    stat_score:         preScore,
    confidence,
    verdict,
    verdict_sub:        verdictSub,
    technique,
    summary,
    phrases:            allPhrases,
    explain:            stats.feature_display,
    layers: {
      l1: Math.round(preScore),
      l2: manipScore,
      l3: Math.min(patternScore, 100),
    },
    scan_id:    "SCN-" + String(Math.floor(Math.random() * 10000)).padStart(4, "0"),
    text_hash:  textHash,
    proc_time:  `${procMs}ms`,
    text_stats: stats.text_stats,
    model_used: "local_engine",
  };
}
