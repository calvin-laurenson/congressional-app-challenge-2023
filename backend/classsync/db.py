from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///app_data.db', echo=True)
Base = declarative_base()

### Next classes are user info in the database

# Student Class takes name, attendance, & class_id parameters

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    face_id = Column(Integer)
    class_id = Column(Float)
    attendance = Column(Boolean)
    date = Column(String)

    def __init__(self, name, attendance, face_id, class_id, date):
        self.name = name
        self.face_id = face_id
        self.attendance = attendance
        self.class_id = class_id
        self.date = date

# Teacher Class takes name & class_id parameters

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    class_id = Column(String)

    def __init__(self, name, class_id):
        self.name = name
        self.class_id = class_id

### Next classes are user-configured timers

# Timer class takes name, timing, and alarm sound id

class Timer(Base):
    __tablename__ = "timers"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    timing = Column(Integer)
    alarm_sound_id = Column(String)

    def __init__(self, name, timing, alarm_sound_id):
        self.name = name
        self.timing = timing
        self.alarm_sound_id = alarm_sound_id

Base.metadata.create_all(engine)
