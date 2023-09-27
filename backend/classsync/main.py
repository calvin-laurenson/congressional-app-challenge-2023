from fastapi import FastAPI
from pydantic import BaseModel
from classsync.db import Student, Teacher, Timer, engine
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()

# Post section for students, teachers, timers

@app.post("/add_student")
async def add_student(name: str, face_id: int, class_id: float, date:str, attendance: bool = False):
    with Session(engine) as session:
        student = Student(name = name, attendance = attendance, face_id = face_id, class_id = class_id, date = date)
        session.add(student)
        session.commit()
        return {"Student succesfully added": student.name}

@app.post("/add_teacher")
async def add_teacher(name: str, class_id: int):
    with Session(engine) as session:
        teacher = Teacher(name = name, class_id = class_id)
        session.add(teacher)
        session.commit()
        return {"Teacher succesfully added": teacher.name}
    
@app.post("/add_timer")
async def add_timer(name: str, timing: int, alarm_sound_id: str):
    with Session(engine) as session:
        timer = Timer(name = name, timing = timing, alarm_sound_id = alarm_sound_id)
        session.add(timer)
        session.commit()
        return {"Timer succesfully added" : timer.name}
    
# Get section for students, teachers, timers

@app.get("/get_student")
async def get_student():
    with Session(engine) as session:
        student_query = session.query(Student)
        return student_query.all()

@app.get("/get_teacher")
async def get_teacher():
    with Session(engine) as session:
        teacher_query = session.query(Teacher)
        return teacher_query.all()
    
@app.get("/get_timer")
async def get_teacher():
    with Session(engine) as session:
        timer_query = session.query(Timer)
        return timer_query.all()

# Update section for timers & students

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)

