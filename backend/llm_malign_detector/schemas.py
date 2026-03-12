from pydantic import BaseModel


class ResultCreate(BaseModel):
    input_text: str
    pre_score: float
    flagged_count: int
    final_verdict: str


class FlagCreate(BaseModel):
    result_id: int
    pattern_id: int
    phrase_text: str
    severity: int
    reason: str