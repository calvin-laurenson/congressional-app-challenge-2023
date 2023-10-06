
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete
from classsync.db import Student, Timer, engine
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
async def add_timer(timing):
    with Session(engine) as session:
        timer = Timer(timing)
        session.add(timer)
        session.commit()
        return {"Timer succesfully added": timer.name}
    
# Post for image transfer from camera
@app.post("/add_image")
async def add_image(image, time):
    student = ()

# Get section for students, plagiarism, timers

@app.get("/get_plagiarized")
async def get_plagiarized(writing1 : str, writing2 : str):
    return float(cosine_similarity(model.encode(writing1), model.encode(writing2)))

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

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
