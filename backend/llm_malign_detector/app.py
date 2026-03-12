from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import AnalysisResult, FlaggedPhrase, MalignPattern
from schemas import ResultCreate, FlagCreate

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "NarrativeShield Backend Running"}


# Get all patterns (parser will use this)
@app.get("/patterns")
def get_patterns(db: Session = Depends(get_db)):
    return db.query(MalignPattern).all()


# Save analysis result from parser/LLM
@app.post("/save_result")
def save_result(result: ResultCreate, db: Session = Depends(get_db)):

    new_result = AnalysisResult(**result.dict())

    db.add(new_result)
    db.commit()
    db.refresh(new_result)

    return {"result_id": new_result.id}


# Save each flagged phrase
@app.post("/save_flag")
def save_flag(flag: FlagCreate, db: Session = Depends(get_db)):

    new_flag = FlaggedPhrase(**flag.dict())

    db.add(new_flag)
    db.commit()

    return {"status": "flag stored"}


# View scan history
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    return db.query(AnalysisResult).all()