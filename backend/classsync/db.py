from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, mapped_column
from pgvector.sqlalchemy import Vector
engine = create_engine('sqlite:///student_data.db', echo=True)
Base = declarative_base()

### Next classes are user info in the database

# Student Class takes name, attendance, & class_id parameters

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    face_embedding = Column(Vector(384))

    def __init__(self, name, face_id):
        self.name = name
        self.face_id = face_id

class Timer(Base):
    __tablename__ = "timers"

    id = Column(Integer, primary_key=True)

    timing = Column(Integer)
    alarm_sound_id = Column(String)

    def __init__(self, timing, alarm_sound_id):
        self.timing = timing
        self.alarm_sound_id = alarm_sound_id
class Writing(Base):
    __tablename__ = "writings"

    id = Column(Integer, primary_key=True)

    writing = Column(String)

    def __init__(self, writing):
        self.writing = writing

Base.metadata.create_all(engine)
