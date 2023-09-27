from fastapi import FastAPI
from pydantic import BaseModel
from classsync.db import Student, Teacher, Timer, Schedule, Class, engine
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()

# Post section for students, teachers, timers

@app.post("/add_student")
async def add_student(name: str, face_id: int, class_id: float, date:str, attendance: bool = False):
    with Session(engine) as session:
        student = Student(name, attendance, face_id, class_id, date)
        session.add(student)
        session.commit()
        return {"Student succesfully added" : student.name}

@app.post("/add_teacher")
async def add_teacher(name: str, class_id: int, username: str, password: str):
    with Session(engine) as session:
        teacher = Teacher(name, class_id, username, password)
        session.add(teacher)
        session.commit()
        return {"Teacher succesfully added" : teacher.name}

@app.post("/add_schedule")
async def add_schedule(school_name: str, schedule_id: int, periods: int):
    with Session(engine) as session:
        schedule = Schedule(school_name, schedule_id, periods)
        session.add(schedule)
        session.commit()
        return {"Schedule succesfully added" : schedule.schedule_id}
    
@app.post("/add_class")
async def add_class(class_id: int, schedule_id: int, duration: int, periods: str):
    with Session(engine) as session:
        class_ = Class(class_id, schedule_id, duration, periods)
        session.add(class_)
        session.commit()
        return {"Class succesfullly added" : class_.class_id}
    
@app.post("/add_timer")
async def add_timer(name: str, timing: int, alarm_sound_id: str):
    with Session(engine) as session:
        timer = Timer(name, timing, alarm_sound_id)
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
    
@app.get("/get_schedule")
async def get_schedule():
    with Session(engine) as session:
        schedule_query = session.query(Schedule)
        return schedule_query.all()

@app.get("/get_class")
async def get_class():
    with Session(engine) as session:
        class_query = session.query(Class)
        return class_query.all()
    
@app.get("/get_timer")
async def get_timer():
    with Session(engine) as session:
        timer_query = session.query(Timer)
        return timer_query.all()

# Update section for timers & students

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)

