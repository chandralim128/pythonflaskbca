import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, ForeignKey, Float, Date

# DATABASE_URL = 'sqlite:///Stupla.db'
DATABASE_URL = 'mysql+mysqlconnector://root:ifapi3HmRFiGKYnwtYe0@containers-us-west-157.railway.app:5474/railway'
engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()

#Mendefinisikan table 'courses'
courses = Table('courses', metadata,
                 Column('course_id', Integer, primary_key = True),
                 Column('title', String),
                 Column('instructor', String),
                 Column('category', String),
                 Column('price', Float))

# Mendefinisikan table 'enrollments'
enrollments = Table('enrollments', metadata,
                 Column('enrollment_id', Integer, primary_key = True),
                 Column('user_id', Integer),
                 Column('course_id', Integer, ForeignKey('courses.course_id')),
                 Column('enrollment_date', Date),
                 Column('completion_date', Date))

# Membuat table
metadata.create_all(engine)

print("Database Stupla.db, table course, dan table  telah berhasil dibuat!")
