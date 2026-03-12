from database import SessionLocal, Base, engine
from models import MalignPattern

Base.metadata.create_all(bind=engine)

db = SessionLocal()

patterns = [

("they don't want you to know","conspiracy_frame","HIGH","hidden_truth","Creates illusion of suppressed information"),
("share this before it's deleted","false_urgency","HIGH","urgency","Forces rapid sharing"),
("the elites","us_vs_them","MED","division","Creates group polarization"),
("wake up people","emotional_amplifier","LOW","emotion","Emotional activation"),
("mainstream media won't show","fake_authority","HIGH","authority_attack","Discredits media"),
]

for p in patterns:

    db.add(MalignPattern(
        pattern_text=p[0],
        category=p[1],
        severity=p[2],
        narrative_technique=p[3],
        description=p[4],
        is_regex=0,
        source="manual"
    ))

db.commit()
db.close()

print("Patterns inserted")