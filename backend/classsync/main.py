from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from classsync.db import Student, Timer, engine, AttendanceEvent, Teacher, PeriodClass, association_table
from classsync.plagiarism_detector import model, cosine_similarity
from classsync.models import Models
from sqlalchemy.orm import Session
import uvicorn

app = FastAPI()
model = Models()

# Post section for students, teachers, timers
@app.post("/add_teacher")
async def add_teacher(name):
    with Session(engine) as session:
        teacher = Teacher(name=name)
        session.add(teacher)
        session.commit()
        return {"Teacher succesfully added": teacher.name}

@app.post("/add_class")
async def add_periodclass(name, teacher_name, students=None):
    with Session(engine) as session:
        teacher = session.query(Teacher).filter(Teacher.name == teacher_name).all()
        if len(teacher) != 1:
            return {"error": f"teacher not found for periodclass {teacher}"}
        if students is None:
            periodclass = PeriodClass(name=name, teacher=teacher[0])
        else:
            periodclass = PeriodClass(name=name, teacher=teacher[0], students=students)
        session.add(periodclass)
        session.commit()
        return {"succesfully added": periodclass.name}


@app.post("/add_student")
async def add_student(name):
    with Session(engine) as session:
        student = Student(name=name)
        session.add(student)
        session.commit()
        return {"Student succesfully added": student.name}


@app.post("/add_timer")
async def add_timer(timing, teacher_id):
    with Session(engine) as session:
        timer = Timer(timing=timing, teacher_id=teacher_id)
        session.add(timer)
        session.commit()
        return {"Timer succesfully added": timer.name}

# Post for image transfer from camera
@app.post("/add_image")
async def add_image(image, time):
    faces = model.findFaces(image)
    with Session(engine) as session:
        for face in faces:
            student = session.scalars(select(Student).order_by(Student.face_embedding.cosine_distance(face)).limit(5))
            entry = AttendanceEvent(student=student, time=time, inputType="image")
            session.add(entry)
        session.commit()
        return {"Recognized faces": len(faces)}
    
@app.get("/get_attendance")
async def get_attendance():
    with Session(engine) as session:
        attendance_query = session.query(AttendanceEvent)
        return attendance_query.all()

@app.patch("/add_student_to_class")
async def add_student_to_class(student_id: int, class_id: int):
    with Session(engine) as session:
        student_query = session.query(Student).filter(Student.id == student_id)
        if len(student_query.all()) != 1:
            return {"error": f"student not found for {student_id=}"}
        
        session.execute(association_table.insert().values(student_id=student_id, periodclass_id=class_id))
        session.commit()
        return {"error": None}

# Get section for students, plagiarism, timers

@app.get("/get_plagiarized")
async def get_plagiarized(writing1: str, writing2: str):
    return float(cosine_similarity(model.encode(writing1), model.encode(writing2)))

@app.get("/get_classes")
async def get_periodclasses():
    with Session(engine) as session:
        periodclass_query = session.query(PeriodClass)
        return periodclass_query.all()

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

@app.get("/get_teachers")
async def get_teachers():
    with Session(engine) as session:
        teacher_query = session.query(Teacher)
        return teacher_query.all()

@app.get("/get_students_in_class")
async def get_students_in_class(class_id: int):
    with Session(engine) as session:
        periodclass_query = session.query(PeriodClass).filter(PeriodClass.id == class_id)
        if len(periodclass_query.all()) != 1:
            return {"error": f"periodclass not found for {class_id=}"}
        return periodclass_query[0].students

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
