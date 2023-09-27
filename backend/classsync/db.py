from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///data.db', echo=True)
Base = declarative_base()

# Student Class takes name, attendance, & class_id parameters

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    attendance = Column(Boolean)
    class_id = Column(Integer)

    def __init__(self, name, attendance, class_id):
        self.name = name
        self.attendance = attendance
        self.class_id = class_id

# Teacher Class takes name & class_id parameters

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    class_id = Column(String)

    def __init__(self, name, class_id):
        self.name = name
        self.classid = class_id

Base.metadata.create_all(engine)
