from typing import List
from sqlalchemy import create_engine, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

engine = create_engine('sqlite:///student_data.db', echo=True)
Base = declarative_base()

### Next classes are user info in the database


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    periodclasses: Mapped[List["PeriodClass"]] = relationship()
    timers: Mapped[List["Timer"]] = relationship()

class PeriodClass(Base):
    __tablename__ = "periodclasses"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column()
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    students: Mapped[List["Student"]] = relationship()

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    face_embedding: Mapped[Vector(384)] = mapped_column()

class AttendanceEvent(Base):
    __tablename__ = "attendance_events"
    id: Mapped[int] = mapped_column(primary_key=True)

    student: Mapped["Student"] = relationship()
    time: Mapped[DateTime] = mapped_column()
    type: Mapped[str] = mapped_column()

class Timer(Base):
    __tablename__ = "timers"

    id: Mapped[int] = mapped_column(primary_key=True)

    timing: Mapped[int] = mapped_column()

Base.metadata.create_all(engine)
