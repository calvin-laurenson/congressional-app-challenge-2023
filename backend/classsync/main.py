from fastapi import FastAPI
from pydantic import BaseModel
from classsync.db import Student, Teacher, engine
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()


@app.post("/add_student")
async def add_student(name: str, class_id: int, attendance: bool = False):
    with Session(engine) as session:
        student = Student(name=name, attendance=attendance, class_id = class_id)
        session.add(student)
        session.commit()
        return {"Student added": student.name}

@app.post("/add_teacher")
async def add_teacher(name: str, class_id: int):
    with Session(engine) as session:
        teacher = Teacher(name=name, class_id=class_id)
        session.add(teacher)
        session.commit()
        return {"Teacher added": teacher.name}

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

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)