from typing import List, Optional
from sqlalchemy import create_engine, ForeignKey, Table, Column
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pgvector.sqlalchemy import Vector

engine = create_engine('postgresql+psycopg2://postgres:esheldror1234@209.141.60.99:1678/eshel', echo=True)
with Session(engine) as session:
    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
Base = declarative_base()


association_table = Table("association_table",
                          Base.metadata,
                          Column("periodclass_id", ForeignKey("periodclasses.id"), primary_key=True),
                          Column("student_id", ForeignKey("students.id"), primary_key=True))

### Next classes are user info in the database

class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()
    periodclasses: Mapped[Optional[List["PeriodClass"]]] = relationship(back_populates="teacher")
    periodclasses: Mapped[Optional[List[int]]] = mapped_column(foreign_keys="periodclasses.id")
    timers: Mapped[Optional[List["Timer"]]] = relationship()

class PeriodClass(Base):
    __tablename__ = "periodclasses"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    name: Mapped[str] = mapped_column()
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    teacher: Mapped["Teacher"] = relationship(back_populates="periodclasses")
    students: Mapped[Optional[List["Student"]]] = relationship(secondary=association_table, back_populates="periodclasses")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)

    periodclasses: Mapped[List["PeriodClass"]] = relationship(secondary=association_table, back_populates="students")
    name: Mapped[str] = mapped_column()
    face_embedding = mapped_column(Vector(384))

class AttendanceEvent(Base):
    __tablename__ = "attendance_events"
    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    student: Mapped["Student"] = relationship()
    time: Mapped[str] = mapped_column() # TODO: Make datetime
    inputType: Mapped[str] = mapped_column()


class Timer(Base):
    __tablename__ = "timers"

    id: Mapped[int] = mapped_column(primary_key=True)

    timing: Mapped[int] = mapped_column()
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))


Base.metadata.create_all(engine)
