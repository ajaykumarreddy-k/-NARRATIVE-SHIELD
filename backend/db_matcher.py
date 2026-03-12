import sqlite3
import os

# Base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "llm_malign_detector", "narrative_shield.db")

def match_patterns(text: str, db_path=DB_PATH):
    matches = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Grab the patterns you seeded
        cursor.execute("SELECT pattern_text, category, severity, description FROM malign_patterns")
        patterns = cursor.fetchall()
        
        text_lower = text.lower()
        for pattern_text, category, severity, description in patterns:
            # Simple, fast substring match for the 5-hour sprint
            idx = text_lower.find(pattern_text.lower())
            if idx != -1:
                matches.append({
                    "phrase": text[idx:idx+len(pattern_text)],
                    "char_start": idx,
                    "char_end": idx + len(pattern_text),
                    "reason": description or f"Matched known {category} pattern",
                    "severity": severity,
                    "source": "db_match"
                })
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Warning: Database error: {e}. Skipping Layer 3 DB match.")
    return matches
