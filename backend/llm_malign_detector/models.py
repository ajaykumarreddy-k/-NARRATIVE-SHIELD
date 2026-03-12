from sqlalchemy import Column, Integer, String, Text, Float
from database import Base


class MalignPattern(Base):
    __tablename__ = "malign_patterns"

    id = Column(Integer, primary_key=True, index=True)
    pattern_text = Column(Text, nullable=False)
    category = Column(String)
    severity = Column(String)
    narrative_technique = Column(String)
    description = Column(Text)
    is_regex = Column(Integer)
    source = Column(String)
    created_at = Column(String)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text)
    text_hash = Column(String)
    pre_score = Column(Float)
    ai_probability = Column(Float)
    manipulation_score = Column(Float)
    final_verdict = Column(String)
    narrative_technique = Column(String)
    confidence = Column(String)
    flagged_count = Column(Integer)
    gemini_summary = Column(Text)
    created_at = Column(String)


class FlaggedPhrase(Base):
    __tablename__ = "flagged_phrases"

    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer)
    pattern_id = Column(Integer)
    phrase_text = Column(Text)
    char_start = Column(Integer)
    char_end = Column(Integer)
    reason = Column(Text)
    severity = Column(String)
    source = Column(String)