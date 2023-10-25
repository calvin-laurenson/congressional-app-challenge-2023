from fastapi import FastAPI, HTTPException, File
from pydantic import BaseModel
from sqlalchemy import delete, select
from classsync.db import (
    Student,
    Timer,
    engine,
    AttendanceEvent,
    Teacher,
    PeriodClass,
    association_table,
)
from classsync.plagiarism_detector import model, cosine_similarity
from classsync.models import Models
from sqlalchemy.orm import Session
import uvicorn
from typing import Annotated
from PIL import Image
from io import BytesIO

print("Initiating API")
app = FastAPI()
print("Initiating Models")
model = Models()


# Posts
@app.post("/add_teacher")
async def add_teacher(name: str):
    with Session(engine) as session:
        teacher = Teacher(name=name)
        session.add(teacher)
        session.commit()
        return {"error": None}


@app.post("/add_class")
async def add_periodclass(name: str, teacher_name: str):
    with Session(engine) as session:
        teacher = session.query(Teacher).filter(Teacher.name == teacher_name).all()
        if len(teacher) != 1:
            return {"error": f"teacher not found for periodclass {teacher}"}
        periodclass = PeriodClass(name=name, teacher=teacher[0])
        session.add(periodclass)
        session.commit()
        return {"error": None}


@app.post("/add_student")
async def add_student(name: str):
    with Session(engine) as session:
        student = Student(name=name)
        session.add(student)
        session.commit()
        return {"error": None}


@app.post("/add_timer")
async def add_timer(timing: int, teacher_id: int):
    with Session(engine) as session:
        timer = Timer(timing=timing, teacher_id=teacher_id)
        session.add(timer)
        session.commit()
        return {"error": None}


# Post for image transfer from camera
@app.post("/add_image")
async def add_image(image_file: Annotated[bytes, File()], time: str):
    image = Image.open(BytesIO(image_file))
    faces = model.find_faces(image)
    with Session(engine) as session:
        for face in faces:
            student = session.query(Student).order_by(Student.face_embedding.cosine_distance(face)).first()
            entry = AttendanceEvent(student=student, time=time, inputType="image")
            session.add(entry)
        session.commit()
        return {"error": None, "face count": len(faces)}

@app.post("/add_attendance")
async def add_attendance(student_id, time):
    with Session(engine) as session:
        student_query = session.query(Student).filter(Student.id == student_id)
        if len(student_query.all()) != 1:
            return {"error": f"student not found for {student_id=}"}
        student = student_query[0]
        entry = AttendanceEvent(student=student, time=time, inputType = "manual")
        session.add(entry)
        session.commit()
        return {"error": None}

# Patches

@app.patch("/add_student_to_class")
async def add_student_to_class(student_id: int, class_id: int):
    with Session(engine) as session:
        student_query = session.query(Student).filter(Student.id == student_id)
        if len(student_query.all()) != 1:
            return {"error": f"student not found for {student_id=}"}

        session.execute(
            association_table.insert().values(
                student_id=student_id, periodclass_id=class_id
            )
        )
        session.commit()
        return {"error": None}

@app.patch("/add_face_to_student")
async def add_student_to_class(face_img: Annotated[bytes, File()], student_id: int):
    image = Image.open(BytesIO(face_img))
    faces = model.find_faces(image)
    if len(faces) > 1:
        return {"error": f"found too many faces in img"}
    if len(faces) == 0:
        return {"error": f"could not find face in img"}
    with Session(engine) as session:
        student_query = session.query(Student).filter(Student.id == student_id)
        if len(student_query.all()) != 1:
            return {"error": f"student not found for {student_id=}"}
        student: Student = student_query[0]
        student.face_embedding = faces[0]
        session.add(student)
        session.commit()
        session.refresh(student)
        return {"error": None}

# Get section for students, plagiarism, timers


@app.get("/get_plagiarized")
async def get_plagiarized(writing1: str, writing2: str):
    return float(cosine_similarity(model.encode(writing1), model.encode(writing2)))

@app.get("/get_attendance")
async def get_attendance():
    with Session(engine) as session:
        attendance_query = session.query(AttendanceEvent)
        return attendance_query.all()

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
        periodclass_query = session.query(PeriodClass).filter(
            PeriodClass.id == class_id
        )
        if len(periodclass_query.all()) != 1:
            return {"error": f"periodclass not found for {class_id=}"}
        print("debug: returning students")
        students = periodclass_query.all()[0].students
        student_ids = [s.id for s in students]
        return student_ids

        


@app.get("/get_student_attendance")
async def get_student_attendance(student_id: int):
    with Session(engine) as session:
        attendance_query = session.query(AttendanceEvent)
        attendance_events = attendance_query.filter(AttendanceEvent.student_id==student_id).order_by(AttendanceEvent.time).all()
        return attendance_events



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
