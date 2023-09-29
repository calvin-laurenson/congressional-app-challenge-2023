from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete
from classsync.db import Student, Timer, Writing, engine
from classsync.plagiarism_detector import model, cosine_similarity
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()

# Post section for students, teachers, timers

@app.post("/add_student")
async def add_student(name, face_embedding):
    with Session(engine) as session:
        student = Student(name, face_embedding)
        session.add(student)
        session.commit()
        return {"Student succesfully added": student.name}

@app.post("/add_timer")
async def add_timer(timing, alarm_sound_id):
    with Session(engine) as session:
        timer = Timer(timing, alarm_sound_id)
        session.add(timer)
        session.commit()
        return {"Timer succesfully added": timer.name}
    
@app.post("/add_writing")
async def add_writing(words):
    with Session(engine) as session:
        query = session.query(Writing)
        if len(query.all()) >= 2:
            return {"Too many writings": "Remove one to add a different one"}
        else:
            writing = Writing(words)
            session.add(writing)
            session.commit()
            return {"Writing succesfully added": writing.writing}
    
# Get section for students, teachers, timers

@app.get("/get_students")
async def get_student():
    with Session(engine) as session:
        student_query = session.query(Student)
        return student_query.all()
    
@app.get("/get_timers")
async def get_timer():
    with Session(engine) as session:
        timer_query = session.query(Timer)
        return timer_query.all()

@app.get("/get_writings")
async def get_writings():
    with Session(engine) as session:
        writing_query = session.query(Writing)
        return writing_query.all()
    
@app.get("/get_plagiarized")
async def get_plagiarized():
    with Session(engine) as session:
        writing_query = session.query(Writing)

        writing = []
        for i in range(len(writing_query.all())):
            writing.append(writing_query.all()[i].writing)

        return int(round(cosine_similarity(model.encode(writing[0]), model.encode(writing[1])), 2)*100)

#

@app.patch("/remove_writings")
def remove_writings():
    with Session(engine) as session:
        deletion = delete(Writing)
        session.execute(deletion)
        session.commit()
        return 'Sentences succesfully removed'

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)

