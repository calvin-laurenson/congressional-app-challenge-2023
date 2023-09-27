from classsync.db import Student, engine
from sqlalchemy.orm import Session
import json

with Session(engine) as session:
    print(session.query(Student))