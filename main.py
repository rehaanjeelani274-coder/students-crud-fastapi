from contextlib import asynccontextmanager
from datetime import date
from typing import Optional
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, model_validator

DB = 'students.db'

def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    with connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, date_of_birth TEXT NOT NULL, email TEXT, phone TEXT, course TEXT, address TEXT, enrollment_date TEXT)''')
    yield

app = FastAPI(title='Students Database CRUD API', lifespan=lifespan)

class StudentInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

    @model_validator(mode='after')
    def contact_required(self):
        if not self.email and not self.phone:
            raise ValueError('Provide an email or phone number')
        return self

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=20)
    course: Optional[str] = None
    address: Optional[str] = None
    enrollment_date: Optional[date] = None

def get_student_or_404(conn, student_id):
    row = conn.execute('SELECT * FROM students WHERE id=?', (student_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail='Student not found')
    return dict(row)

@app.get('/')
def home():
    return {'message': 'Students API is running. Visit /docs to test endpoints.'}

@app.post('/students', status_code=201)
def create_student(student: StudentInput):
    data = student.model_dump(mode='json')
    with connect() as conn:
        cursor = conn.execute('INSERT INTO students (name,date_of_birth,email,phone,course,address,enrollment_date) VALUES (:name,:date_of_birth,:email,:phone,:course,:address,:enrollment_date)', data)
        return get_student_or_404(conn, cursor.lastrowid)

@app.get('/students')
def list_students(name: Optional[str] = Query(default=None), course: Optional[str] = Query(default=None)):
    sql = 'SELECT * FROM students WHERE 1=1'
    params = []
    if name:
        sql += ' AND name LIKE ?'
        params.append('%' + name + '%')
    if course:
        sql += ' AND course LIKE ?'
        params.append('%' + course + '%')
    sql += ' ORDER BY id'
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]

@app.get('/students/{student_id}')
def read_student(student_id: int):
    with connect() as conn:
        return get_student_or_404(conn, student_id)

@app.patch('/students/{student_id}')
def update_student(student_id: int, changes: StudentUpdate):
    data = changes.model_dump(mode='json', exclude_unset=True)
    with connect() as conn:
        existing = get_student_or_404(conn, student_id)
        combined = {**existing, **data}
        StudentInput.model_validate({k: v for k, v in combined.items() if k != 'id'})
        if data:
            sql = 'UPDATE students SET ' + ', '.join(f'{key}=?' for key in data) + ' WHERE id=?'
            conn.execute(sql, [*data.values(), student_id])
        return get_student_or_404(conn, student_id)

@app.delete('/students/{student_id}')
def delete_student(student_id: int):
    with connect() as conn:
        get_student_or_404(conn, student_id)
        conn.execute('DELETE FROM students WHERE id=?', (student_id,))
    return {'message': 'Student deleted successfully', 'student_id': student_id}
