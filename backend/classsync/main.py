import time
from fastapi import FastAPI, File, Request
from classsync.db import (
    Student,
    Timer,
    engine,
    AttendanceEvent,
    Teacher,
    PeriodClass,
    association_table,
)
from classsync.plagiarism_detector import model as sbert, cosine_similarity
from classsync.models import Models
from sqlalchemy.orm import Session
import uvicorn
from typing import Annotated
from PIL import Image
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import numpy as np


app = FastAPI()
model = Models()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

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
async def add_image(image_file: Annotated[bytes, File()], time: int, tardy: bool):
    image = Image.open(BytesIO(image_file))
    faces = model.find_faces(image)
    not_found = 0
    with Session(engine) as session:
        for face in faces:
            students = (
                session.query(Student)
                .order_by(Student.face_embedding.cosine_distance(face).desc())
                .all()
            )
            if len(students) >= 3:
                similarities = [cosine_similarity(students[i].face_embedding,np.asarray(face)) for i in range(3)]
                if (students is None) or (similarities[0]-similarities[1]) > 1.5*(similarities[1]-similarities[2]):
                    not_found += 1
                    continue
            entry = AttendanceEvent(
                student=students[0], time=time, inputType="image", tardy=tardy
            )
            session.add(entry)
        session.commit()
        return {"error": None, "face_count": len(faces), "not_found": not_found}


@app.post("/add_attendance")
async def add_attendance(student_id: int, time: int, tardy: bool):
    with Session(engine) as session:
        student_query = session.query(Student).filter(Student.id == student_id)
        if len(student_query.all()) != 1:
            return {"error": f"student not found for {student_id=}"}
        student = student_query[0]
        entry = AttendanceEvent(
            student=student, time=time, inputType="manual", tardy=tardy
        )
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


# Delete


@app.delete("/clear_db")
async def clear_db():
    with Session(engine) as session:
        session.expunge_all()
        session.commit()


# Get


@app.get("/get_plagiarized")
async def get_plagiarized(writing1: str, writing2: str):
    return {
        "error": None,
        "similarity": float(
            cosine_similarity(sbert.encode(writing1), sbert.encode(writing2))
        ),
    }


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


@app.get("/get_classes")
async def get_periodclasses():
    with Session(engine) as session:
        periodclass_query = session.query(PeriodClass)
        return periodclass_query.all()


@app.get("/get_students")
async def get_student():
    with Session(engine) as session:
        student_query = session.query(Student)
        students = student_query.all()
        for s in students:
            if s.face_embedding:
                s.face_embedding = True
        return students


@app.get("/get_attendance")
async def get_attendance():
    with Session(engine) as session:
        attendance_query = session.query(AttendanceEvent)
        return attendance_query.all()


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
        student_names = [s.name for s in students]
        return student_names


@app.get("/get_student_attendance")
async def get_student_attendance(student_id: int):
    with Session(engine) as session:
        attendance_query = session.query(AttendanceEvent)
        attendance_events = (
            attendance_query.filter(AttendanceEvent.student_id == student_id)
            .order_by(AttendanceEvent.time)
            .all()
        )
        return attendance_events


@app.get("/get_class_attendance")
async def get_class_attendance(class_id: int, start_time: int):
    with Session(engine) as session:
        class_query = session.query(PeriodClass)
        periodclass = class_query.filter(PeriodClass.id == class_id).all()
        if len(periodclass) != 1:
            return {"error": f"couldn't find {class_id=}"}
        students = periodclass[0].students
        student_attendance: dict[int, str] = dict()
        attendance_query = (
            session.query(AttendanceEvent)
            .filter(AttendanceEvent.time >= start_time)
            .order_by(AttendanceEvent.time)
        )
        for student in students:
            attendance = attendance_query.filter(
                AttendanceEvent.student_id == student.id
            ).first()
            if attendance == None:
                student_attendance[student.name] = "absent"
            elif attendance.tardy:
                student_attendance[student.name] = "tardy"
            else:
                student_attendance[student.name] = "present"
        return student_attendance


@app.get("/get_student_id_by_name")
async def get_student_id_by_name(student_name: str):
    with Session(engine) as session:
        student_query = session.query(Student)
        student = student_query.filter(Student.name == student_name).all()
        if len(student) != 1:
            return {"error": f"didn't find one {student_name=}"}
        return {"error": None, "id": student[0].id}


@app.get("/get_student_name_by_id")
async def get_student_name_by_id(student_id: int):
    with Session(engine) as session:
        student_query = session.query(Student)
        student = student_query.filter(Student.id == student_id).all()
        if len(student) != 1:
            return {"error": f"didn't find one {student_id=}"}
        return {"error": None, "id": student[0].name}


@app.get("/get_class_id_by_name")
async def get_class_name_by_id(class_name: str):
    with Session(engine) as session:
        class_query = session.query(PeriodClass)
        periodclasses = class_query.filter(PeriodClass.name == class_name).all()
        if len(periodclasses) != 1:
            return {"error": f"didn't find one {class_name=}"}
        return {"error": None, "id": periodclasses[0].name}


@app.get("/get_class_names_by_teacher_id")
async def get_class_names_by_teacher_id(teacher_id: int):
    with Session(engine) as session:
        class_query = session.query(PeriodClass)
        periodclasses = class_query.filter(PeriodClass.teacher_id == teacher_id).all()
        return {"error": None, "periodclasses": [c.name for c in periodclasses]}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000)
