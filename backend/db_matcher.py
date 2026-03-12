"""
NarrativeShield — Layer 3: Database Pattern Matcher
=====================================================
Matches input text against known malign patterns stored in SQLite.
Auto-seeds the database if the table is empty or missing.
"""

import sqlite3
import os

# Base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "llm_malign_detector", "narrative_shield.db")

# ── Seed patterns (used if DB is empty or table missing) ──────────────────────
SEED_PATTERNS = [
    ("they don't want you to know",    "conspiracy_frame",    "HIGH", "Creates illusion of suppressed information"),
    ("share this before it's deleted", "false_urgency",       "HIGH", "Forces rapid sharing through artificial scarcity"),
    ("the elites",                     "us_vs_them",          "MED",  "Creates group polarization and division"),
    ("wake up people",                 "emotional_amplifier", "LOW",  "Emotional activation technique"),
    ("mainstream media won't show",    "fake_authority",      "HIGH", "Discredits legitimate media sources"),
    ("shocking truth",                 "emotional_amplifier", "HIGH", "Emotional clickbait trigger"),
    ("deep state",                     "us_vs_them",          "HIGH", "Conspiracy-driven tribal framing"),
    ("time is running out",            "false_urgency",       "HIGH", "Creates artificial time pressure"),
    ("experts agree",                  "fake_authority",      "MED",  "Vague appeal to unnamed authority"),
    ("share immediately",              "false_urgency",       "HIGH", "Pressures for viral sharing"),
    ("our people",                     "us_vs_them",          "HIGH", "In-group tribal identity marker"),
    ("real citizens",                  "us_vs_them",          "HIGH", "Exclusionary identity framing"),
    ("before it's deleted",            "false_urgency",       "HIGH", "Censorship fear tactic"),
    ("globalists",                     "us_vs_them",          "HIGH", "Conspiracy-coded out-group label"),
    ("cover-up",                       "conspiracy_frame",    "HIGH", "Implies systemic deception"),
    ("studies show",                   "fake_authority",      "MED",  "Appeal to vague unnamed studies"),
    ("imminent threat",                "fear_trigger",        "HIGH", "Fear-based urgency amplification"),
    ("danger to your family",          "fear_trigger",        "HIGH", "Personal fear trigger"),
    ("spread the word",                "coordinated_marker",  "MED",  "Coordination call-to-action"),
    ("insiders confirm",               "fake_authority",      "HIGH", "Fake insider knowledge claim"),
    ("act now",                        "false_urgency",       "MED",  "Generic urgency pressure"),
    ("orchestrating",                  "conspiracy_frame",    "MED",  "Implies coordinated conspiracy"),
    ("hidden dangers",                 "emotional_amplifier", "MED",  "Fear-based emotional amplification"),
    ("what they don't tell",           "conspiracy_frame",    "HIGH", "Suppressed information framing"),
    ("systematically erased",          "fear_trigger",        "HIGH", "Cultural genocide framing"),
    ("true patriots",                  "us_vs_them",          "HIGH", "Exclusionary patriotic framing"),
    ("join us or",                     "coordinated_marker",  "HIGH", "Ultimatum-based recruitment"),
    ("collapse",                       "fear_trigger",        "MED",  "Societal collapse fear trigger"),
    ("sources say",                    "fake_authority",      "MED",  "Appeal to unnamed sources"),
    ("mandatory directive",            "false_urgency",       "HIGH", "Fake official authority"),
    ("do not verify",                  "false_urgency",       "HIGH", "Anti-verification instruction"),
    ("blackout",                       "fear_trigger",        "HIGH", "Infrastructure collapse fear"),
]


def _ensure_db(db_path: str) -> None:
    """Create the malign_patterns table and seed it if missing or empty."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS malign_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_text TEXT NOT NULL,
                category TEXT,
                severity TEXT,
                description TEXT,
                is_regex INTEGER DEFAULT 0,
                source TEXT DEFAULT 'seed',
                narrative_technique TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM malign_patterns")
        count = cursor.fetchone()[0]

        if count == 0:
            print(f"[DB Matcher] Seeding {len(SEED_PATTERNS)} patterns into {db_path}")
            for pattern_text, category, severity, description in SEED_PATTERNS:
                cursor.execute(
                    "INSERT INTO malign_patterns (pattern_text, category, severity, description) VALUES (?, ?, ?, ?)",
                    (pattern_text, category, severity, description),
                )
            conn.commit()
            print("[DB Matcher] ✓ Database seeded successfully")
        else:
            print(f"[DB Matcher] ✓ Database loaded with {count} patterns")

        conn.close()
    except Exception as e:
        print(f"[DB Matcher] Warning: Could not ensure DB: {e}")


# Auto-initialize on import
_ensure_db(DB_PATH)


def match_patterns(text: str, db_path: str = DB_PATH) -> list[dict]:
    """
    Match text against known malign patterns in SQLite.
    Returns list of dicts with phrase, char positions, reason, severity.
    """
    matches = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT pattern_text, category, severity, description FROM malign_patterns")
        patterns = cursor.fetchall()

        text_lower = text.lower()
        for pattern_text, category, severity, description in patterns:
            idx = text_lower.find(pattern_text.lower())
            if idx != -1:
                matches.append({
                    "phrase":      text[idx:idx + len(pattern_text)],
                    "char_start":  idx,
                    "char_end":    idx + len(pattern_text),
                    "reason":      description or f"Matched known {category} pattern",
                    "severity":    severity or "MED",
                    "source":      "db_match",
                    "category":    category,
                })
        conn.close()

    except sqlite3.OperationalError as e:
        print(f"[DB Matcher] Warning: Database error: {e}. Skipping Layer 3 DB match.")
    except Exception as e:
        print(f"[DB Matcher] Warning: Unexpected error: {e}. Skipping Layer 3 DB match.")

    return matches
